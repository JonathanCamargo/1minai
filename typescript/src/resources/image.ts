/**
 * Image domain resource for the 1min.ai API.
 *
 * Domain timeout: 90s (per INFRA-07) — image generation takes significant time.
 *
 * Provides 14 public methods:
 *   generate, toPrompt, variation, upscale, extend,
 *   removeBackground, replaceBackground, removeText,
 *   removeObject, searchAndReplace, inpaint, editText,
 *   swapFace, generate3d.
 *
 * All editing methods follow the upload-then-feature pattern:
 *   1. Upload the image to /api/assets to obtain an asset URL.
 *   2. POST to /api/features with the asset URL in promptObject.
 *
 * generate() supports Midjourney auto-polling via pollJob.
 */

import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { ImageResult } from '../types.js';
import { uploadFile, type FileInput } from '../file-upload.js';
import { pollJob } from '../polling.js';

/** Midjourney model UUID — triggers async job polling instead of a direct result. */
const MIDJOURNEY_MODEL = '5c232a9e-9061-4777-980a-ddc8e65647c6';

/**
 * Accepted image input types:
 * - FileInput (Uint8Array or [filename, Uint8Array]) — uploaded to /api/assets first
 * - string starting with "http" — used as an asset URL directly (no upload)
 */
type ImageInput = FileInput | string;

