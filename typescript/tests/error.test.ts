import { describe, it, expect } from 'vitest';
import {
  OneMinError,
  APIError,
  AuthenticationError,
  RateLimitError,
  NotFoundError,
  BadRequestError,
  InternalServerError,
  ConnectionError,
  TimeoutError,
} from '../src/error.js';

describe('OneMinError', () => {
  it('is an instance of Error', () => {
    const err = new OneMinError('test error');
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new OneMinError('test');
    expect(err.name).toBe('OneMinError');
  });

  it('has the correct message', () => {
    const err = new OneMinError('something went wrong');
    expect(err.message).toBe('something went wrong');
  });
});

describe('APIError', () => {
  it('is an instance of OneMinError and Error', () => {
    const err = new APIError('bad request', 400);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
    expect(err).toBeInstanceOf(Error);
  });

  it('has statusCode property', () => {
    const err = new APIError('not found', 404);
    expect(err.statusCode).toBe(404);
  });

  it('has requestId property when provided', () => {
    const err = new APIError('error', 500, 'req-123');
    expect(err.requestId).toBe('req-123');
  });

  it('requestId is undefined when not provided', () => {
    const err = new APIError('error', 500);
    expect(err.requestId).toBeUndefined();
  });

  it('formats message as "HTTP {code}: {msg}"', () => {
    const err = new APIError('Unauthorized', 401);
    expect(err.message).toBe('HTTP 401: Unauthorized');
  });

  it('has the correct name', () => {
    const err = new APIError('error', 400);
    expect(err.name).toBe('APIError');
  });
});

describe('AuthenticationError', () => {
  it('is an instance of APIError and OneMinError', () => {
    const err = new AuthenticationError('invalid key', 401);
    expect(err).toBeInstanceOf(AuthenticationError);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new AuthenticationError('invalid key', 401);
    expect(err.name).toBe('AuthenticationError');
  });

  it('has statusCode 401', () => {
    const err = new AuthenticationError('invalid key', 401);
    expect(err.statusCode).toBe(401);
  });
});

describe('RateLimitError', () => {
  it('is an instance of APIError and OneMinError', () => {
    const err = new RateLimitError('rate limited', 429);
    expect(err).toBeInstanceOf(RateLimitError);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new RateLimitError('rate limited', 429);
    expect(err.name).toBe('RateLimitError');
  });
});

describe('NotFoundError', () => {
  it('is an instance of APIError and OneMinError', () => {
    const err = new NotFoundError('not found', 404);
    expect(err).toBeInstanceOf(NotFoundError);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new NotFoundError('not found', 404);
    expect(err.name).toBe('NotFoundError');
  });
});

describe('BadRequestError', () => {
  it('is an instance of APIError and OneMinError', () => {
    const err = new BadRequestError('bad input', 400);
    expect(err).toBeInstanceOf(BadRequestError);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new BadRequestError('bad input', 400);
    expect(err.name).toBe('BadRequestError');
  });
});

describe('InternalServerError', () => {
  it('is an instance of APIError and OneMinError', () => {
    const err = new InternalServerError('server error', 500);
    expect(err).toBeInstanceOf(InternalServerError);
    expect(err).toBeInstanceOf(APIError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('has the correct name', () => {
    const err = new InternalServerError('server error', 500);
    expect(err.name).toBe('InternalServerError');
  });
});

describe('ConnectionError', () => {
  it('is an instance of OneMinError but NOT APIError', () => {
    const err = new ConnectionError('connection failed');
    expect(err).toBeInstanceOf(ConnectionError);
    expect(err).toBeInstanceOf(OneMinError);
    expect(err).not.toBeInstanceOf(APIError);
  });

  it('has the correct name', () => {
    const err = new ConnectionError('connection failed');
    expect(err.name).toBe('ConnectionError');
  });
});

describe('TimeoutError', () => {
  it('is an instance of ConnectionError', () => {
    const err = new TimeoutError('timed out');
    expect(err).toBeInstanceOf(TimeoutError);
    expect(err).toBeInstanceOf(ConnectionError);
    expect(err).toBeInstanceOf(OneMinError);
  });

  it('is NOT an instance of APIError', () => {
    const err = new TimeoutError('timed out');
    expect(err).not.toBeInstanceOf(APIError);
  });

  it('has the correct name', () => {
    const err = new TimeoutError('timed out');
    expect(err.name).toBe('TimeoutError');
  });
});
