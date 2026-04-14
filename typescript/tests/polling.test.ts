import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { APIError, TimeoutError } from '../src/error.js';
import {
  isJobComplete,
  isJobFailed,
  pollJob,
  DEFAULT_POLL_INTERVAL,
  MAX_POLL_INTERVAL,
  DEFAULT_MAX_WAIT,
  POLL_BACKOFF_STEP,
} from '../src/polling.js';

// Helper to create a mock Response
function mockJsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const BASE_URL = 'https://api.1min.ai';
const API_KEY = 'test-api-key-12345678';
const JOB_ID = 'test-job-abc123';

// ---------------------------------------------------------------------------
// isJobComplete tests
// ---------------------------------------------------------------------------

describe('isJobComplete', () => {
  it('returns true for status: completed with output', () => {
    expect(isJobComplete({ status: 'completed', output: { url: 'http://example.com' } })).toBe(true);
  });

  it('returns true for status: done', () => {
    expect(isJobComplete({ status: 'done' })).toBe(true);
  });

  it('returns true for status: succeeded', () => {
    expect(isJobComplete({ status: 'succeeded' })).toBe(true);
  });

  it('returns true when result field is present and non-null', () => {
    expect(isJobComplete({ result: 'http://example.com/image.png' })).toBe(true);
  });

  it('returns true when output field is present and non-null', () => {
    expect(isJobComplete({ output: { url: 'http://example.com' } })).toBe(true);
  });

  it('returns false for status: processing', () => {
    expect(isJobComplete({ status: 'processing' })).toBe(false);
  });

  it('returns false for empty object', () => {
    expect(isJobComplete({})).toBe(false);
  });

  it('returns false when result is explicitly null', () => {
    expect(isJobComplete({ result: null, status: 'processing' })).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// isJobFailed tests
// ---------------------------------------------------------------------------

describe('isJobFailed', () => {
  it('returns true for status: failed', () => {
    expect(isJobFailed({ status: 'failed' })).toBe(true);
  });

  it('returns true for status: error', () => {
    expect(isJobFailed({ status: 'error' })).toBe(true);
  });

  it('returns true for status: cancelled', () => {
    expect(isJobFailed({ status: 'cancelled' })).toBe(true);
  });

  it('returns false for status: processing', () => {
    expect(isJobFailed({ status: 'processing' })).toBe(false);
  });

  it('returns false for empty object', () => {
    expect(isJobFailed({})).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// pollJob tests
// ---------------------------------------------------------------------------

describe('pollJob', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('returns completed result after two polls (processing then completed)', async () => {
    let callCount = 0;
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => {
      callCount++;
      if (callCount === 1) {
        return Promise.resolve(mockJsonResponse({ status: 'processing' }));
      }
      return Promise.resolve(mockJsonResponse({ status: 'completed', output: { url: 'http://img.com/1.png' } }));
    }));

    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 100, maxWait: 10_000 });
    // Advance timers to get past the sleep
    await vi.runAllTimersAsync();
    const result = await promise;
    expect(result.status).toBe('completed');
    expect((result.output as { url: string }).url).toBe('http://img.com/1.png');
  });

  it('returns result immediately when first poll shows completed', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'completed', output: {} }))
    ));

    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 100, maxWait: 10_000 });
    await vi.runAllTimersAsync();
    const result = await promise;
    expect(result.status).toBe('completed');
  });

  it('throws TimeoutError when maxWait is exceeded', async () => {
    // Use real timers: small interval + maxWait forces actual timeout
    vi.useRealTimers();
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'processing' }))
    ));

    await expect(
      pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 10, maxWait: 50 })
    ).rejects.toThrow(TimeoutError);
  });

  it('TimeoutError message includes jobId', async () => {
    vi.useRealTimers();
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'processing' }))
    ));

    await expect(
      pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 10, maxWait: 50 })
    ).rejects.toThrow(JOB_ID);
  });

  it('throws APIError immediately when job status is failed', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'failed', error: 'generation failed' }))
    ));

    // Attach rejection handler before runAllTimersAsync to avoid unhandled rejection
    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 100, maxWait: 10_000 });
    const caught = promise.catch((e) => e);
    await vi.runAllTimersAsync();
    const err = await caught;
    expect(err).toBeInstanceOf(APIError);
  });

  it('APIError message from failed job includes error text', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'failed', error: 'quota exceeded' }))
    ));

    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 100, maxWait: 10_000 });
    const caught = promise.catch((e) => e);
    await vi.runAllTimersAsync();
    const err = await caught;
    expect(err).toBeInstanceOf(APIError);
    expect(String(err)).toContain('quota exceeded');
  });

  it('throws APIError immediately for status: error (no extra polls)', async () => {
    const mockFetch = vi.fn().mockImplementation(() =>
      Promise.resolve(mockJsonResponse({ status: 'error', message: 'internal error' }))
    );
    vi.stubGlobal('fetch', mockFetch);

    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, { interval: 100, maxWait: 10_000 });
    const caught = promise.catch((e) => e);
    await vi.runAllTimersAsync();
    const err = await caught;
    expect(err).toBeInstanceOf(APIError);
    // Fetch should only be called once — fail fast
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('increases interval linearly from start toward MAX_POLL_INTERVAL', async () => {
    let callCount = 0;
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => {
      callCount++;
      if (callCount < 4) {
        return Promise.resolve(mockJsonResponse({ status: 'processing' }));
      }
      return Promise.resolve(mockJsonResponse({ status: 'completed', output: {} }));
    }));

    const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');
    const promise = pollJob(BASE_URL, API_KEY, JOB_ID, {
      interval: DEFAULT_POLL_INTERVAL,
      maxWait: DEFAULT_MAX_WAIT,
    });
    await vi.runAllTimersAsync();
    await promise;

    // Filter setTimeout calls to only the sleep intervals (< 30_000ms, which is the AbortController timeout)
    const sleepCalls = setTimeoutSpy.mock.calls
      .filter(call => typeof call[1] === 'number' && (call[1] as number) < 30_000);
    expect(sleepCalls.length).toBeGreaterThanOrEqual(2);
    // First sleep should be at DEFAULT_POLL_INTERVAL (3000ms)
    const firstSleep = sleepCalls[0]?.[1] as number;
    expect(firstSleep).toBe(DEFAULT_POLL_INTERVAL);
    // Second sleep should be at DEFAULT_POLL_INTERVAL + POLL_BACKOFF_STEP (4000ms)
    const secondSleep = sleepCalls[1]?.[1] as number;
    expect(secondSleep).toBe(DEFAULT_POLL_INTERVAL + POLL_BACKOFF_STEP);
  });
});

// ---------------------------------------------------------------------------
// Constant value tests
// ---------------------------------------------------------------------------

describe('polling constants', () => {
  it('DEFAULT_POLL_INTERVAL is 3000ms', () => {
    expect(DEFAULT_POLL_INTERVAL).toBe(3_000);
  });

  it('MAX_POLL_INTERVAL is 10000ms', () => {
    expect(MAX_POLL_INTERVAL).toBe(10_000);
  });

  it('DEFAULT_MAX_WAIT is 300000ms (5 minutes)', () => {
    expect(DEFAULT_MAX_WAIT).toBe(300_000);
  });

  it('POLL_BACKOFF_STEP is 1000ms', () => {
    expect(POLL_BACKOFF_STEP).toBe(1_000);
  });
});
