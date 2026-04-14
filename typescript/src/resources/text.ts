import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { TextResult } from '../types.js';
import { streamSSE } from '../streaming.js';
import { API_KEY_HEADER } from '../constants.js';

export interface ChatOptions {
  model?: string;
  stream?: boolean;
  webSearch?: boolean;
  chatHistory?: Array<{ role: string; message: string }>;
  [key: string]: unknown;
}

export class TextResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'text');
  }

  /**
   * Send a chat/completion request to a language model.
   *
   * @param prompt - The user message to send.
   * @param options - Optional parameters: model (default "gpt-4o"), stream,
   *   webSearch, chatHistory, and any extra fields forwarded to promptObject.
   * @returns TextResult with content, model name, and optional usage metadata.
   *   When stream is true, returns an AsyncGenerator yielding token strings.
   *
   * @example
   * const result = await client.text.chat('What is 2+2?');
   * console.log(result.content);
   *
   * @example
   * // Streaming
   * for await (const token of await client.text.chat('Tell me a joke', { stream: true })) {
   *   process.stdout.write(token);
   * }
   */
  async chat(prompt: string, options: ChatOptions & { stream: true }): Promise<AsyncGenerator<string, void, undefined>>;
  async chat(prompt: string, options?: ChatOptions & { stream?: false }): Promise<TextResult>;
  async chat(prompt: string, options?: ChatOptions): Promise<TextResult | AsyncGenerator<string, void, undefined>>;
  async chat(
    prompt: string,
    options: ChatOptions = {},
  ): Promise<TextResult | AsyncGenerator<string, void, undefined>> {
    const {
      model = 'gpt-4o',
      stream = false,
      webSearch = false,
      chatHistory = [],
      ...extra
    } = options;

    const payload: Record<string, unknown> = {
      type: 'CHAT_WITH_AI',
      model,
      promptObject: {
        prompt,
        isMixed: false,
        webSearch,
        chatList: chatHistory,
        ...extra,
      },
    };

    if (stream) {
      return this._streamChat(payload, model);
    }

    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseTextResult(response, model);
  }

  private async _streamChat(
    payload: Record<string, unknown>,
    _model: string,
  ): Promise<AsyncGenerator<string, void, undefined>> {
    const url = `${this.client.baseUrl}/api/features?isStreaming=true`;
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          [API_KEY_HEADER]: (this.client as unknown as { apiKey: string }).apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: ctrl.signal,
      });
      clearTimeout(timer);
      return streamSSE(response);
    } catch (err) {
      clearTimeout(timer);
      throw err;
    }
  }

  private _parseTextResult(
    response: Record<string, unknown>,
    model: string,
  ): TextResult {
    const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? {}) as Record<string, unknown>;
    const content = String(
      resultObj.message ?? resultObj.content ?? resultObj.text ?? JSON.stringify(resultObj),
    );
    const usage = resultObj.usage as Record<string, unknown> | undefined;
    return { content, model, usage };
  }
}
