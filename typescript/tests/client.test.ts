import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  AuthenticationError,
  RateLimitError,
  NotFoundError,
  BadRequestError,
  InternalServerError,
  APIError,
  ConnectionError,
  TimeoutError,
  UnsupportedModelError,
} from '../src/error.js';
import { OneMinClient } from '../src/client.js';

// Helper to create a mock Response
function mockResponse(body: unknown, status: number, headers: Record<string, string> = {}): Response {
  const responseBody = typeof body === 'string' ? body : JSON.stringify(body);
  return new Response(responseBody, { status, headers: { 'Content-Type': 'application/json', ...headers } });
}

describe('OneMinClient - instantiation', () => {
  beforeEach(() => {
    delete process.env.ONEMIN_API_KEY;
  });

  afterEach(() => {
    delete process.env.ONEMIN_API_KEY;
    vi.restoreAllMocks();
  });

  it('creates client without error when apiKey is provided', () => {
    expect(() => new OneMinClient({ apiKey: 'test-key-12345678' })).not.toThrow();
  });

  it('creates client with ONEMIN_API_KEY env var when no apiKey in options', () => {
    process.env.ONEMIN_API_KEY = 'test-key-from-env';
    expect(() => new OneMinClient()).not.toThrow();
  });

  it('throws AuthenticationError when no apiKey and no env var', () => {
    expect(() => new OneMinClient()).toThrow(AuthenticationError);
  });

  it('constructor apiKey takes precedence over env var', () => {
    process.env.ONEMIN_API_KEY = 'env-key-xxxx';
    const client = new OneMinClient({ apiKey: 'constructor-key-yyyy' });
    // The client should use the constructor key (not the env var)
    // We verify by checking toString() shows masked constructor key
    expect(client.toString()).toContain('cons');
  });
});

describe('OneMinClient - toString() key masking', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('does not contain the full API key in toString()', () => {
    const apiKey = 'secret-api-key-very-long-12345678';
    const client = new OneMinClient({ apiKey });
    const str = client.toString();
    expect(str).not.toContain(apiKey);
  });

  it('masks the API key with first 4 and last 4 chars', () => {
    const apiKey = 'abcd1234efgh5678';
    const client = new OneMinClient({ apiKey });
    const str = client.toString();
    expect(str).toContain('abcd');
    expect(str).toContain('5678');
    expect(str).not.toContain('1234efgh');
  });

  it('masks short keys as ***', () => {
    const apiKey = 'short';
    const client = new OneMinClient({ apiKey });
    const str = client.toString();
    expect(str).toContain('***');
    expect(str).not.toContain('short');
  });
});

describe('OneMinClient - HTTP error mapping', () => {
  let client: OneMinClient;

  beforeEach(() => {
    client = new OneMinClient({ apiKey: 'test-api-key-12345678' });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('throws AuthenticationError for 401 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Unauthorized', 401)));
    await expect(client._request('GET', '/test')).rejects.toThrow(AuthenticationError);
    await expect(client._request('GET', '/test')).rejects.toMatchObject({ statusCode: 401 });
  });

  it('throws RateLimitError for 429 response', async () => {
    // 429 is retryable, mock multiple calls all returning 429
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Rate limited', 429)));
    await expect(client._request('GET', '/test')).rejects.toThrow(RateLimitError);
    await expect(client._request('GET', '/test')).rejects.toMatchObject({ statusCode: 429 });
  });

  it('throws NotFoundError for 404 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Not found', 404)));
    await expect(client._request('GET', '/test')).rejects.toThrow(NotFoundError);
    await expect(client._request('GET', '/test')).rejects.toMatchObject({ statusCode: 404 });
  });

  it('throws BadRequestError for 400 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Bad request', 400)));
    await expect(client._request('GET', '/test')).rejects.toThrow(BadRequestError);
    await expect(client._request('GET', '/test')).rejects.toMatchObject({ statusCode: 400 });
  });

  it('promotes UNSUPPORTED_MODEL 400 to UnsupportedModelError with suggestions', async () => {
    const body = JSON.stringify({
      errorCode: 'UNSUPPORTED_MODEL',
      message: 'Model totally-not-a-model is not supported',
    });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse(body, 400)));
    const err = await client._request('GET', '/test').catch((e) => e);
    expect(err).toBeInstanceOf(UnsupportedModelError);
    expect(err).toBeInstanceOf(BadRequestError);
    expect(err.requestedModel).toBe('totally-not-a-model');
    expect(err.suggestions.length).toBeGreaterThan(0);
    expect(err.message).toContain('Try one of:');
  });

  it('keeps non-UNSUPPORTED_MODEL 400 as plain BadRequestError', async () => {
    const body = JSON.stringify({
      errorCode: 'REQUEST_BODY_VALIDATION_FAILED',
      message: 'bad payload',
    });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse(body, 400)));
    const err = await client._request('GET', '/test').catch((e) => e);
    expect(err).toBeInstanceOf(BadRequestError);
    expect(err).not.toBeInstanceOf(UnsupportedModelError);
  });

  it('throws InternalServerError for 500 response', async () => {
    // 500 is retryable, mock multiple calls all returning 500
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Internal server error', 500)));
    await expect(client._request('GET', '/test')).rejects.toThrow(InternalServerError);
    await expect(client._request('GET', '/test')).rejects.toMatchObject({ statusCode: 500 });
  });
});

