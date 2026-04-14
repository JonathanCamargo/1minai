import type { BaseOneMinClient } from '../base-client.js';
import { DOMAIN_TIMEOUTS } from '../constants.js';

export class BaseResource {
  protected readonly timeout: number;

  constructor(
    protected readonly client: BaseOneMinClient,
    protected readonly domain: string = 'text',
  ) {
    this.timeout = DOMAIN_TIMEOUTS[domain] ?? 30_000;
  }

  async raw<T = unknown>(payload: Record<string, unknown>): Promise<T> {
    return this.client._request<T>('POST', '/api/features', payload, {
      timeout: this.timeout,
    });
  }
}
