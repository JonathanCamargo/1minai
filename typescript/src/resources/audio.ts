/**
 * Audio domain resource for the 1min.ai API.
 *
 * Domain timeout: 90s (per INFRA-07) — audio processing takes significant time.
 *
 * Provides 4 methods:
 * - speak: text-to-speech (TTS) using ElevenLabs, OpenAI TTS, Google TTS
 * - transcribe: speech-to-text (STT) using Whisper
 * - translate: audio translation using Whisper
 * - generateMusic: music generation using Suno, Udio, MusicGen
 */

import { BaseResource } from './base-resource.js';
import type { BaseOneMinClient } from '../base-client.js';
import type { AudioResult } from '../types.js';
import { uploadFile, type FileInput } from '../file-upload.js';

/** Audio input: binary file data or an existing HTTP URL string. */
type AudioInput = FileInput | string;

export class AudioResource extends BaseResource {
  constructor(client: BaseOneMinClient) {
    super(client, 'audio'); // 90s timeout per INFRA-07
  }

  /**
   * Upload a file or return URL if already a remote URL.
   *
   * @param audio - Binary file data or HTTP URL string.
   * @returns URL string pointing to the uploaded (or existing) asset.
   */
  private async _upload(audio: AudioInput): Promise<string> {
    if (typeof audio === 'string' && audio.startsWith('http')) {
      return audio;
    }
    return uploadFile(
      this.client.baseUrl,
      (this.client as unknown as { apiKey: string }).apiKey,
      audio as FileInput,
    );
  }

  /**
   * Convert text to speech audio.
   *
   * @param text - The text to convert to speech.
   * @param options - Optional parameters: model, voice, and extra API fields.
   * @returns AudioResult with url pointing to the generated audio file.
   *
   * @example
   * const result = await client.audio.speak('Hello world', { model: 'tts-1' });
   * console.log(result.url);
   */
  async speak(
    text: string,
    options?: { model?: string; voice?: string; [key: string]: unknown },
  ): Promise<AudioResult> {
    const { model = 'tts-1', voice, ...extra } = options ?? {};

    const promptObject: Record<string, unknown> = { prompt: text };
    if (voice !== undefined) {
      promptObject['voice'] = voice;
    }
    Object.assign(promptObject, extra);

    const payload = {
      type: 'TEXT_TO_SPEECH',
      model,
      promptObject,
    };

    const response = await this.raw<Record<string, unknown>>(payload);

    const aiRecord = (response.aiRecord ?? response) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? aiRecord) as Record<string, unknown>;
    const url =
      (typeof resultObj.url === 'string' ? resultObj.url : undefined) ??
      (typeof resultObj.audioUrl === 'string' ? resultObj.audioUrl : undefined) ??
      '';

    return { url, model, metadata: resultObj };
  }

  /**
   * Transcribe speech from an audio file to text.
   *
   * @param audio - Binary audio data or HTTP URL of an uploaded audio file.
   * @param options - Optional parameters: model and extra API fields.
   * @returns AudioResult with content containing the transcript text.
   *
   * @example
   * const result = await client.audio.transcribe(audioBuffer);
   * console.log(result.content);
   */
  async transcribe(
    audio: AudioInput,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<AudioResult> {
    const { model = 'whisper-1', ...extra } = options ?? {};

    const audioUrl = await this._upload(audio);

    const payload = {
      type: 'SPEECH_TO_TEXT',
      model,
      promptObject: { audioUrl, ...extra },
    };

    const response = await this.raw<Record<string, unknown>>(payload);

    const aiRecord = (response.aiRecord ?? response) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? aiRecord) as Record<string, unknown>;
    const text =
      (typeof resultObj.text === 'string' ? resultObj.text : undefined) ??
      (typeof resultObj.content === 'string' ? resultObj.content : undefined) ??
      (typeof resultObj.message === 'string' ? resultObj.message : undefined) ??
      '';

    return { content: text, model, metadata: resultObj };
  }

  /**
   * Translate speech in an audio file to English text.
   *
   * @param audio - Binary audio data or HTTP URL of an uploaded audio file.
   * @param options - Optional parameters: model and extra API fields.
   * @returns AudioResult with content containing the translated text.
   *
   * @example
   * const result = await client.audio.translate(spanishAudioBuffer);
   * console.log(result.content); // English translation
   */
  async translate(
    audio: AudioInput,
    options?: { model?: string; [key: string]: unknown },
  ): Promise<AudioResult> {
    const { model = 'whisper-1', ...extra } = options ?? {};

    const audioUrl = await this._upload(audio);

    const payload = {
      type: 'AUDIO_TRANSLATOR',
      model,
      promptObject: { audioUrl, ...extra },
    };

    const response = await this.raw<Record<string, unknown>>(payload);

    const aiRecord = (response.aiRecord ?? response) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? aiRecord) as Record<string, unknown>;
    const text =
      (typeof resultObj.text === 'string' ? resultObj.text : undefined) ??
      (typeof resultObj.content === 'string' ? resultObj.content : undefined) ??
      (typeof resultObj.message === 'string' ? resultObj.message : undefined) ??
      '';

    return { content: text, model, metadata: resultObj };
  }

  /**
   * Generate music from a text description.
   *
   * @param prompt - Text description of the music to generate.
   * @param options - Optional parameters: model, duration, and extra API fields.
   * @returns AudioResult with url pointing to the generated music file.
   *
   * @example
   * const result = await client.audio.generateMusic('upbeat electronic', { duration: 30 });
   * console.log(result.url);
   */
  async generateMusic(
    prompt: string,
    options?: { model?: string; duration?: number; [key: string]: unknown },
  ): Promise<AudioResult> {
    const { model = 'music-s', duration = 30, ...extra } = options ?? {};

    const payload = {
      type: 'MUSIC_GENERATOR',
      model,
      promptObject: { prompt, duration, ...extra },
    };

    const response = await this.raw<Record<string, unknown>>(payload);

    const aiRecord = (response.aiRecord ?? response) as Record<string, unknown>;
    const resultObj = (aiRecord.resultObject ?? aiRecord) as Record<string, unknown>;
    const url =
      (typeof resultObj.url === 'string' ? resultObj.url : undefined) ??
      (typeof resultObj.audioUrl === 'string' ? resultObj.audioUrl : undefined) ??
      '';

    return { url, model, metadata: resultObj };
  }
}