describe('OneMinClient - retry behavior', () => {
  let client: OneMinClient;

  beforeEach(() => {
    // maxRetries=1 and baseDelay=0 to keep tests fast
    client = new OneMinClient({ apiKey: 'test-api-key-12345678', maxRetries: 1, baseDelay: 0 });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('retries 503 response (2 total calls for maxRetries=1)', async () => {
    const mockFetch = vi.fn().mockResolvedValue(mockResponse('Service unavailable', 503));
    vi.stubGlobal('fetch', mockFetch);
    await expect(client._request('GET', '/test')).rejects.toThrow();
    // maxRetries=1 means: 1 initial attempt + 1 retry = 2 total calls
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('does NOT retry 401 response (exactly 1 fetch call)', async () => {
    const mockFetch = vi.fn().mockResolvedValue(mockResponse('Unauthorized', 401));
    vi.stubGlobal('fetch', mockFetch);
    await expect(client._request('GET', '/test')).rejects.toThrow(AuthenticationError);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('does NOT retry 403 response (exactly 1 fetch call)', async () => {
    const mockFetch = vi.fn().mockResolvedValue(mockResponse('Forbidden', 403));
    vi.stubGlobal('fetch', mockFetch);
    await expect(client._request('GET', '/test')).rejects.toThrow(APIError);
    // 403 is NOT retried per D-11
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('does NOT retry 404 response (exactly 1 fetch call)', async () => {
    const mockFetch = vi.fn().mockResolvedValue(mockResponse('Not found', 404));
    vi.stubGlobal('fetch', mockFetch);
    await expect(client._request('GET', '/test')).rejects.toThrow(NotFoundError);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('does NOT retry 400 response (exactly 1 fetch call)', async () => {
    const mockFetch = vi.fn().mockResolvedValue(mockResponse('Bad request', 400));
    vi.stubGlobal('fetch', mockFetch);
    await expect(client._request('GET', '/test')).rejects.toThrow(BadRequestError);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });
});

describe('OneMinClient - timeout and connection errors', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('throws TimeoutError when AbortController timeout fires', async () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', timeout: 50, maxRetries: 0 });
    // fetch never resolves — simulates hanging request
    vi.stubGlobal('fetch', vi.fn().mockImplementation((_url: string, options: RequestInit) => {
      return new Promise<Response>((_resolve, reject) => {
        if (options.signal) {
          options.signal.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'));
          });
        }
        // Never resolve
      });
    }));
    await expect(client._request('GET', '/test')).rejects.toThrow(TimeoutError);
  });

  it('throws ConnectionError on fetch network error', async () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', maxRetries: 0 });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('fetch failed')));
    await expect(client._request('GET', '/test')).rejects.toThrow(ConnectionError);
  });
});

describe('OneMinClient - timeout memory leak prevention', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls clearTimeout after a successful request', async () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', maxRetries: 0 });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse({ result: 'ok' }, 200)));
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
    await client._request('GET', '/test');
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('calls clearTimeout even when request throws an error', async () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', maxRetries: 0 });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse('Unauthorized', 401)));
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
    await expect(client._request('GET', '/test')).rejects.toThrow();
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });
});

describe('OneMinClient - configuration', () => {
  it('maxRetries is configurable via constructor options', () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', maxRetries: 5 });
    expect(client.maxRetries).toBe(5);
  });

  it('timeout is configurable via constructor options', () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', timeout: 60000 });
    expect(client.timeout).toBe(60000);
  });

  it('baseDelay is configurable via constructor options', () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', baseDelay: 1000 });
    expect(client.baseDelay).toBe(1000);
  });

  it('request accepts optional timeout parameter that overrides default', async () => {
    const client = new OneMinClient({ apiKey: 'test-api-key-12345678', timeout: 30000, maxRetries: 0 });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockResponse({ result: 'ok' }, 200)));
    // Should not throw — custom timeout parameter is accepted
    await expect(client._request('GET', '/test', undefined, { timeout: 90000 })).resolves.toBeDefined();
  });
});
