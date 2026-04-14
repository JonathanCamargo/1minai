"""
Public model constants for the 1min.ai SDK.

Provides a discoverable `Models` class with nested domain inner classes
so developers can tab-complete model names without reading API docs.

Usage::

    from onemin import Models

    # Text generation
    model = Models.Text.GPT_4O
    model = Models.Text.CLAUDE_3_5_SONNET

    # Image generation
    model = Models.Image.MIDJOURNEY
    model = Models.Image.DALL_E_3

    # Audio
    model = Models.Audio.TTS_1
    model = Models.Audio.WHISPER_1

    # Video
    model = Models.Video.LUMA_AI

All values are plain strings — the exact model ID strings accepted by the
1min.ai API. No `.value` accessor needed. Works as dict keys and is
JSON-serializable.
"""


class Models:
    """
    Nested model constants grouped by domain.

    Each inner class corresponds to a 1min.ai capability domain.
    Values are plain strings matching the exact model IDs the API accepts.

    Domains:
        - Models.Text   — language models for chat, writing, summarization
        - Models.Image  — image generation and editing models
        - Models.Audio  — text-to-speech, speech-to-text, and music generation
        - Models.Video  — video generation models
    """

    class Text:
        """
        Language models for text generation, chat, and writing tasks.

        These model IDs are accepted by the ``text`` and ``conversation``
        resource methods (``generate``, ``chat``, ``summarize``, ``translate``,
        ``write``, etc.).

        Example::

            from onemin import Models, OneMinClient

            client = OneMinClient(api_key="...")
            result = client.text.generate(
                "Explain quantum entanglement",
                model=Models.Text.GPT_4O,
            )
        """

        # OpenAI
        GPT_4O = "gpt-4o"
        GPT_4O_MINI = "gpt-4o-mini"
        GPT_4_TURBO = "gpt-4-turbo"
        GPT_4 = "gpt-4"
        GPT_3_5_TURBO = "gpt-3.5-turbo"
        GPT_3_5_TURBO_16K = "gpt-3.5-5-turbo"
        O1 = "o1"
        O1_MINI = "o1-mini"
        O3_MINI = "o3-mini"

        # Anthropic
        CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
        CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
        CLAUDE_3_OPUS = "claude-3-opus-20240229"
        CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
        CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

        # Google
        GEMINI_1_5_PRO = "gemini-1.5-pro"
        GEMINI_1_5_FLASH = "gemini-1.5-flash"
        GEMINI_2_0_FLASH = "gemini-2.0-flash"
        GEMINI_PRO = "gemini-pro"

        # Mistral
        MISTRAL_LARGE = "mistral-large-latest"
        MISTRAL_SMALL = "mistral-small-latest"
        MISTRAL_NEMO = "mistral-nemo"
        PIXTRAL_12B = "pixtral-12b"
        MIXTRAL_8X22B = "open-mixtral-8x22b"
        MIXTRAL_8X7B = "open-mixtral-8x7b"
        MISTRAL_7B = "open-mistral-7b"

        # Meta / Llama
        LLAMA_3_1_405B = "meta/meta-llama-3.1-405b-instruct"
        LLAMA_3_70B = "meta/meta-llama-3-70b-instruct"
        LLAMA_2_70B = "meta/llama-2-70b-chat"

        # Cohere
        COMMAND_R_PLUS = "command-r-plus"
        COMMAND_R = "command-r"
        COMMAND = "command"

        # DeepSeek
        DEEPSEEK_CHAT = "deepseek-chat"

        # xAI
        GROK_2 = "grok-2"

    class Image:
        """
        Image generation and editing models.

        Generation models are accepted by ``client.image.generate()``.
        Editing operation model selection is typically handled automatically
        by the operation type (e.g., ``remove_background`` uses ``stable-image``).

        Example::

            from onemin import Models, OneMinClient

            client = OneMinClient(api_key="...")
            result = client.image.generate(
                "A photorealistic cat on a mountain",
                model=Models.Image.MIDJOURNEY,
            )
        """

        # Midjourney (UUID — required by the 1min.ai API)
        MIDJOURNEY = "5c232a9e-9061-4777-980a-ddc8e65647c6"

        # OpenAI
        DALL_E_3 = "dall-e-3"
        DALL_E_2 = "dall-e-2"

        # Stability AI
        STABLE_DIFFUSION_XL = "stable-diffusion-xl-1024-v1-0"
        STABLE_DIFFUSION_768 = "stable-diffusion-v1-6"
        STABLE_IMAGE = "stable-image"  # used by editing operations

        # Leonardo AI
        LEONARDO_PHOENIX = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"
        LEONARDO_VISION_XL = "5c232a9e-9061-4777-980a-ddc8e65647c6"
        LEONARDO_DIFFUSION_XL = "1e60896f-3c26-4296-8ecc-53e2afecc132"
        LEONARDO_KINO_XL = "aa77f04e-3eec-4034-9c07-d0f619684628"
        LEONARDO_ANIME_XL = "e71a1c2f-4f80-4800-934f-2c68979d1cc6"

        # Flux (Black Forest Labs)
        FLUX_SCHNELL = "flux/schnell"
        FLUX_DEV = "flux/dev"
        FLUX_PRO = "flux/pro"
        FLUX_PRO_1_1 = "flux/pro/v1.1"

        # Ideogram
        IDEOGRAM_V2 = "ideogram-v2"
        IDEOGRAM_V2_TURBO = "ideogram-v2-turbo"

        # Recraft
        RECRAFT_V3 = "recraftv3"

        # Google
        IMAGEN_3 = "imagen-3.0-generate-002"

        # Editing operations (used internally by image resource methods)
        CLIPDROP = "clipdrop"  # background replacer, text remover
        QUBICO_IMAGE_TOOLKIT = "Qubico/image-toolkit"  # face swapper

    class Audio:
        """
        Text-to-speech, speech-to-text, and music generation models.

        TTS models are accepted by ``client.audio.text_to_speech()``.
        STT models are accepted by ``client.audio.speech_to_text()``.
        Music models are accepted by ``client.audio.generate_music()``.

        Example::

            from onemin import Models, OneMinClient

            client = OneMinClient(api_key="...")
            result = client.audio.text_to_speech(
                "Hello, world!",
                model=Models.Audio.TTS_1_HD,
            )
        """

        # OpenAI — Text-to-Speech
        TTS_1 = "tts-1"
        TTS_1_HD = "tts-1-hd"

        # ElevenLabs — Text-to-Speech
        ELEVENLABS_TTS = "elevenlabs-tts"

        # Google — Text-to-Speech
        GOOGLE_TTS = "google-tts"

        # OpenAI — Speech-to-Text
        WHISPER_1 = "whisper-1"

        # Music generation
        SUNO = "music-s"   # Suno AI music generation
        UDIO = "music-u"   # Udio music generation

    class Video:
        """
        Video generation models.

        Accepted by ``client.video.generate()``.

        Example::

            from onemin import Models, OneMinClient

            client = OneMinClient(api_key="...")
            result = client.video.generate(
                "A time-lapse of a blooming flower",
                model=Models.Video.LUMA_AI,
            )
        """

        # Luma AI
        LUMA_AI = "luma-ai"

        # Kling AI
        KLING = "kling"

        # AnimateDiff (Lightricks)
        ANIMATE_DIFF = "animate-diff"

        # Tongyi Wanxiang (Alibaba)
        TONGYI = "tongyi"