export class ImageResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'image'); // 90s timeout per INFRA-07
  }

  // ------------------------------------------------------------------
  // Private helpers
  // ------------------------------------------------------------------

  /**
   * Upload a file to /api/assets or return an HTTP URL as-is.
   *
   * @param image - A FileInput or an HTTP URL string.
   * @returns The asset URL string.
   */
  private async _upload(image: ImageInput): Promise<string> {
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
   * Upload an image and POST to /api/features.
   *
   * Encapsulates the repeated pattern used by all editing methods:
   *   upload file -> build payload with imageUrl -> POST -> parse result.
   *
   * @param featureType - The API feature type constant (e.g., "BACKGROUND_REMOVER").
   * @param image - File input or URL string for the image to process.
   * @param model - Model name to include in the payload.
   * @param promptObjectExtra - Additional fields to merge into promptObject.
   * @returns An ImageResult with url, model, optional urls, and metadata.
   */
  private async _uploadAndCall(
    featureType: string,
    image: ImageInput,
    model: string,
    promptObjectExtra: Record<string, unknown>,
  ): Promise<ImageResult> {
    const assetUrl = await this._upload(image);
    const payload = {
      type: featureType,
      model,
      promptObject: {
        imageUrl: assetUrl,
        ...promptObjectExtra,
      },
    };
    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseImageResult(response, model);
  }

  /**
   * Extract an ImageResult from a raw /api/features response.
   *
   * Handles response shapes:
   *   - response.aiRecord.resultObject.url
   *   - response.aiRecord.resultObject.imageUrl
   *   - response.aiRecord.resultObject.urls or .images for multiple URLs
   *
   * @param response - Raw JSON response object from the API.
   * @param model - Model name to include in the result.
   * @returns An ImageResult.
   */
  private _parseImageResult(response: Record<string, unknown>, model: string): ImageResult {
    const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? {}) as Record<string, unknown>;

    const url = String(resultObj.url ?? resultObj.imageUrl ?? '');
    const rawUrls = resultObj.urls ?? resultObj.images;
    const urls = Array.isArray(rawUrls) ? (rawUrls as string[]) : undefined;

    return { url, model, urls, metadata: resultObj };
  }

  // ------------------------------------------------------------------
  // Public methods
  // ------------------------------------------------------------------

  /**
   * Generate an image from a text prompt.
   *
   * For Midjourney models the request is submitted as an async job and
   * automatically polled until completion (up to 5 minutes).
   *
   * @param prompt - Text description of the image to generate.
   * @param options - Optional parameters.
   * @param options.model - Model to use (default "dall-e-3").
   *   Pass "midjourney" or the Midjourney UUID to use Midjourney with polling.
   * @param options.width - Image width in pixels (default 1024).
   * @param options.height - Image height in pixels (default 1024).
   * @param options.n - Number of images to generate (default 1).
   * @returns An ImageResult with the generated image URL.
   *
   * @example
   * const result = await client.image.generate('a cat on a rooftop at sunset');
   * console.log(result.url);
   */
  async generate(
    prompt: string,
    options: {
      model?: string;
      width?: number;
      height?: number;
      n?: number;
      [key: string]: unknown;
    } = {},
  ): Promise<ImageResult> {
    const { model: rawModel = 'dall-e-3', width = 1024, height = 1024, n = 1, ...rest } = options;

    const isMidjourney =
      rawModel === MIDJOURNEY_MODEL || rawModel.toLowerCase().startsWith('midjourney');
    const effectiveModel = isMidjourney ? MIDJOURNEY_MODEL : rawModel;

    const payload = {
      type: 'IMAGE_GENERATOR',
      model: effectiveModel,
      promptObject: { prompt, width, height, n, ...rest },
    };

    let response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );

    if (isMidjourney) {
      const aiRecord = (response.aiRecord ?? {}) as Record<string, unknown>;
      const jobId = String(aiRecord.id ?? '');
      response = await pollJob(this.client.baseUrl, (this.client as unknown as { apiKey: string }).apiKey, jobId);
    }

    return this._parseImageResult(response, effectiveModel);
  }

  /**
   * Convert an image to a text description (image-to-prompt).
   *
   * @param image - Image file or URL to describe.
   * @param options - Optional parameters including model (default "gpt-4o").
   * @returns An ImageResult whose `url` field contains the description text.
   *
   * @example
   * const result = await client.image.toPrompt(imageBytes);
   * console.log(result.url); // The generated description
   */
  async toPrompt(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'gpt-4o', ...rest } = options;
    return this._uploadAndCall('IMAGE_TO_PROMPT', image, model, rest);
  }

  /**
   * Generate a variation of an existing image.
   *
   * @param image - Source image file or URL.
   * @param options - Optional parameters including model (default "dall-e-2") and n.
   * @returns An ImageResult with the variation URL(s).
   *
   * @example
   * const result = await client.image.variation(imageBytes);
   * console.log(result.url);
   */
  async variation(
    image: ImageInput,
    options: { model?: string; n?: number; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', n = 1, ...rest } = options;
    return this._uploadAndCall('IMAGE_VARIATOR', image, model, { n, ...rest });
  }

  /**
   * Upscale an image to higher resolution.
   *
   * @param image - Image file or URL to upscale.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the upscaled image URL.
   *
   * @example
   * const result = await client.image.upscale(imageBytes);
   * console.log(result.url);
   */
  async upscale(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('IMAGE_UPSCALER', image, model, rest);
  }

  /**
   * Extend the canvas of an image outward (outpainting).
   *
   * @param image - Image file or URL to extend.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the extended image URL.
   *
   * @example
   * const result = await client.image.extend(imageBytes);
   * console.log(result.url);
   */
  async extend(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('IMAGE_EXTENDER', image, model, rest);
  }

  /**
   * Remove the background from an image.
   *
   * @param image - Image file or URL.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the background-removed image URL.
   *
   * @example
   * const result = await client.image.removeBackground(imageBytes);
   * console.log(result.url);
   */
  async removeBackground(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('BACKGROUND_REMOVER', image, model, rest);
  }

  /**
   * Replace the background of an image with a new scene.
   *
   * @param image - Image file or URL with the foreground subject.
   * @param prompt - Text description of the new background.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the new-background image URL.
   *
   * @example
   * const result = await client.image.replaceBackground(imageBytes, 'a tropical beach');
   * console.log(result.url);
   */
  async replaceBackground(
    image: ImageInput,
    prompt: string,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('BACKGROUND_REPLACER', image, model, { prompt, ...rest });
  }

  /**
   * Remove text overlays from an image.
   *
   * @param image - Image file or URL containing text to remove.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the text-removed image URL.
   *
   * @example
   * const result = await client.image.removeText(imageBytes);
   * console.log(result.url);
   */
  async removeText(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('TEXT_REMOVER', image, model, rest);
  }

  /**
   * Remove a specified object from an image.
   *
   * @param image - Image file or URL.
   * @param prompt - Description of the object to remove.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the object-removed image URL.
   *
   * @example
   * const result = await client.image.removeObject(imageBytes, 'the red car');
   * console.log(result.url);
   */
  async removeObject(
    image: ImageInput,
    prompt: string,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('IMAGE_OBJECT_REMOVER', image, model, { prompt, ...rest });
  }

  /**
   * Find an element in an image and replace it.
   *
   * @param image - Image file or URL.
   * @param searchPrompt - Description of the element to find and replace.
   * @param replacePrompt - Description of what to replace it with.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the modified image URL.
   *
   * @example
   * const result = await client.image.searchAndReplace(imageBytes, 'blue car', 'red sports car');
   * console.log(result.url);
   */
  async searchAndReplace(
    image: ImageInput,
    searchPrompt: string,
    replacePrompt: string,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('SEARCH_AND_REPLACE', image, model, {
      searchPrompt,
      replacePrompt,
      ...rest,
    });
  }

  /**
   * Fill a masked area of an image guided by a text prompt (inpainting).
   *
   * @param image - Source image file or URL.
   * @param mask - Mask image file or URL (white = area to fill, black = keep).
   * @param prompt - Text description of what to generate in the masked area.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the inpainted image URL.
   *
   * @example
   * const result = await client.image.inpaint(imageBytes, maskBytes, 'a bouquet of flowers');
   * console.log(result.url);
   */
  async inpaint(
    image: ImageInput,
    mask: ImageInput,
    prompt: string,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    const imageUrl = await this._upload(image);
    const maskUrl = await this._upload(mask);
    const payload = {
      type: 'IMAGE_INPAINTER',
      model,
      promptObject: { imageUrl, maskUrl, prompt, ...rest },
    };
    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseImageResult(response, model);
  }

  /**
   * Edit text content within an image.
   *
   * @param image - Image file or URL containing text to edit.
   * @param textConfig - Configuration object describing the text edits.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the text-edited image URL.
   *
   * @example
   * const result = await client.image.editText(imageBytes, { text: 'Hello', x: 10, y: 20 });
   * console.log(result.url);
   */
  async editText(
    image: ImageInput,
    textConfig: Record<string, unknown>,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('IMAGE_EDITOR', image, model, { textConfig, ...rest });
  }

  /**
   * Swap a face from the source image onto the target image.
   *
   * @param sourceImage - Image file or URL containing the face to copy.
   * @param targetImage - Image file or URL to place the face onto.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the face-swapped image URL.
   *
   * @example
   * const result = await client.image.swapFace(sourceBytes, targetBytes);
   * console.log(result.url);
   */
  async swapFace(
    sourceImage: ImageInput,
    targetImage: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    const sourceImageUrl = await this._upload(sourceImage);
    const targetImageUrl = await this._upload(targetImage);
    const payload = {
      type: 'FACE_SWAPPER',
      model,
      promptObject: { sourceImageUrl, targetImageUrl, ...rest },
    };
    const response = await this.client._request<Record<string, unknown>>(
      'POST',
      '/api/features',
      payload,
      { timeout: this.timeout },
    );
    return this._parseImageResult(response, model);
  }

  /**
   * Generate a 3D representation of an object from an image.
   *
   * @param image - Image file or URL of the object to convert to 3D.
   * @param options - Optional parameters including model (default "dall-e-2").
   * @returns An ImageResult with the 3D model URL.
   *
   * @example
   * const result = await client.image.generate3d(imageBytes);
   * console.log(result.url);
   */
  async generate3d(
    image: ImageInput,
    options: { model?: string; [key: string]: unknown } = {},
  ): Promise<ImageResult> {
    const { model = 'dall-e-2', ...rest } = options;
    return this._uploadAndCall('IMAGE_3D_GENERATOR', image, model, rest);
  }
}
