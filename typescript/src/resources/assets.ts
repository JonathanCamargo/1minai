import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { AssetResult } from '../types.js';
import { normalizeFile, type FileInput } from '../file-upload.js';
import { API_KEY_HEADER } from '../constants.js';
import { APIError } from '../error.js';

export class AssetResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'asset');
  }

  /**
   * Send a raw request to /api/assets and return the response as-is.
   *
   * @param payload - The raw JSON payload to send to the assets endpoint.
   * @returns The raw API response typed as T.
   *
   * @example
   * const raw = await client.assets.raw({ action: 'list' });
   */
  override async raw<T = unknown>(payload: Record<string, unknown>): Promise<T> {
    return this.client._request<T>('POST', '/api/assets', payload, {
      timeout: this.timeout,
    });
  }

  /**
   * Upload a file to /api/assets and return AssetResult.
   *
   * @param file - A Uint8Array or [filename, Uint8Array] tuple.
   * @returns AssetResult with url, assetId, and contentType.
   *
   * @example
   * const result = await client.assets.upload(fileBytes);
   * console.log(result.url);
   */
  async upload(file: FileInput): Promise<AssetResult> {
    const [filename, content] = normalizeFile(file);
    const formData = new FormData();
    formData.append('asset', new Blob([content]), filename);

    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeout);

    try {
      const response = await fetch(
        `${this.client.baseUrl}/api/assets`,
        {
          method: 'POST',
          headers: { [API_KEY_HEADER]: (this.client as unknown as { apiKey: string }).apiKey },
          body: formData,
          signal: ctrl.signal,
        },
      );

      if (!response.ok) {
        const body = await response.text().catch(() => `HTTP ${response.status}`);
        throw new APIError(body, response.status);
      }

      const data = (await response.json()) as Record<string, unknown>;
      const asset = (data.asset ?? {}) as Record<string, unknown>;
      return {
        url: String(asset.location ?? ''),
        assetId: String(asset.id ?? ''),
        contentType: asset.contentType != null ? String(asset.contentType) : undefined,
        metadata: asset,
      };
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * List available assets. GET /api/assets.
   *
   * @param options - Optional query parameters (unused currently, reserved for future filters).
   * @returns Array of asset objects from the API.
   *
   * @example
   * const assets = await client.assets.list();
   * console.log(assets.length);
   */
  async list(options?: Record<string, unknown>): Promise<unknown[]> {
    return this.client._request<unknown[]>('GET', '/api/assets', undefined, {
      timeout: this.timeout,
    });
  }

  /**
   * Get a single asset by ID. GET /api/assets/{id}.
   *
   * @param assetId - The asset ID to retrieve.
   * @returns AssetResult with url, assetId, and contentType.
   *
   * @example
   * const asset = await client.assets.get('asset-123');
   * console.log(asset.url);
   */
  async get(assetId: string): Promise<AssetResult> {
    const data = await this.client._request<Record<string, unknown>>(
      'GET',
      `/api/assets/${assetId}`,
      undefined,
      { timeout: this.timeout },
    );
    const asset = (data.asset ?? data) as Record<string, unknown>;
    return {
      url: String(asset.location ?? asset.url ?? ''),
      assetId: String(asset.id ?? assetId),
      contentType: asset.contentType != null ? String(asset.contentType) : undefined,
      metadata: asset,
    };
  }
}
