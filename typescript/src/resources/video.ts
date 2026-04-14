/**
 * Video domain resource for the 1min.ai API.
 *
 * Domain timeout: 300s (per INFRA-07) — video generation is the most time-intensive
 * operation and can take several minutes to complete.
 *
 * Provides 2 methods:
 * - generate: text-to-video using Luma AI, Kling, AnimateDiff, Tongyi
 * - fromImage: image-to-video using Luma AI, Kling
 *
 * Both methods auto-poll for completion since all video models are async.
 */

import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { VideoResult } from '../types.js';
import { uploadFile, type FileInput } from '../file-upload.js';
import { pollJob } from '../polling.js';

export class VideoResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'video'); // 300s timeout per INFRA-07
  }

  /**
   * Upload a file or return URL if already a remote URL.
   *
   * @param image - Binary file data or HTTP URL string.
   * @returns URL string pointing to the uploaded (or existing) asset.
   */
  private async _upload(image: FileInput | string): Promise<string> {
    if (typeof image === 'string' && image.startsWith('http')) {
      return image;
    }
    return uploadFile(
      this.client.baseUrl,
      (this.client as unknown as { apiKey: string }).apiKey,
      image as FileInput,
    );
  }

  /**
   * Poll for async job completion and parse the video result.
   *
   * @param response - Initial API response containing aiRecord.id.
   * @param model - Model name for the VideoResult.
   * @returns VideoResult with url and metadata from the completed job.
   */
  private async _pollAndParse(
    response: Record<string, unknown>,
    model: string,
  ): Promise<VideoResult> {
    const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
    const jobId = String(
      aiRecord.id ?? aiRecord.jobId ?? response.id ?? '',
    );

    const result = await pollJob(
      this.client.baseUrl,
      (this.client as unknown as { apiKey: string }).apiKey,
      jobId,
    );

    const output = (result.output ?? {}) as Record<string, unknown>;
    const url =
      (typeof result.result === 'string' ? result.result : undefined) ??
      (typeof output.url === 'string' ? output.url : undefined) ??
      (typeof result.url === 'string' ? result.url : undefined) ??
      '';

    return { url, model, metadata: result };
  }

  /**
   * Generate a video from a text prompt.
   *
   * All video generation models are asynchronous — this method automatically
   * polls until completion and returns the final VideoResult.
   *
   * @param prompt - Text description of the video to generate.
   * @param options - Optional parameters: model, duration, aspectRatio, and extra API fields.
   * @returns VideoResult with url pointing to the generated video file.
   *
   * @example
   * const result = await client.video.generate('sunset over the ocean', { model: 'luma-ai' });
   * console.log(result.url);
   */
  async generate(
    prompt: string,
    options?: {
      model?: string;
      duration?: number;
      aspectRatio?: string;
      [key: string]: unknown;
    },
  ): Promise<VideoResult> {
    const { model = 'luma-ai', duration, aspectRatio, ...extra } = options ?? {};

    const promptObject: Record<string, unknown> = { prompt };
    if (duration !== undefined) {
      promptObject['duration'] = duration;
    }
    if (aspectRatio !== undefined) {
      promptObject['aspectRatio'] = aspectRatio;
    }
    Object.assign(promptObject, extra);

    const payload = {
      type: 'TEXT_TO_VIDEO',
      model,
      promptObject,
    };

    const response = await this.raw<Record<string, unknown>>(payload);
    return this._pollAndParse(response, model);
  }

  /**
   * Generate a video from an image and optional text prompt.
   *
   * All video generation models are asynchronous — this method automatically
   * polls until completion and returns the final VideoResult.
   *
   * @param image - Binary image data or HTTP URL of an uploaded image.
   * @param prompt - Optional text description to guide the animation.
   * @param options - Optional parameters: model and extra API fields.
   * @returns VideoResult with url pointing to the generated video file.
   *
   * @example
   * const result = await client.video.fromImage(imageBuffer, 'animate the scene');
   * console.log(result.url);
   */
  async fromImage(
    image: FileInput | string,
    prompt?: string,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<VideoResult> {
    const { model = 'luma-ai', ...extra } = options ?? {};

    const imageUrl = await this._upload(image);

    const promptObject: Record<string, unknown> = {
      prompt: prompt ?? '',
      imageUrl,
      ...extra,
    };

    const payload = {
      type: 'IMAGE_TO_VIDEO',
      model,
      promptObject,
    };

    const response = await this.raw<Record<string, unknown>>(payload);
    return this._pollAndParse(response, model);
  }
}
