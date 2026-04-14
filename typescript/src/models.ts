/**
 * Public model constants for the 1min.ai SDK.
 *
 * Provides a discoverable `Models` object with nested domain objects
 * so developers can tab-complete model names without reading API docs.
 *
 * All values are plain strings — the exact model ID strings accepted by
 * the 1min.ai API.
 *
 * @example
 * ```typescript
 * import { Models } from 'onemin';
 *
 * // Text generation
 * const model = Models.Text.GPT_4O;
 * const model2 = Models.Text.CLAUDE_3_5_SONNET;
 *
 * // Image generation
 * const imgModel = Models.Image.MIDJOURNEY;
 * const imgModel2 = Models.Image.DALL_E_3;
 *
 * // Audio
 * const ttsModel = Models.Audio.TTS_1_HD;
 * const sttModel = Models.Audio.WHISPER_1;
 *
 * // Video
 * const vidModel = Models.Video.LUMA_AI;
 * ```
 */
export const Models = {
  /**
   * Language models for text generation, chat, and writing tasks.
   *
   * These model IDs are accepted by the `text` and `conversation` resource
   * methods (`generate`, `chat`, `summarize`, `translate`, `write`, etc.).
   */
  Text: {
    // OpenAI
    /** GPT-4o — OpenAI's most capable multimodal model */
    GPT_4O: "gpt-4o",
    /** GPT-4o Mini — smaller, faster GPT-4o */
    GPT_4O_MINI: "gpt-4o-mini",
    /** GPT-4 Turbo — previous generation high-capability model */
    GPT_4_TURBO: "gpt-4-turbo",
    /** GPT-4 — original GPT-4 */
    GPT_4: "gpt-4",
    /** GPT-3.5 Turbo — fast, cost-efficient */
    GPT_3_5_TURBO: "gpt-3.5-turbo",
    /** GPT-3.5 Turbo 16K — extended context window */
    GPT_3_5_TURBO_16K: "gpt-3.5-5-turbo",
    /** o1 — OpenAI reasoning model */
    O1: "o1",
    /** o1 Mini — smaller reasoning model */
    O1_MINI: "o1-mini",
    /** o3 Mini — latest compact reasoning model */
    O3_MINI: "o3-mini",

    // Anthropic
    /** Claude 3.5 Sonnet — Anthropic's most capable model */
    CLAUDE_3_5_SONNET: "claude-3-5-sonnet-20241022",
    /** Claude 3.5 Haiku — fast, lightweight Claude */
    CLAUDE_3_5_HAIKU: "claude-3-5-haiku-20241022",
    /** Claude 3 Opus — most powerful Claude 3 model */
    CLAUDE_3_OPUS: "claude-3-opus-20240229",
    /** Claude 3 Sonnet — balanced Claude 3 model */
    CLAUDE_3_SONNET: "claude-3-sonnet-20240229",
    /** Claude 3 Haiku — fastest Claude 3 model */
    CLAUDE_3_HAIKU: "claude-3-haiku-20240307",

    // Google
    /** Gemini 1.5 Pro — Google's most capable model */
    GEMINI_1_5_PRO: "gemini-1.5-pro",
    /** Gemini 1.5 Flash — fast, efficient Gemini */
    GEMINI_1_5_FLASH: "gemini-1.5-flash",
    /** Gemini 2.0 Flash — latest generation Gemini */
    GEMINI_2_0_FLASH: "gemini-2.0-flash",
    /** Gemini Pro — standard Gemini model */
    GEMINI_PRO: "gemini-pro",

    // Mistral
    /** Mistral Large — most capable Mistral model */
    MISTRAL_LARGE: "mistral-large-latest",
    /** Mistral Small — efficient Mistral model */
    MISTRAL_SMALL: "mistral-small-latest",
    /** Mistral Nemo — compact Mistral model */
    MISTRAL_NEMO: "mistral-nemo",
    /** Pixtral 12B — Mistral's multimodal model */
    PIXTRAL_12B: "pixtral-12b",
    /** Mixtral 8x22B — large mixture-of-experts model */
    MIXTRAL_8X22B: "open-mixtral-8x22b",
    /** Mixtral 8x7B — efficient mixture-of-experts model */
    MIXTRAL_8X7B: "open-mixtral-8x7b",
    /** Mistral 7B — base Mistral model */
    MISTRAL_7B: "open-mistral-7b",

    // Meta / Llama
    /** Llama 3.1 405B — Meta's largest open model */
    LLAMA_3_1_405B: "meta/meta-llama-3.1-405b-instruct",
    /** Llama 3 70B — capable open model */
    LLAMA_3_70B: "meta/meta-llama-3-70b-instruct",
    /** Llama 2 70B — previous generation large open model */
    LLAMA_2_70B: "meta/llama-2-70b-chat",

    // Cohere
    /** Command R Plus — Cohere's most capable model */
    COMMAND_R_PLUS: "command-r-plus",
    /** Command R — Cohere retrieval-optimized model */
    COMMAND_R: "command-r",
    /** Command — standard Cohere model */
    COMMAND: "command",

    // DeepSeek
    /** DeepSeek Chat — DeepSeek's general-purpose model */
    DEEPSEEK_CHAT: "deepseek-chat",

    // xAI
    /** Grok 2 — xAI's latest model */
    GROK_2: "grok-2",
  },

  /**
   * Image generation and editing models.
   *
   * Generation models are accepted by `client.image.generate()`.
   * Editing operation model selection is typically handled automatically
   * by the operation type (e.g., `removeBackground` uses `stable-image`).
   */
  Image: {
    // Midjourney (UUID — required by the 1min.ai API)
    /** Midjourney — premium AI image generation */
    MIDJOURNEY: "5c232a9e-9061-4777-980a-ddc8e65647c6",

    // OpenAI
    /** DALL-E 3 — OpenAI's latest image model */
    DALL_E_3: "dall-e-3",
    /** DALL-E 2 — previous generation OpenAI image model */
    DALL_E_2: "dall-e-2",

    // Stability AI
    /** Stable Diffusion XL 1024 */
    STABLE_DIFFUSION_XL: "stable-diffusion-xl-1024-v1-0",
    /** Stable Diffusion v1.6 (768px) */
    STABLE_DIFFUSION_768: "stable-diffusion-v1-6",
    /** Stable Image — used by editing operations */
    STABLE_IMAGE: "stable-image",

    // Leonardo AI
    /** Leonardo Phoenix */
    LEONARDO_PHOENIX: "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3",
    /** Leonardo Vision XL */
    LEONARDO_VISION_XL: "5c232a9e-9061-4777-980a-ddc8e65647c6",
    /** Leonardo Diffusion XL */
    LEONARDO_DIFFUSION_XL: "1e60896f-3c26-4296-8ecc-53e2afecc132",
    /** Leonardo Kino XL — cinematic style */
    LEONARDO_KINO_XL: "aa77f04e-3eec-4034-9c07-d0f619684628",
    /** Leonardo Anime XL — anime style */
    LEONARDO_ANIME_XL: "e71a1c2f-4f80-4800-934f-2c68979d1cc6",

    // Flux (Black Forest Labs)
    /** Flux Schnell — fastest Flux model */
    FLUX_SCHNELL: "flux/schnell",
    /** Flux Dev — development/research Flux model */
    FLUX_DEV: "flux/dev",
    /** Flux Pro — professional Flux model */
    FLUX_PRO: "flux/pro",
    /** Flux Pro v1.1 — latest Flux Pro */
    FLUX_PRO_1_1: "flux/pro/v1.1",

    // Ideogram
    /** Ideogram v2 — text-in-image generation */
    IDEOGRAM_V2: "ideogram-v2",
    /** Ideogram v2 Turbo — faster Ideogram */
    IDEOGRAM_V2_TURBO: "ideogram-v2-turbo",

    // Recraft
    /** Recraft v3 — vector and raster image generation */
    RECRAFT_V3: "recraftv3",

    // Google
    /** Imagen 3 — Google's latest image model */
    IMAGEN_3: "imagen-3.0-generate-002",

    // Editing operations (used internally by image resource methods)
    /** Clipdrop — used by background replacer, text remover */
    CLIPDROP: "clipdrop",
    /** Qubico Image Toolkit — used by face swapper */
    QUBICO_IMAGE_TOOLKIT: "Qubico/image-toolkit",
  },

  /**
   * Text-to-speech, speech-to-text, and music generation models.
   *
   * TTS models are accepted by `client.audio.textToSpeech()`.
   * STT models are accepted by `client.audio.speechToText()`.
   * Music models are accepted by `client.audio.generateMusic()`.
   */
  Audio: {
    // OpenAI — Text-to-Speech
    /** TTS-1 — OpenAI standard text-to-speech */
    TTS_1: "tts-1",
    /** TTS-1 HD — OpenAI high-definition text-to-speech */
    TTS_1_HD: "tts-1-hd",

    // ElevenLabs — Text-to-Speech
    /** ElevenLabs TTS — high-quality voice synthesis */
    ELEVENLABS_TTS: "elevenlabs-tts",

    // Google — Text-to-Speech
    /** Google TTS — Google Cloud text-to-speech */
    GOOGLE_TTS: "google-tts",

    // OpenAI — Speech-to-Text
    /** Whisper-1 — OpenAI speech recognition */
    WHISPER_1: "whisper-1",

    // Music generation
    /** Suno — AI music generation */
    SUNO: "music-s",
    /** Udio — AI music generation */
    UDIO: "music-u",
  },

  /**
   * Video generation models.
   *
   * Accepted by `client.video.generate()`.
   */
  Video: {
    // Luma AI
    /** Luma AI Dream Machine — cinematic video generation */
    LUMA_AI: "luma-ai",

    // Kling AI
    /** Kling — high-quality video generation */
    KLING: "kling",

    // AnimateDiff (Lightricks)
    /** AnimateDiff — animation from images */
    ANIMATE_DIFF: "animate-diff",

    // Tongyi Wanxiang (Alibaba)
    /** Tongyi Wanxiang — Alibaba video generation */
    TONGYI: "tongyi",
  },
} as const;

/**
 * Type representing any valid model ID string in the SDK.
 * Derived from the Models constant object for full type safety.
 */
export type ModelId =
  | (typeof Models.Text)[keyof typeof Models.Text]
  | (typeof Models.Image)[keyof typeof Models.Image]
  | (typeof Models.Audio)[keyof typeof Models.Audio]
  | (typeof Models.Video)[keyof typeof Models.Video];
