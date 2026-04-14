/**
 * SSE streaming helpers for the 1min.ai SDK.
 *
 * Provides an async generator that consumes Server-Sent Events from the
 * 1min.ai streaming endpoint (/api/features?isStreaming=true) and yields
 * token strings, handling:
 *
 * - Partial JSON across SSE chunk boundaries (buffered accumulation)
 * - [DONE] sentinel termination
 * - Empty data lines (SSE keepalives)
 * - Non-data SSE lines (comments, event:, id:, retry:)
 * - Buffer overflow protection (1MB cap to prevent OOM on malformed streams)
 *
 * Usage:
 * ```typescript
 * import { streamSSE } from '@onemin/sdk';
 *
 * const response = await fetch(url, { method: 'POST', ... });
 * for await (const token of streamSSE(response)) {
 *   process.stdout.write(token);
 * }
 * ```
 */

import { APIError, ConnectionError } from './error.js';

/** Maximum allowed SSE buffer size (1 MB). Prevents OOM on malformed streams. */
export const MAX_BUFFER_SIZE = 1_048_576;

/**
 * Extract a token string from a parsed SSE JSON payload.
 *
 * Tries multiple known paths in order of priority:
 * 1. OpenAI-style: choices[0].delta.content
 * 2. Simple format: obj.data
 * 3. Fallback: JSON.stringify(obj)
 *
 * @param obj - Parsed JSON object from an SSE data line.
 * @returns Extracted token string. May be empty if the delta had no content.
 */
export function extractToken(obj: Record<string, unknown>): string {
  // Try OpenAI-style: choices[0].delta.content
  const choices = obj?.choices;
  if (Array.isArray(choices) && choices.length > 0) {
    const delta = (choices[0] as Record<string, unknown>)?.delta as Record<string, unknown> | undefined;
    const content = delta?.content;
    if (typeof content === 'string') {
      return content; // May be empty — caller decides whether to yield
    }
    return '';
  }

  // Try simple format: obj.data
  const data = obj?.data;
  if (data !== undefined && data !== null) {
    return String(data);
  }

  // Fallback: stringify the whole object
  return JSON.stringify(obj);
}

/**
 * Async generator that reads SSE events from a fetch Response and yields tokens.
 *
 * The caller is responsible for making the fetch request with `?isStreaming=true`.
 * This function handles the SSE parsing, including:
 * - Line-by-line SSE parsing from the response body stream
 * - Partial JSON reassembly across chunk boundaries
 * - [DONE] sentinel detection
 * - Buffer overflow protection
 *
 * @param response - The fetch Response from the streaming endpoint.
 * @yields Individual token strings extracted from SSE data events.
 * @throws {APIError} If the response status is not ok.
 * @throws {ConnectionError} If the response body is null.
 * @throws {Error} If the buffer exceeds MAX_BUFFER_SIZE (malformed stream).
 */
export async function* streamSSE(
  response: Response,
): AsyncGenerator<string, void, undefined> {
  // Check response status
  if (!response.ok) {
    let body: string;
    try {
      body = await response.text();
    } catch {
      body = `HTTP ${response.status} error`;
    }
    throw new APIError(body, response.status);
  }

  // Check that body is available
  if (!response.body) {
    throw new ConnectionError('Response body is null — cannot stream SSE');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  // Line buffer: accumulates text until we can extract complete SSE lines
  let lineBuffer = '';

  // JSON buffer: accumulates partial JSON data across SSE chunk boundaries
  let jsonBuffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      // Decode chunk and append to line buffer
      lineBuffer += decoder.decode(value, { stream: true });

      // Guard against memory exhaustion
      if (lineBuffer.length > MAX_BUFFER_SIZE) {
        throw new Error('SSE buffer overflow: exceeded 1MB');
      }

      // Split on newlines to process complete lines
      // Keep the last (potentially incomplete) segment as the new buffer
      const lines = lineBuffer.split('\n');
      lineBuffer = lines.pop() ?? '';

      for (const line of lines) {
        // Skip non-data SSE lines (comments, event:, id:, retry:, empty lines)
        if (!line.startsWith('data: ')) {
          continue;
        }

        // Extract data portion after "data: " prefix
        const data = line.slice(6);

        // Empty data string — skip (SSE keepalive)
        if (!data) {
          continue;
        }

        // [DONE] sentinel — end the stream
        if (data === '[DONE]') {
          return;
        }

        // Accumulate for JSON reassembly
        jsonBuffer += data;

        // Guard against memory exhaustion from accumulated json buffer
        if (jsonBuffer.length > MAX_BUFFER_SIZE) {
          throw new Error('SSE buffer overflow: exceeded 1MB');
        }

        // Try to parse accumulated JSON
        try {
          const obj = JSON.parse(jsonBuffer) as Record<string, unknown>;
          jsonBuffer = ''; // Reset on success
          const token = extractToken(obj);
          if (token) {
            yield token;
          }
        } catch {
          // Incomplete JSON — continue accumulating across chunk boundaries
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
