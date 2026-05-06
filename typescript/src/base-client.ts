import {
  AuthenticationError,
  APIError,
  RateLimitError,
  NotFoundError,
  BadRequestError,
  InternalServerError,
  ConnectionError,
  TimeoutError,
  UnsupportedModelError,
} from './error.js';
import {
  BASE_URL,
  DEFAULT_TIMEOUT,
  DEFAULT_MAX_RETRIES,
  DEFAULT_BASE_DELAY,
  RETRYABLE_STATUS_CODES,
  API_KEY_HEADER,
} from './constants.js';
import { MODEL_CATALOGUE } from './models-data.js';

const UNSUPPORTED_MODEL_NAME_RE = /Model\s+(\S+?)\s+is not supported/i;
const MAX_SUGGESTIONS = 6;

function domainForModel(model: string): string | null {
  for (const [domain, entries] of Object.entries(MODEL_CATALOGUE)) {
    for (const entry of entries) {
      if (entry.id === model || entry.constant === model) return domain;
    }
  }
  return null;
}

function suggestModels(requested: string | null): string[] {
  const domain = (requested ? domainForModel(requested) : null) ?? 'text';
  return (MODEL_CATALOGUE[domain] ?? []).slice(0, MAX_SUGGESTIONS).map((m) => m.id);
}

function maybeUnsupportedModelError(
  body: string,
  status: number,
  requestId: string | undefined,
): UnsupportedModelError | null {
  let payload: unknown;
  try {
    payload = JSON.parse(body);
  } catch {
    return null;
  }
  if (!payload || typeof payload !== 'object') return null;
  const obj = payload as Record<string, unknown>;
  if (obj.errorCode !== 'UNSUPPORTED_MODEL') return null;
  const apiMessage = typeof obj.message === 'string' ? obj.message : '';
  const match = apiMessage.match(UNSUPPORTED_MODEL_NAME_RE);
  const requested = match ? match[1] : null;
  const suggestions = suggestModels(requested);
  const suggestionText = suggestions.length
    ? ` Try one of: ${suggestions.join(', ')}.`
    : '';
  const msg =
    `${apiMessage} Edit data/models.json and run scripts/sync_models.py if you've added a new model.${suggestionText}`;
  return new UnsupportedModelError(msg, status, requestId, requested, suggestions);
}

export interface ClientOptions {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;     // milliseconds, default 30000
  maxRetries?: number;  // default 2
  baseDelay?: number;   // milliseconds, default 500
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class BaseOneMinClient {
  protected readonly apiKey: string;
  readonly baseUrl: string;
  readonly timeout: number;
  readonly maxRetries: number;
  readonly baseDelay: number;

  constructor(options: ClientOptions = {}) {
    const key = options.apiKey ?? process.env.ONEMIN_API_KEY;
    if (!key) {
      throw new AuthenticationError(
        'No API key provided. Either pass apiKey to OneMinClient() or set the ONEMIN_API_KEY environment variable.',
        401,
      );
    }
    this.apiKey = key;
    this.baseUrl = options.baseUrl ?? BASE_URL;
    this.timeout = options.timeout ?? DEFAULT_TIMEOUT;
    this.maxRetries = options.maxRetries ?? DEFAULT_MAX_RETRIES;
    this.baseDelay = options.baseDelay ?? DEFAULT_BASE_DELAY;
  }

  toString(): string {
    const key = this.apiKey;
    const masked = key.length > 8
      ? `${key.slice(0, 4)}...${key.slice(-4)}`
      : '***';
    return `OneMinClient(apiKey='${masked}', baseUrl='${this.baseUrl}')`;
  }

  protected isRetryable(statusCode: number): boolean {
    return RETRYABLE_STATUS_CODES.has(statusCode);
  }

  protected getRetryDelay(
    statusCode: number | null,
    headers: Headers | null,
    attempt: number,
  ): number {
    // Honor Retry-After header for 429 responses
    if (statusCode === 429 && headers) {
      const retryAfter = headers.get('Retry-After');
      if (retryAfter) {
        const parsed = parseFloat(retryAfter);
        if (!isNaN(parsed) && parsed > 0) {
          // If Retry-After is in seconds (common), convert to ms
          // Values > 1000 are assumed to already be ms; values <= 1000 are seconds
          return parsed <= 1000 ? parsed * 1000 : parsed;
        }
      }
    }
    const delay = this.baseDelay * Math.pow(2, attempt);
    const jitter = delay * (0.3 + Math.random() * 0.2);
    return delay + jitter;
  }

  protected async handleResponse<T>(response: Response): Promise<T> {
    const requestId = response.headers.get('x-request-id') ?? undefined;
    const status = response.status;

    if (response.ok) {
      return response.json() as Promise<T>;
    }

    let body: string;
    try {
      body = await response.text();
    } catch {
      body = `HTTP ${status} error`;
    }

    switch (status) {
      case 401:
        throw new AuthenticationError(body, 401, requestId);
      case 403:
        throw new APIError(body, 403, requestId);
      case 429:
        throw new RateLimitError(body, 429, requestId);
      case 404:
        throw new NotFoundError(body, 404, requestId);
      case 400: {
        const unsupported = maybeUnsupportedModelError(body, 400, requestId);
        if (unsupported) throw unsupported;
        throw new BadRequestError(body, 400, requestId);
      }
      default:
        if (status >= 500) {
          throw new InternalServerError(body, status, requestId);
        }
        throw new APIError(body, status, requestId);
    }
  }

  protected async request<T>(
    method: string,
    path: string,
    body?: unknown,
    options?: { timeout?: number },
  ): Promise<T> {
    const url = `${this.baseUrl}/${path.replace(/^\//, '')}`;
    const effectiveTimeout = options?.timeout ?? this.timeout;

    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      if (attempt > 0 && lastError !== undefined) {
        // Determine retry-after delay based on previous response status (if available)
        const statusCode = lastError instanceof APIError ? lastError.statusCode : null;
        const delay = this.getRetryDelay(statusCode, null, attempt - 1);
        if (delay > 0) {
          await sleep(delay);
        }
      }

      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), effectiveTimeout);

      try {
        const fetchOptions: RequestInit = {
          method,
          headers: {
            [API_KEY_HEADER]: this.apiKey,
            'Content-Type': 'application/json',
          },
          signal: ctrl.signal,
        };

        if (body !== undefined) {
          (fetchOptions as RequestInit & { body: string }).body = JSON.stringify(body);
        }

        let response: Response;
        try {
          response = await fetch(url, fetchOptions);
        } catch (err) {
          // Handle abort (timeout) vs network error
          if (err instanceof DOMException && err.name === 'AbortError') {
            throw new TimeoutError('Request timed out');
          }
          if (err instanceof TypeError) {
            // Network error — retry if possible
            if (attempt < this.maxRetries) {
              lastError = new ConnectionError((err as TypeError).message);
              continue;
            }
            throw new ConnectionError((err as TypeError).message);
          }
          throw err;
        }

        if (!response.ok && this.isRetryable(response.status) && attempt < this.maxRetries) {
          // Clone response to read it later
          lastError = new APIError(
            `Retryable error: ${response.status}`,
            response.status,
          );
          continue;
        }

        return await this.handleResponse<T>(response);
      } finally {
        clearTimeout(timer);
      }
    }

    // Should never reach here but TypeScript needs this
    throw lastError ?? new ConnectionError('Request failed after retries');
  }

  public _request<T>(
    method: string,
    path: string,
    body?: unknown,
    options?: { timeout?: number },
  ): Promise<T> {
    return this.request<T>(method, path, body, options);
  }
}
