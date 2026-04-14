/**
 * Auto-polling for long-running jobs in the 1min.ai SDK.
 *
 * Provides an async poll loop for jobs that complete asynchronously —
 * e.g. Midjourney image generation, video creation. Takes a job ID,
 * polls GET /api/jobs/{id} at increasing intervals until a completion
 * signal is detected, then returns the final result object.
 *
 * Completion detection handles multiple response shapes:
 *   - `{ status: "completed", output: { ... } }` — status-based completion
 *   - `{ result: "http://..." }` — result field present and non-null
 *   - `{ output: { ... } }` — output field present and non-null
 *
 * @example
 * ```typescript
 * import { pollJob } from '@onemin/sdk';
 *
 * const result = await pollJob(
 *   'https://api.1min.ai',
 *   process.env.ONEMIN_API_KEY!,
 *   jobId,
 * );
 * console.log(result.output);
 * ```
 */

import { APIError, TimeoutError } from './error.js';
import { API_KEY_HEADER } from './constants.js';

// ---------------------------------------------------------------------------
// Polling configuration defaults (in milliseconds)
// ---------------------------------------------------------------------------

/** Starting poll interval in milliseconds (3 seconds). */
export const DEFAULT_POLL_INTERVAL = 3_000;

/** Maximum poll interval in milliseconds (10 seconds). Linear backoff cap. */
export const MAX_POLL_INTERVAL = 10_000;

/** Milliseconds added to the interval after each poll cycle (linear backoff). */
export const POLL_BACKOFF_STEP = 1_000;

/** Maximum total wait time in milliseconds (5 minutes). Matches video timeout. */
export const DEFAULT_MAX_WAIT = 300_000;

// ---------------------------------------------------------------------------
// Completion / failure status sets
// ---------------------------------------------------------------------------

const COMPLETE_STATUSES = new Set(['completed', 'complete', 'done', 'succeeded', 'success']);
const FAILED_STATUSES = new Set(['failed', 'error', 'cancelled', 'canceled']);

// ---------------------------------------------------------------------------
// Detection helpers
// ---------------------------------------------------------------------------

/**
 * Check if a job polling response indicates completion.
 *
 * Handles three patterns observed in 1min.ai job responses:
 * 1. `status` field set to a completion value (e.g. "completed", "done")
 * 2. `result` field is present and non-null
 * 3. `output` field is present and non-null
 *
 * @param data - Parsed JSON response from GET /api/jobs/{id}.
 * @returns True if the job appears to be complete, false otherwise.
 */
export function isJobComplete(data: Record<string, unknown>): boolean {
  const status = String(data.status ?? '').toLowerCase();
  if (COMPLETE_STATUSES.has(status)) return true;
  if (data.result != null) return true;
  if (data.output != null) return true;
  return false;
}

/**
 * Check if a job polling response indicates a failure.
 *
 * @param data - Parsed JSON response from GET /api/jobs/{id}.
 * @returns True if the job has failed (no more polling needed), false otherwise.
 */
export function isJobFailed(data: Record<string, unknown>): boolean {
  const status = String(data.status ?? '').toLowerCase();
  return FAILED_STATUSES.has(status);
}

// ---------------------------------------------------------------------------
// Sleep helper
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Async polling
// ---------------------------------------------------------------------------

/**
 * Async: poll GET /api/jobs/{jobId} until the job completes or times out.
 *
 * Polls at `interval` milliseconds initially, increasing linearly by
 * `POLL_BACKOFF_STEP` each cycle up to `MAX_POLL_INTERVAL`.
 *
 * @param baseUrl - API base URL (e.g. "https://api.1min.ai").
 * @param apiKey - 1min.ai API key for the API-KEY header.
 * @param jobId - Job identifier returned by the job creation endpoint.
 * @param options - Optional overrides for interval and maxWait.
 * @returns The final job response object when the job completes.
 * @throws {APIError} If the job status indicates failure (fail fast).
 * @throws {TimeoutError} If maxWait is exceeded without a completion signal.
 */
export async function pollJob(
  baseUrl: string,
  apiKey: string,
  jobId: string,
  options?: {
    /** Starting poll interval in milliseconds (default: {@link DEFAULT_POLL_INTERVAL}). */
    interval?: number;
    /** Maximum total wait time in milliseconds (default: {@link DEFAULT_MAX_WAIT}). */
    maxWait?: number;
  },
): Promise<Record<string, unknown>> {
  const interval = options?.interval ?? DEFAULT_POLL_INTERVAL;
  const maxWait = options?.maxWait ?? DEFAULT_MAX_WAIT;
  const deadline = Date.now() + maxWait;
  let currentInterval = interval;
  let lastData: Record<string, unknown> = {};

  while (Date.now() < deadline) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 30_000);

    try {
      const response = await fetch(`${baseUrl}/api/jobs/${jobId}`, {
        method: 'GET',
        headers: { [API_KEY_HEADER]: apiKey },
        signal: ctrl.signal,
      });

      if (!response.ok) {
        const body = await response.text().catch(() => `HTTP ${response.status}`);
        throw new APIError(body, response.status);
      }

      lastData = (await response.json()) as Record<string, unknown>;
    } finally {
      clearTimeout(timer);
    }

    if (isJobFailed(lastData)) {
      const errorMsg = String(lastData.error ?? lastData.message ?? JSON.stringify(lastData));
      throw new APIError(`Job ${jobId} failed: ${errorMsg}`, 0);
    }

    if (isJobComplete(lastData)) {
      return lastData;
    }

    await sleep(currentInterval);
    currentInterval = Math.min(currentInterval + POLL_BACKOFF_STEP, MAX_POLL_INTERVAL);
  }

  throw new TimeoutError(
    `Job ${jobId} did not complete within ${maxWait}ms. Last response: ${JSON.stringify(lastData)}`,
  );
}
