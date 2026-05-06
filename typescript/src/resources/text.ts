import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { TextResult } from '../types.js';
import { streamSSE } from '../streaming.js';
import { API_KEY_HEADER } from '../constants.js';

export interface ChatOptions {
  model?: string;
  stream?: boolean;
  webSearch?: boolean;
  /** Number of sites web search should query (only applied when webSearch is true). */
  numOfSite?: number;
  /** Maximum words extracted per site (only applied when webSearch is true). */
  maxWord?: number;
  [key: string]: unknown;
}

export class TextResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'text');
  }

  /**
   * Send a chat/completion request to a language model.
   *
   * Hits POST /api/chat-with-ai with type `UNIFY_CHAT_WITH_AI` -- the unified
   * endpoint that replaces the legacy CHAT_WITH_IMAGE / CHAT_WITH_PDF /
   * CHAT_WITH_YOUTUBE_VIDEO feature types. Pass `attachments`,
   * `conversationId`, `settings`, `brandVoiceId`, or `metadata` through
   * `options` to access the full promptObject schema documented at
   * https://docs.1min.ai/docs/api/chat-with-ai-api.
   *
   * @param prompt - The user message to send. Including a YouTube URL in the
   *   prompt triggers automatic transcript extraction (max 3 URLs).
   * @param options - Optional parameters: model (default "gpt-4o"), stream,
   *   webSearch, numOfSite, maxWord, plus any promptObject fields
   *   (`attachments`, `conversationId`, `settings`, etc.).
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
      numOfSite,
      maxWord,
      ...extra
    } = options;

    const promptObject: Record<string, unknown> = { prompt, ...extra };
    if (webSearch) {
      const webSearchSettings: Record<string, unknown> = { webSearch: true };
      if (numOfSite !== undefined) webSearchSettings.numOfSite = numOfSite;
      if (maxWord !== undefined) webSearchSettings.maxWord = maxWord;
      promptObject.settings = { webSearchSettings };
    }

    const payload: Record<string, unknown> = {
      type: 'UNIFY_CHAT_WITH_AI',
      model,
      promptObject,
    };

    if (stream) {
      return this._streamChat(payload, model);
    }

    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/chat-with-ai',
      payload,
      { timeout: this.timeout },
    );
    return this._parseTextResult(response, model);
  }

  private async _streamChat(
    payload: Record<string, unknown>,
    _model: string,
  ): Promise<AsyncGenerator<string, void, undefined>> {
    const url = `${this.client.baseUrl}/api/chat-with-ai?isStreaming=true`;
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
    const detail = (aiRecord.aiRecordDetail ?? {}) as Record<string, unknown>;
    const resultObj = detail.resultObject ?? aiRecord.resultObject;
    let content: string;
    if (Array.isArray(resultObj)) {
      content = resultObj.map((c) => String(c)).join('');
    } else if (resultObj && typeof resultObj === 'object') {
      const r = resultObj as Record<string, unknown>;
      content = String(r.message ?? r.content ?? r.text ?? JSON.stringify(r));
    } else {
      content = resultObj == null ? '' : String(resultObj);
    }
    return { content, model };
  }
}
