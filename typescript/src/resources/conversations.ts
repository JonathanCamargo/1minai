import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { ConversationResult } from '../types.js';

export class ConversationResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'conversation');
  }

  /**
   * Send a raw request to /api/conversations and return the response as-is.
   *
   * @param payload - The raw JSON payload to send to the conversations endpoint.
   * @returns The raw API response typed as T.
   *
   * @example
   * const raw = await client.conversation.raw({ title: 'Test', type: 'UNIFY_CHAT_WITH_AI', model: 'gpt-4o' });
   */
  override async raw<T = unknown>(payload: Record<string, unknown>): Promise<T> {
    return this.client._request<T>('POST', '/api/conversations', payload, {
      timeout: this.timeout,
    });
  }

  /**
   * Create a new conversation and return its ID.
   *
   * @param options - Optional parameters: title (default "Untitled"), model (default "gpt-4o"),
   *   conversationType (default "UNIFY_CHAT_WITH_AI" -- the recommended unified flow that
   *   covers text, image, file, and YouTube inputs; legacy CHAT_WITH_IMAGE/CHAT_WITH_PDF/
   *   CHAT_WITH_YOUTUBE_VIDEO are deprecated upstream), and any extra fields.
   * @returns ConversationResult with conversationId and empty initial content.
   *
   * @example
   * const conv = await client.conversation.create({ title: 'My Chat' });
   * console.log(conv.conversationId);
   */
  async create(options: {
    title?: string;
    model?: string;
    conversationType?: string;
    [key: string]: unknown;
  } = {}): Promise<ConversationResult> {
    const {
      title = 'Untitled',
      model = 'gpt-4o',
      conversationType = 'UNIFY_CHAT_WITH_AI',
      ...extra
    } = options;

    const response = await this.raw<Record<string, unknown>>({
      title,
      type: conversationType,
      model,
      ...extra,
    });
    const conv = (response.conversation ?? {}) as Record<string, unknown>;
    return {
      content: '',
      conversationId: String(conv.id ?? ''),
      model,
      metadata: conv,
    };
  }

  /**
   * Send a message in an existing conversation.
   *
   * @param conversationId - The ID of the conversation to send the message to.
   * @param prompt - The user message to send.
   * @param options - Optional parameters: model (default "gpt-4o"), chatHistory, and extra fields.
   * @returns ConversationResult with content, conversationId, model, and metadata.
   *
   * @example
   * const conv = await client.conversation.create();
   * const reply = await client.conversation.send(conv.conversationId, 'What is TypeScript?');
   * console.log(reply.content);
   */
  async send(
    conversationId: string,
    prompt: string,
    options: {
      model?: string;
      [key: string]: unknown;
    } = {},
  ): Promise<ConversationResult> {
    const { model = 'gpt-4o', ...extra } = options;

    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/chat-with-ai',
      {
        type: 'UNIFY_CHAT_WITH_AI',
        model,
        promptObject: {
          prompt,
          conversationId,
          ...extra,
        },
      },
      { timeout: this.timeout },
    );

    const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
    const detail = (aiRecord.aiRecordDetail ?? {}) as Record<string, unknown>;
    const resultObj = detail.resultObject ?? aiRecord.resultObject;
    let content: string;
    let metadata: Record<string, unknown>;
    if (Array.isArray(resultObj)) {
      content = resultObj.map((c) => String(c)).join('');
      metadata = { resultObject: resultObj };
    } else if (resultObj && typeof resultObj === 'object') {
      const r = resultObj as Record<string, unknown>;
      content = String(r.message ?? r.content ?? r.text ?? JSON.stringify(r));
      metadata = r;
    } else {
      content = resultObj == null ? '' : String(resultObj);
      metadata = {};
    }
    return {
      content,
      conversationId,
      model,
      metadata,
    };
  }
}
