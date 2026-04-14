/**
 * File upload helper for the 1min.ai SDK.
 *
 * Normalizes Uint8Array or [filename, Uint8Array] tuple inputs and uploads
 * them to /api/assets via multipart FormData POST, returning the URL string
 * from the response.
 *
 * Note: TypeScript FileInput does NOT include string paths because Node.js
 * fetch + FormData does not have direct filesystem access. Callers that need
 * to upload from a file path should read it first (e.g., fs.readFileSync)
 * and pass the resulting Buffer/Uint8Array.
 *
 * The API returns the uploaded asset URL nested at response.asset.location.
 */

import { APIError } from './error.js';
import { API_KEY_HEADER } from './constants.js';

/**
 * Accepted file input types for upload:
 * - Uint8Array: raw binary content (filename defaults to "upload")
 * - [string, Uint8Array]: explicit (filename, content) pair
 */
export type FileInput = Uint8Array | [string, Uint8Array];

/**
 * Normalize various file input types to a [filename, Uint8Array] tuple.
 *
 * @param file - A Uint8Array or [name, Uint8Array] tuple.
 * @returns A [filename, Uint8Array] pair ready for FormData upload.
 * @throws TypeError if the input type is not supported or the tuple is malformed.
 */
export function normalizeFile(file: FileInput): [string, Uint8Array] {
  if (file instanceof Uint8Array) {
    return ['upload', file];
  }

  if (
    Array.isArray(file) &&
    file.length === 2 &&
    typeof file[0] === 'string' &&
    file[1] instanceof Uint8Array
  ) {
    return [file[0], file[1]];
  }

  throw new TypeError(
    `Unsupported file input type: ${typeof file}. Expected Uint8Array or [string, Uint8Array].`,
  );
}

/**
 * Extract the uploaded file URL from the /api/assets response JSON.
 *
 * Reads the nested path data.asset.location as documented in the API.
 *
 * @param data - Parsed JSON response from /api/assets.
 * @returns The URL string for the uploaded asset.
 * @throws APIError if no recognized URL field is found.
 */
export function extractUrl(data: Record<string, unknown>): string {
  const asset = data.asset;
  if (
    asset !== null &&
    asset !== undefined &&
    typeof asset === 'object' &&
    'location' in (asset as Record<string, unknown>)
  ) {
    const location = (asset as Record<string, unknown>).location;
    if (typeof location === 'string' && location.length > 0) {
      return location;
    }
  }

  throw new APIError(
    `No asset URL found in upload response. ` +
      `Expected data.asset.location. ` +
      `Response: ${JSON.stringify(data)}`,
    0,
  );
}

/**
 * Upload a file to /api/assets and return the URL string.
 *
 * Sends a multipart FormData POST request with the file under the "file" field.
 * The API-KEY header is set from the provided apiKey.
 *
 * @param baseUrl - The API base URL (e.g., "https://api.1min.ai").
 * @param apiKey - The 1min.ai API key.
 * @param file - The file to upload.
 * @param options - Optional timeout in milliseconds (default 30000).
 * @returns The URL string of the uploaded asset.
 * @throws TypeError if the file input type is not supported.
 * @throws APIError if the response has a non-2xx status or no URL field.
 */
export async function uploadFile(
  baseUrl: string,
  apiKey: string,
  file: FileInput,
  options?: { timeout?: number },
): Promise<string> {
  const [filename, content] = normalizeFile(file);

  const formData = new FormData();
  formData.append('asset', new Blob([content]), filename);

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), options?.timeout ?? 30_000);

  try {
    const response = await fetch(`${baseUrl}/api/assets`, {
      method: 'POST',
      headers: { [API_KEY_HEADER]: apiKey },
      body: formData,
      signal: ctrl.signal,
    });

    if (!response.ok) {
      const body = await response.text().catch(() => `HTTP ${response.status}`);
      throw new APIError(body, response.status);
    }

    const data = (await response.json()) as Record<string, unknown>;
    return extractUrl(data);
  } finally {
    clearTimeout(timer);
  }
}
