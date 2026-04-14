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
   * const raw = await client.conversation.raw({ title: 'Test', type: 'CHAT_WITH_AI', model: 'gpt-4o' });
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
   *   conversationType (default "CHAT_WITH_AI"), and any extra fields.
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
      conversationType = 'CHAT_WITH_AI',
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
      chatHistory?: Array<{ role: string; message: string }>;
      [key: string]: unknown;
    } = {},
  ): Promise<ConversationResult> {
    const { model = 'gpt-4o', chatHistory = [], ...extra } = options;

    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      {
        type: 'CHAT_WITH_AI',
        model,
        conversationId,
        promptObject: {
          prompt,
          chatList: chatHistory,
          ...extra,
        },
      },
      { timeout: this.timeout },
    );

    const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? {}) as Record<string, unknown>;
    const content = String(
      resultObj.message ?? resultObj.content ?? resultObj.text ?? JSON.stringify(resultObj),
    );
    return {
      content,
      conversationId,
      model,
      metadata: resultObj,
    };
  }
}
