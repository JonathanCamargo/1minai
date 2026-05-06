export class OneMinError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class APIError extends OneMinError {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly requestId?: string,
  ) {
    super(`HTTP ${statusCode}: ${message}`);
  }
}

export class AuthenticationError extends APIError {}
export class RateLimitError extends APIError {}
export class NotFoundError extends APIError {}
export class BadRequestError extends APIError {}
export class InternalServerError extends APIError {}

/**
 * Raised when the API rejects a model id with errorCode `UNSUPPORTED_MODEL`.
 *
 * The error message includes a short list of currently-known alternatives
 * pulled from the generated catalogue (`data/models.json`).
 */
export class UnsupportedModelError extends BadRequestError {
  constructor(
    message: string,
    statusCode: number,
    requestId: string | undefined,
    public readonly requestedModel: string | null,
    public readonly suggestions: string[],
  ) {
    super(message, statusCode, requestId);
  }
}

export class ConnectionError extends OneMinError {}
export class TimeoutError extends ConnectionError {}
