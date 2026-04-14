import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { WritingResult } from '../types.js';

export class WritingResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'writing'); // 30s timeout (per INFRA-07)
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  /**
   * Common request method for all writing endpoints with sentinel conversationId.
   * conversationId MUST equal the feature type string or the API will reject.
   */
  private async _writingCall(
    featureType: string,
    prompt: string,
    model: string,
    extraPayload?: Record<string, unknown>,
    extraPromptFields?: Record<string, unknown>,
  ): Promise<WritingResult> {
    const payload: Record<string, unknown> = {
      type: featureType,
      model,
      conversationId: featureType, // SENTINEL — must equal the type string
      promptObject: {
        prompt,
        ...extraPromptFields,
      },
      ...extraPayload,
    };
    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseWritingResult(response, model);
  }

  /**
   * Extract a WritingResult from a raw API response.
   */
  private _parseWritingResult(
    response: Record<string, unknown>,
    model: string,
  ): WritingResult {
    const aiRecord = (response['aiRecord'] ?? {}) as Record<string, unknown>;
    const resultObj = (aiRecord['resultObject'] ?? {}) as Record<string, unknown>;
    const content =
      (resultObj['message'] as string | undefined) ??
      (resultObj['content'] as string | undefined) ??
      (resultObj['text'] as string | undefined) ??
      JSON.stringify(resultObj);
    return { content, model, metadata: resultObj };
  }

  // ------------------------------------------------------------------
  // Public methods
  // ------------------------------------------------------------------

  /**
   * Research keywords for SEO or content planning.
   *
   * @param topic - The topic or niche to research keywords for.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the keyword list.
   *
   * @example
   * const result = await client.writing.keywordResearch('electric vehicles');
   * console.log(result.content);
   */
  async keywordResearch(
    topic: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('KEYWORD_RESEARCH', topic, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Generate a full blog article on the given topic.
   *
   * @param topic - The subject of the blog article.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the generated article.
   *
   * @example
   * const result = await client.writing.blogArticle('benefits of meditation');
   * console.log(result.content);
   */
  async blogArticle(
    topic: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('CONTENT_GENERATOR_BLOG_ARTICLE', topic, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Rewrite a block of text while preserving its meaning.
   *
   * @param text - The text to rewrite.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the rewritten text.
   *
   * @example
   * const result = await client.writing.rewrite('The quick brown fox jumps.');
   * console.log(result.content);
   */
  async rewrite(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('REWRITER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Expand a short passage into a longer, more detailed version.
   *
   * @param text - The text to expand.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the expanded text.
   *
   * @example
   * const result = await client.writing.expand('AI is transforming industries.');
   * console.log(result.content);
   */
  async expand(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('CONTENT_EXPANDER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Shorten a piece of text while retaining key information.
   *
   * @param text - The text to shorten.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the shortened text.
   *
   * @example
   * const result = await client.writing.shorten('A very long paragraph...');
   * console.log(result.content);
   */
  async shorten(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('CONTENT_SHORTENER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Translate text into the target language.
   *
   * @param text - The text to translate.
   * @param options - Optional parameters: model, targetLanguage (default "en").
   * @returns WritingResult with content containing the translated text.
   *
   * @example
   * const result = await client.writing.translate('Bonjour le monde', { targetLanguage: 'en' });
   * console.log(result.content);
   */
  async translate(
    text: string,
    options?: { model?: string; targetLanguage?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', targetLanguage = 'en', ...rest } = options ?? {};
    return this._writingCall(
      'CONTENT_TRANSLATOR',
      text,
      model,
      undefined,
      { targetLanguage, ...rest as Record<string, unknown> },
    );
  }

  /**
   * Paraphrase text to express the same idea with different wording.
   *
   * @param text - The text to paraphrase.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the paraphrased text.
   *
   * @example
   * const result = await client.writing.paraphrase('The sun is very bright today.');
   * console.log(result.content);
   */
  async paraphrase(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('PARAPHRASER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Summarize a block of text.
   *
   * @param text - The text to summarize.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the summary.
   *
   * @example
   * const result = await client.writing.summarize('A long article text...');
   * console.log(result.content);
   */
  async summarize(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('SUMMARIZER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Check and correct the grammar of a block of text.
   *
   * @param text - The text to grammar-check.
   * @param options - Optional parameters: model, and any extra prompt fields.
   * @returns WritingResult with content containing the corrected text.
   *
   * @example
   * const result = await client.writing.checkGrammar('She dont like cats.');
   * console.log(result.content);
   */
  async checkGrammar(
    text: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const { model = 'gpt-4o', ...rest } = options ?? {};
    return this._writingCall('GRAMMAR_CHECKER', text, model, undefined, rest as Record<string, unknown>);
  }

  /**
   * Summarize a YouTube video.
   *
   * Uses the double videoUrl pattern required by the API: videoUrl must
   * appear at the top-level payload AND inside promptObject.
   *
   * @param videoUrl - The YouTube video URL to summarize.
   * @param options - Optional: model, prompt, and any extra prompt fields.
   * @returns WritingResult with content containing the video summary.
   *
   * @example
   * const result = await client.writing.summarizeYoutube('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
   * console.log(result.content);
   */
  async summarizeYoutube(
    videoUrl: string,
    options?: { model?: string; prompt?: string; [key: string]: unknown },
  ): Promise<WritingResult> {
    const model = options?.model ?? 'gpt-4o';
    const prompt = options?.prompt ?? 'Summarize this video';
    const payload: Record<string, unknown> = {
      type: 'YOUTUBE_SUMMARIZER',
      model,
      conversationId: 'YOUTUBE_SUMMARIZER', // SENTINEL
      videoUrl, // top-level field (REQUIRED)
      promptObject: {
        prompt,
        videoUrl, // also inside promptObject (REQUIRED)
      },
    };
    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseWritingResult(response, model);
  }
}
