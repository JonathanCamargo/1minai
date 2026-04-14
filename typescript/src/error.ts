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

export class ConnectionError extends OneMinError {}
export class TimeoutError extends ConnectionError {}
