"""Generated model constants for the 1min.ai Python SDK.

DO NOT EDIT. Regenerate with ``python scripts/sync_models.py``.
Source of truth: ``data/models.json``.
"""

from __future__ import annotations


class Models:
    """Model identifiers grouped by capability domain."""

    class Text:
        """Text models -- UNIFY_CHAT_WITH_AI via /api/chat-with-ai."""

        GPT_4O = "gpt-4o"
        GPT_4O_MINI = "gpt-4o-mini"
        GPT_4_TURBO = "gpt-4-turbo"
        GPT_3_5_TURBO = "gpt-3.5-turbo"
        O3_MINI = "o3-mini"
        GEMINI_2_5_FLASH = "gemini-2.5-flash"
        MISTRAL_LARGE = "mistral-large-latest"
        MISTRAL_SMALL = "mistral-small-latest"
        LLAMA_3_70B = "meta/meta-llama-3-70b-instruct"
        QWEN3_7_PLUS = "qwen3.7-plus"
        QWEN3_7_MAX = "qwen3.7-max"
        QWEN3_7_FLASH = "qwen3.7-flash"
        QWEN3_6_PLUS = "qwen3.6-plus"
        QWEN3_6_MAX_PREVIEW = "qwen3.6-max-preview"
        QWEN3_6_FLASH = "qwen3.6-flash"
        QWEN3_VL_PLUS = "qwen3-vl-plus"
        QWEN3_VL_FLASH = "qwen3-vl-flash"
        QWEN3_VL_8B_THINKING = "qwen3-vl-8b-thinking"
        QWEN3_MAX = "qwen3-max"
        QWEN3_8B = "qwen3-8b"
        QWEN_VL_PLUS = "qwen-vl-plus"
        QWEN_VL_MAX = "qwen-vl-max"
        QWEN_PLUS = "qwen-plus"
        QWEN_MAX = "qwen-max"
        QWEN_FLASH = "qwen-flash"
        CLAUDE_SONNET_5 = "us.anthropic.claude-sonnet-5"
        CLAUDE_SONNET_4_6 = "us.anthropic.claude-sonnet-4-6"
        CLAUDE_SONNET_4_5_20250929 = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        CLAUDE_OPUS_5_5 = "us.anthropic.claude-opus-5-5"
        CLAUDE_OPUS_5 = "us.anthropic.claude-opus-5"
        CLAUDE_OPUS_4_8 = "us.anthropic.claude-opus-4-8"
        CLAUDE_OPUS_4_7 = "us.anthropic.claude-opus-4-7"
        CLAUDE_OPUS_4_6 = "us.anthropic.claude-opus-4-6-v1"
        CLAUDE_OPUS_4_5_20251101 = "us.anthropic.claude-opus-4-5-20251101-v1:0"
        CLAUDE_HAIKU_4_5_20251001 = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        CLAUDE_FABLE_5_1 = "us.anthropic.claude-fable-5-1"
        CLAUDE_FABLE_5 = "us.anthropic.claude-fable-5"
        COMMAND_R_08_2024 = "command-r-08-2024"
        DEEPSEEK_V4_PRO = "deepseek-v4-pro"
        DEEPSEEK_FLASH = "deepseek-flash"
        GEMINI_3_8_FLASH = "gemini-3.8-flash"
        GEMINI_3_7_FLASH = "gemini-3.7-flash"
        GEMINI_3_6_FLASH = "gemini-3.6-flash"
        GEMINI_3_5_FLASH = "gemini-3.5-flash"
        GEMINI_3_1_PRO_PREVIEW = "gemini-3.1-pro-preview"
        GEMINI_3_1_FLASH_LITE_PREVIEW = "gemini-3.1-flash-lite-preview"
        GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
        GEMINI_2_5_PRO = "gemini-2.5-pro"
        LLAMA_4_MAVERICK_INSTRUCT = "meta/llama-4-maverick-instruct"
        MAGISTRAL_SMALL_LATEST = "magistral-small-latest"
        MAGISTRAL_MEDIUM_LATEST = "magistral-medium-latest"
        MINISTRAL_14B_LATEST = "ministral-14b-latest"
        OPEN_MISTRAL_NEMO = "open-mistral-nemo"
        MISTRAL_SMALL_2603 = "mistral-small-2603"
        MISTRAL_MEDIUM_LATEST = "mistral-medium-latest"
        MISTRAL_MEDIUM_3_5 = "mistral-medium-3-5"
        MISTRAL_LARGE_2512 = "mistral-large-2512"
        GPT_5_3_CODEX = "gpt-5.3-codex"
        GPT_6_1_SOL = "gpt-6.1-sol"
        GPT_6_SOL = "gpt-6-sol"
        GPT_6_LUNA = "gpt-6-luna"
        GPT_6_ASTRA = "gpt-6-astra"
        GPT_5_6_TERRA = "gpt-5.6-terra"
        GPT_5_6_SOL = "gpt-5.6-sol"
        GPT_5_6_LUNA = "gpt-5.6-luna"
        GPT_5_5_PRO = "gpt-5.5-pro"
        GPT_5_5 = "gpt-5.5"
        GPT_5_4_PRO = "gpt-5.4-pro"
        GPT_5_4_NANO = "gpt-5.4-nano"
        GPT_5_4_MINI = "gpt-5.4-mini"
        GPT_5_4 = "gpt-5.4"
        GPT_5_2_PRO = "gpt-5.2-pro"
        GPT_5_2 = "gpt-5.2"
        GPT_5_1 = "gpt-5.1"
        GPT_5_NANO = "gpt-5-nano"
        GPT_5_MINI = "gpt-5-mini"
        GPT_5 = "gpt-5"
        GPT_4_1_NANO = "gpt-4.1-nano"
        GPT_4_1_MINI = "gpt-4.1-mini"
        GPT_4_1 = "gpt-4.1"
        GPT_OSS_20B = "openai/gpt-oss-20b"
        GPT_OSS_120B = "openai/gpt-oss-120b"
        O3_PRO = "o3-pro"
        O3 = "o3"
        KIMI_K3 = "moonshotai/kimi-k3"
        KIMI_K2_7_CODE = "moonshotai/kimi-k2.7-code"
        KIMI_K2_6 = "moonshotai/kimi-k2.6"
        MUSE_SPARK_1_3 = "meta/muse-spark-1.3"
        MUSE_SPARK_1_2 = "meta/muse-spark-1.2"
        MUSE_SPARK_1_1 = "meta/muse-spark-1.1"
        SONAR_REASONING_PRO = "sonar-reasoning-pro"
        SONAR_PRO = "sonar-pro"
        SONAR_DEEP_RESEARCH = "sonar-deep-research"
        SONAR = "sonar"
        GROK_4_7 = "grok-4.7"
        GROK_4_6 = "grok-4.6"
        GROK_4_5 = "grok-4.5"
        GROK_4_3 = "grok-4.3"
        GLM_5_3 = "glm-5.3"
        GLM_5_2 = "glm-5.2"
        GLM_5_1 = "glm-5.1"
        GLM_5 = "glm-5"

    class Image:
        """Image models -- IMAGE_GENERATOR via /api/features."""

        MIDJOURNEY = "5c232a9e-9061-4777-980a-ddc8e65647c6"
        STABLE_DIFFUSION_XL = "stable-diffusion-xl-1024-v1-0"
        STABLE_IMAGE = "stable-image"
        LEONARDO_DIFFUSION_XL = "1e60896f-3c26-4296-8ecc-53e2afecc132"
        LEONARDO_KINO_XL = "aa77f04e-3eec-4034-9c07-d0f619684628"
        QWEN_IMAGE_PLUS = "qwen-image-plus"
        QWEN_IMAGE_MAX = "qwen-image-max"
        FLUX_SCHNELL_LORA = "black-forest-labs/flux-schnell-lora"
        FLUX_KREA_DEV = "black-forest-labs/flux-krea-dev"
        FLUX_DEV_LORA = "black-forest-labs/flux-dev-lora"
        FLUX_DEV = "black-forest-labs/flux-dev"
        FLUX_2_PRO = "black-forest-labs/flux-2-pro"
        FLUX_2_MAX = "black-forest-labs/flux-2-max"
        FLUX_2_KLEIN_9B = "black-forest-labs/flux-2-klein-9b"
        FLUX_2_KLEIN_4B = "black-forest-labs/flux-2-klein-4b"
        FLUX_2_FLEX = "black-forest-labs/flux-2-flex"
        FLUX_2_DEV = "black-forest-labs/flux-2-dev"
        FLUX_1_1_PRO_ULTRA = "black-forest-labs/flux-1.1-pro-ultra"
        FLUX_1_1_PRO = "black-forest-labs/flux-1.1-pro"
        DZINE = "dzine"
        GEMINI_3_1_FLASH_IMAGE_PREVIEW = "gemini-3.1-flash-image-preview"
        GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"
        GEMINI_2_5_FLASH_IMAGE = "gemini-2.5-flash-image"
        IDEOGRAM_3 = "ideogram-3"
        LEONARDO_ANIME_XL_LEONARDOAI = "e71a1c2f-4f80-4800-934f-2c68979d8cc8"
        LEONARDO_LIGHTNING_XL_LEONARDOAI = "b24e16ff-06e3-43eb-8d33-4416c2d75876"
        LEONARDO_PHOENIX_LEONARDOAI = "6b645e3a-d64f-4341-a6d8-7a3690fbf042"
        LEONARDO_ALBEDOBASE_XL_LEONARDOAI = "2067ae52-33fd-4a82-bb92-c2c55e7d2786"
        MAGIC_ART_7_0 = "magic-art_7_0"
        MAGIC_ART_6_1 = "magic-art_6_1"
        MAGIC_ART = "magic-art"
        GPT_IMAGE_2 = "gpt-image-2"
        GPT_IMAGE_1_MINI = "gpt-image-1-mini"
        GPT_IMAGE_1 = "gpt-image-1"
        RECRAFT = "recraft"
        STABLE_IMAGE_ULTRA = "stable-image-ultra"
        SD3_5_MEDIUM = "sd3.5-medium"
        SD3_5_LARGE_TURBO = "sd3.5-large-turbo"
        SD3_5_LARGE = "sd3.5-large"
        SD3_5_FLASH = "sd3.5-flash"
        GROK_IMAGINE_IMAGE = "grok-imagine-image"
        IMG2PROMPT = "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5"
        FLUX_REDUX_SCHNELL = "black-forest-labs/flux-redux-schnell"
        FLUX_REDUX_DEV = "black-forest-labs/flux-redux-dev"
        CLIPDROP = "clipdrop"
        QWEN_IMAGE_EDIT_PLUS = "qwen-image-edit-plus"
        FLUX_KONTEXT_PRO = "black-forest-labs/flux-kontext-pro"
        FLUX_KONTEXT_MAX = "black-forest-labs/flux-kontext-max"
        FLUX_KONTEXT_DEV_LORA = "black-forest-labs/flux-kontext-dev-lora"
        FLUX_KONTEXT_DEV = "black-forest-labs/flux-kontext-dev"
        FLUX_DEPTH_PRO = "black-forest-labs/flux-depth-pro"
        FLUX_DEPTH_DEV = "black-forest-labs/flux-depth-dev"
        FLUX_CANNY_PRO = "black-forest-labs/flux-canny-pro"
        FLUX_CANNY_DEV = "black-forest-labs/flux-canny-dev"
        FLUX_FILL_PRO = "black-forest-labs/flux-fill-pro"
        FLUX_FILL_DEV = "black-forest-labs/flux-fill-dev"
        ERASER = "bria/eraser"
        IMAGE_TOOLKIT = "Qubico/image-toolkit"
        TRELLIS = "Qubico/trellis"

    class Audio:
        """Audio models -- TEXT_TO_SPEECH via /api/features."""

        TTS_1 = "tts-1"
        TTS_1_HD = "tts-1-hd"
        ELEVENLABS_TTS = "elevenlabs-tts"
        GOOGLE_TTS = "google-tts"
        WHISPER_1 = "whisper-1"
        UDIO = "music-u"
        QWEN3_TTS_FLASH = "qwen3-tts-flash"
        QWEN3_ASR_FLASH = "qwen3-asr-flash"
        ELEVENLABS_SPEECH_TO_TEXT = "elevenlabs-speech-to-text"
        TELEPHONY_SHORT = "telephony_short"
        TELEPHONY = "telephony"
        PHONE_CALL = "phone_call"
        MEDICAL_DICTATION = "medical_dictation"
        MEDICAL_CONVERSATION = "medical_conversation"
        LATEST_SHORT = "latest_short"
        LATEST_LONG = "latest_long"
        GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"
        GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
        ELEVENLABS_MUSIC = "elevenlabs-music-v1"
        LYRIA_3_PRO_PREVIEW = "lyria-3-pro-preview"
        LYRIA_3_CLIP_PREVIEW = "lyria-3-clip-preview"
        LYRIA_002 = "lyria-002"
        MUSICGEN = "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb"
        SUNO_TTAPI = "suno-ttapi"
        QWEN3_LIVETRANSLATE_FLASH = "qwen3-livetranslate-flash"
        GEMINI_3_8_FLASH = "gemini-3.8-flash"
        GEMINI_3_7_FLASH = "gemini-3.7-flash"
        GEMINI_3_6_FLASH = "gemini-3.6-flash"
        GEMINI_3_5_FLASH = "gemini-3.5-flash"
        GEMINI_3_1_PRO_PREVIEW = "gemini-3.1-pro-preview"
        GEMINI_3_1_FLASH_LITE_PREVIEW = "gemini-3.1-flash-lite-preview"
        GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
        GEMINI_2_5_PRO = "gemini-2.5-pro"
        GEMINI_2_5_FLASH = "gemini-2.5-flash"

    class Video:
        """Video models -- TEXT_TO_VIDEO via /api/features."""

        KLING = "kling"
        DAMO_TEXT_TO_VIDEO = "cjwbw/damo-text-to-video:1e205ea73084bd17a0a3b43396e49ba0d6bc2e754e9283b2df49fad2dcf95755"
        WAN2_7_T2V = "wan2.7-t2v"
        PIKA = "pika"
        SEEDANCE_2_5 = "bytedance/seedance-2.5"
        SEEDANCE_2_0_MINI = "bytedance/seedance-2.0-mini"
        SEEDANCE_2_0_FAST = "bytedance/seedance-2.0-fast"
        SEEDANCE_2_0 = "bytedance/seedance-2.0"
        VEO3_VIDEO = "veo3-video"
        HAILUO = "hailuo"
        HUNYUAN = "Qubico/hunyuan"
        WANX = "Qubico/wanx"
        ANIMATE_DIFF = "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f"
        WAN2_7_I2V = "wan2.7-i2v"
        SKYREELS = "Qubico/skyreels"


MODEL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "text": [
        {
            "constant": "GPT_4O",
            "id": "gpt-4o",
            "provider": "openai",
            "label": "GPT-4o",
        },
        {
            "constant": "GPT_4O_MINI",
            "id": "gpt-4o-mini",
            "provider": "openai",
            "label": "GPT-4o Mini",
        },
        {
            "constant": "GPT_4_TURBO",
            "id": "gpt-4-turbo",
            "provider": "openai",
            "label": "GPT-4 Turbo",
        },
        {
            "constant": "GPT_3_5_TURBO",
            "id": "gpt-3.5-turbo",
            "provider": "openai",
            "label": "GPT-3.5 Turbo",
        },
        {
            "constant": "O3_MINI",
            "id": "o3-mini",
            "provider": "openai",
            "label": "o3 Mini",
        },
        {
            "constant": "GEMINI_2_5_FLASH",
            "id": "gemini-2.5-flash",
            "provider": "google",
            "label": "Gemini 2.5 Flash",
        },
        {
            "constant": "MISTRAL_LARGE",
            "id": "mistral-large-latest",
            "provider": "mistral",
            "label": "Mistral Large",
        },
        {
            "constant": "MISTRAL_SMALL",
            "id": "mistral-small-latest",
            "provider": "mistral",
            "label": "Mistral Small",
        },
        {
            "constant": "LLAMA_3_70B",
            "id": "meta/meta-llama-3-70b-instruct",
            "provider": "meta",
            "label": "Llama 3 70B Instruct",
        },
        {
            "constant": "QWEN3_7_PLUS",
            "id": "qwen3.7-plus",
            "provider": "alibaba",
            "label": "Qwen 3.7 Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_7_MAX",
            "id": "qwen3.7-max",
            "provider": "alibaba",
            "label": "Qwen 3.7 Max - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_7_FLASH",
            "id": "qwen3.7-flash",
            "provider": "alibaba",
            "label": "Qwen 3.7 Flash - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_6_PLUS",
            "id": "qwen3.6-plus",
            "provider": "alibaba",
            "label": "Qwen 3.6 Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_6_MAX_PREVIEW",
            "id": "qwen3.6-max-preview",
            "provider": "alibaba",
            "label": "Qwen 3.6 Max Preview - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_6_FLASH",
            "id": "qwen3.6-flash",
            "provider": "alibaba",
            "label": "Qwen 3.6 Flash - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_VL_PLUS",
            "id": "qwen3-vl-plus",
            "provider": "alibaba",
            "label": "Qwen3 VL Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_VL_FLASH",
            "id": "qwen3-vl-flash",
            "provider": "alibaba",
            "label": "Qwen3 VL Flash - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_VL_8B_THINKING",
            "id": "qwen3-vl-8b-thinking",
            "provider": "alibaba",
            "label": "Qwen3 VL 8B Thinking",
        },
        {
            "constant": "QWEN3_MAX",
            "id": "qwen3-max",
            "provider": "alibaba",
            "label": "Qwen3 Max - Alibaba Cloud",
        },
        {
            "constant": "QWEN3_8B",
            "id": "qwen3-8b",
            "provider": "alibaba",
            "label": "Qwen3 8B",
        },
        {
            "constant": "QWEN_VL_PLUS",
            "id": "qwen-vl-plus",
            "provider": "alibaba",
            "label": "Qwen VL Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN_VL_MAX",
            "id": "qwen-vl-max",
            "provider": "alibaba",
            "label": "Qwen VL Max - Alibaba Cloud",
        },
        {
            "constant": "QWEN_PLUS",
            "id": "qwen-plus",
            "provider": "alibaba",
            "label": "Qwen Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN_MAX",
            "id": "qwen-max",
            "provider": "alibaba",
            "label": "Qwen Max - Alibaba Cloud",
        },
        {
            "constant": "QWEN_FLASH",
            "id": "qwen-flash",
            "provider": "alibaba",
            "label": "Qwen Flash - Alibaba Cloud",
        },
        {
            "constant": "CLAUDE_SONNET_5",
            "id": "us.anthropic.claude-sonnet-5",
            "provider": "aws-bedrock",
            "label": "Claude 5 Sonnet - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_SONNET_4_6",
            "id": "us.anthropic.claude-sonnet-4-6",
            "provider": "aws-bedrock",
            "label": "Claude 4.6 Sonnet - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_SONNET_4_5_20250929",
            "id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "provider": "aws-bedrock",
            "label": "Claude 4.5 Sonnet - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_5_5",
            "id": "us.anthropic.claude-opus-5-5",
            "provider": "aws-bedrock",
            "label": "Claude 5.5 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_5",
            "id": "us.anthropic.claude-opus-5",
            "provider": "aws-bedrock",
            "label": "Claude 5 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_4_8",
            "id": "us.anthropic.claude-opus-4-8",
            "provider": "aws-bedrock",
            "label": "Claude 4.8 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_4_7",
            "id": "us.anthropic.claude-opus-4-7",
            "provider": "aws-bedrock",
            "label": "Claude 4.7 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_4_6",
            "id": "us.anthropic.claude-opus-4-6-v1",
            "provider": "aws-bedrock",
            "label": "Claude 4.6 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_OPUS_4_5_20251101",
            "id": "us.anthropic.claude-opus-4-5-20251101-v1:0",
            "provider": "aws-bedrock",
            "label": "Claude 4.5 Opus - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_HAIKU_4_5_20251001",
            "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider": "aws-bedrock",
            "label": "Claude 4.5 Haiku - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_FABLE_5_1",
            "id": "us.anthropic.claude-fable-5-1",
            "provider": "aws-bedrock",
            "label": "Claude 5.1 Fable - AWS Bedrock US",
        },
        {
            "constant": "CLAUDE_FABLE_5",
            "id": "us.anthropic.claude-fable-5",
            "provider": "aws-bedrock",
            "label": "Claude 5 Fable - AWS Bedrock US",
        },
        {
            "constant": "COMMAND_R_08_2024",
            "id": "command-r-08-2024",
            "provider": "cohere",
            "label": "Command R - Cohere",
        },
        {
            "constant": "DEEPSEEK_V4_PRO",
            "id": "deepseek-v4-pro",
            "provider": "deepseek",
            "label": "DeepSeek V4 Pro",
        },
        {
            "constant": "DEEPSEEK_FLASH",
            "id": "deepseek-flash",
            "provider": "deepseek",
            "label": "DeepSeek V4.1 Flash",
        },
        {
            "constant": "GEMINI_3_8_FLASH",
            "id": "gemini-3.8-flash",
            "provider": "googleai",
            "label": "Gemini 3.8 Flash - GoogleAI",
        },
        {
            "constant": "GEMINI_3_7_FLASH",
            "id": "gemini-3.7-flash",
            "provider": "googleai",
            "label": "Gemini 3.7 Flash - GoogleAI",
        },
        {
            "constant": "GEMINI_3_6_FLASH",
            "id": "gemini-3.6-flash",
            "provider": "googleai",
            "label": "Gemini 3.6 Flash - GoogleAI",
        },
        {
            "constant": "GEMINI_3_5_FLASH",
            "id": "gemini-3.5-flash",
            "provider": "googleai",
            "label": "Gemini 3.5 Flash - GoogleAI",
        },
        {
            "constant": "GEMINI_3_1_PRO_PREVIEW",
            "id": "gemini-3.1-pro-preview",
            "provider": "googleai",
            "label": "Gemini 3.1 Pro - GoogleAI",
        },
        {
            "constant": "GEMINI_3_1_FLASH_LITE_PREVIEW",
            "id": "gemini-3.1-flash-lite-preview",
            "provider": "googleai",
            "label": "Gemini 3.1 Flash Lite - GoogleAI",
        },
        {
            "constant": "GEMINI_3_FLASH_PREVIEW",
            "id": "gemini-3-flash-preview",
            "provider": "googleai",
            "label": "Gemini 3 Flash - GoogleAI",
        },
        {
            "constant": "GEMINI_2_5_PRO",
            "id": "gemini-2.5-pro",
            "provider": "googleai",
            "label": "Gemini 2.5 Pro -  GoogleAI",
        },
        {
            "constant": "LLAMA_4_MAVERICK_INSTRUCT",
            "id": "meta/llama-4-maverick-instruct",
            "provider": "replicate",
            "label": "LLaMA 4 Maverick Instruct - MetaAI",
        },
        {
            "constant": "MAGISTRAL_SMALL_LATEST",
            "id": "magistral-small-latest",
            "provider": "mistralai",
            "label": "Magistral Small 1.2 - MistralAI",
        },
        {
            "constant": "MAGISTRAL_MEDIUM_LATEST",
            "id": "magistral-medium-latest",
            "provider": "mistralai",
            "label": "Magistral Medium 1.2 - MistralAI",
        },
        {
            "constant": "MINISTRAL_14B_LATEST",
            "id": "ministral-14b-latest",
            "provider": "mistralai",
            "label": "Ministral 14B Latest - MistralAI",
        },
        {
            "constant": "OPEN_MISTRAL_NEMO",
            "id": "open-mistral-nemo",
            "provider": "mistralai",
            "label": "Mistral Open Nemo - MistralAI",
        },
        {
            "constant": "MISTRAL_SMALL_2603",
            "id": "mistral-small-2603",
            "provider": "mistralai",
            "label": "Mistral Small 4 - MistralAI",
        },
        {
            "constant": "MISTRAL_MEDIUM_LATEST",
            "id": "mistral-medium-latest",
            "provider": "mistralai",
            "label": "Mistral Medium 3.1 - MistralAI",
        },
        {
            "constant": "MISTRAL_MEDIUM_3_5",
            "id": "mistral-medium-3-5",
            "provider": "mistralai",
            "label": "Mistral Medium 3.5 - MistralAI",
        },
        {
            "constant": "MISTRAL_LARGE_2512",
            "id": "mistral-large-2512",
            "provider": "mistralai",
            "label": "Mistral Large 3 - MistralAI",
        },
        {
            "constant": "GPT_5_3_CODEX",
            "id": "gpt-5.3-codex",
            "provider": "openai",
            "label": "GPT-5.3 Codex - OpenAI",
        },
        {
            "constant": "GPT_6_1_SOL",
            "id": "gpt-6.1-sol",
            "provider": "openai",
            "label": "GPT-6.1 Sol - OpenAI",
        },
        {
            "constant": "GPT_6_SOL",
            "id": "gpt-6-sol",
            "provider": "openai",
            "label": "GPT-6 Sol - OpenAI",
        },
        {
            "constant": "GPT_6_LUNA",
            "id": "gpt-6-luna",
            "provider": "openai",
            "label": "GPT-6 Luna - OpenAI",
        },
        {
            "constant": "GPT_6_ASTRA",
            "id": "gpt-6-astra",
            "provider": "openai",
            "label": "GPT-6 Astra - OpenAI",
        },
        {
            "constant": "GPT_5_6_TERRA",
            "id": "gpt-5.6-terra",
            "provider": "openai",
            "label": "GPT-5.6 Terra - OpenAI",
        },
        {
            "constant": "GPT_5_6_SOL",
            "id": "gpt-5.6-sol",
            "provider": "openai",
            "label": "GPT-5.6 Sol - OpenAI",
        },
        {
            "constant": "GPT_5_6_LUNA",
            "id": "gpt-5.6-luna",
            "provider": "openai",
            "label": "GPT-5.6 Luna - OpenAI",
        },
        {
            "constant": "GPT_5_5_PRO",
            "id": "gpt-5.5-pro",
            "provider": "openai",
            "label": "GPT-5.5 Pro - OpenAI",
        },
        {
            "constant": "GPT_5_5",
            "id": "gpt-5.5",
            "provider": "openai",
            "label": "GPT-5.5 - OpenAI",
        },
        {
            "constant": "GPT_5_4_PRO",
            "id": "gpt-5.4-pro",
            "provider": "openai",
            "label": "GPT-5.4 Pro - OpenAI",
        },
        {
            "constant": "GPT_5_4_NANO",
            "id": "gpt-5.4-nano",
            "provider": "openai",
            "label": "GPT-5.4 Nano - OpenAI",
        },
        {
            "constant": "GPT_5_4_MINI",
            "id": "gpt-5.4-mini",
            "provider": "openai",
            "label": "GPT-5.4 Mini - OpenAI",
        },
        {
            "constant": "GPT_5_4",
            "id": "gpt-5.4",
            "provider": "openai",
            "label": "GPT-5.4 - OpenAI",
        },
        {
            "constant": "GPT_5_2_PRO",
            "id": "gpt-5.2-pro",
            "provider": "openai",
            "label": "GPT-5.2 Pro - OpenAI",
        },
        {
            "constant": "GPT_5_2",
            "id": "gpt-5.2",
            "provider": "openai",
            "label": "GPT-5.2 - OpenAI",
        },
        {
            "constant": "GPT_5_1",
            "id": "gpt-5.1",
            "provider": "openai",
            "label": "GPT-5.1 - OpenAI",
        },
        {
            "constant": "GPT_5_NANO",
            "id": "gpt-5-nano",
            "provider": "openai",
            "label": "GPT-5 Nano - OpenAI",
        },
        {
            "constant": "GPT_5_MINI",
            "id": "gpt-5-mini",
            "provider": "openai",
            "label": "GPT-5 Mini - OpenAI",
        },
        {
            "constant": "GPT_5",
            "id": "gpt-5",
            "provider": "openai",
            "label": "GPT-5 - OpenAI",
        },
        {
            "constant": "GPT_4_1_NANO",
            "id": "gpt-4.1-nano",
            "provider": "openai",
            "label": "GPT-4.1 nano - OpenAI",
        },
        {
            "constant": "GPT_4_1_MINI",
            "id": "gpt-4.1-mini",
            "provider": "openai",
            "label": "GPT-4.1 mini - OpenAI",
        },
        {
            "constant": "GPT_4_1",
            "id": "gpt-4.1",
            "provider": "openai",
            "label": "GPT-4.1 - OpenAI",
        },
        {
            "constant": "GPT_OSS_20B",
            "id": "openai/gpt-oss-20b",
            "provider": "replicate",
            "label": "GPT OSS 20b - OpenAI",
        },
        {
            "constant": "GPT_OSS_120B",
            "id": "openai/gpt-oss-120b",
            "provider": "replicate",
            "label": "GPT OSS 120b - OpenAI",
        },
        {
            "constant": "O3_PRO",
            "id": "o3-pro",
            "provider": "openai",
            "label": "o3 Pro - OpenAI",
        },
        {
            "constant": "O3",
            "id": "o3",
            "provider": "openai",
            "label": "o3 - OpenAI",
        },
        {
            "constant": "KIMI_K3",
            "id": "moonshotai/kimi-k3",
            "provider": "openrouter",
            "label": "Kimi K3",
        },
        {
            "constant": "KIMI_K2_7_CODE",
            "id": "moonshotai/kimi-k2.7-code",
            "provider": "openrouter",
            "label": "Kimi K2.7 Code",
        },
        {
            "constant": "KIMI_K2_6",
            "id": "moonshotai/kimi-k2.6",
            "provider": "openrouter",
            "label": "Kimi K2.6",
        },
        {
            "constant": "MUSE_SPARK_1_3",
            "id": "meta/muse-spark-1.3",
            "provider": "openrouter",
            "label": "Muse Spark 1.3",
        },
        {
            "constant": "MUSE_SPARK_1_2",
            "id": "meta/muse-spark-1.2",
            "provider": "openrouter",
            "label": "Muse Spark 1.2",
        },
        {
            "constant": "MUSE_SPARK_1_1",
            "id": "meta/muse-spark-1.1",
            "provider": "openrouter",
            "label": "Muse Spark 1.1",
        },
        {
            "constant": "SONAR_REASONING_PRO",
            "id": "sonar-reasoning-pro",
            "provider": "perplexity",
            "label": "Perplexity [reasoning pro]",
        },
        {
            "constant": "SONAR_PRO",
            "id": "sonar-pro",
            "provider": "perplexity",
            "label": "Perplexity [pro]",
        },
        {
            "constant": "SONAR_DEEP_RESEARCH",
            "id": "sonar-deep-research",
            "provider": "perplexity",
            "label": "Perplexity [deep research]",
        },
        {
            "constant": "SONAR",
            "id": "sonar",
            "provider": "perplexity",
            "label": "Perplexity",
        },
        {
            "constant": "GROK_4_7",
            "id": "grok-4.7",
            "provider": "xai",
            "label": "xAI - Grok 4.7",
        },
        {
            "constant": "GROK_4_6",
            "id": "grok-4.6",
            "provider": "xai",
            "label": "xAI - Grok 4.6",
        },
        {
            "constant": "GROK_4_5",
            "id": "grok-4.5",
            "provider": "xai",
            "label": "xAI - Grok 4.5",
        },
        {
            "constant": "GROK_4_3",
            "id": "grok-4.3",
            "provider": "xai",
            "label": "xAI - Grok 4.3",
        },
        {
            "constant": "GLM_5_3",
            "id": "glm-5.3",
            "provider": "zai",
            "label": "GLM-5.3 - Z.AI",
        },
        {
            "constant": "GLM_5_2",
            "id": "glm-5.2",
            "provider": "zai",
            "label": "GLM-5.2 - Z.AI",
        },
        {
            "constant": "GLM_5_1",
            "id": "glm-5.1",
            "provider": "zai",
            "label": "GLM-5.1 - Z.AI",
        },
        {
            "constant": "GLM_5",
            "id": "glm-5",
            "provider": "zai",
            "label": "GLM-5 - Z.AI",
        },
    ],
    "image": [
        {
            "constant": "MIDJOURNEY",
            "id": "5c232a9e-9061-4777-980a-ddc8e65647c6",
            "provider": "midjourney",
            "label": "Midjourney",
            "tags": ["polled"],
        },
        {
            "constant": "STABLE_DIFFUSION_XL",
            "id": "stable-diffusion-xl-1024-v1-0",
            "provider": "stability",
            "label": "Stable Diffusion XL 1024",
        },
        {
            "constant": "STABLE_IMAGE",
            "id": "stable-image",
            "provider": "stability",
            "label": "Stable Image (editing)",
        },
        {
            "constant": "LEONARDO_DIFFUSION_XL",
            "id": "1e60896f-3c26-4296-8ecc-53e2afecc132",
            "provider": "leonardo",
            "label": "Leonardo Diffusion XL",
        },
        {
            "constant": "LEONARDO_KINO_XL",
            "id": "aa77f04e-3eec-4034-9c07-d0f619684628",
            "provider": "leonardo",
            "label": "Leonardo Kino XL",
        },
        {
            "constant": "QWEN_IMAGE_PLUS",
            "id": "qwen-image-plus",
            "provider": "alibaba",
            "label": "Qwen Image Plus - Alibaba Cloud",
        },
        {
            "constant": "QWEN_IMAGE_MAX",
            "id": "qwen-image-max",
            "provider": "alibaba",
            "label": "Qwen Image Max - Alibaba Cloud",
        },
        {
            "constant": "FLUX_SCHNELL_LORA",
            "id": "black-forest-labs/flux-schnell-lora",
            "provider": "replicate",
            "label": "Flux Schnell LoRA - Black Forest Labs",
        },
        {
            "constant": "FLUX_KREA_DEV",
            "id": "black-forest-labs/flux-krea-dev",
            "provider": "replicate",
            "label": "Flux Krea Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_DEV_LORA",
            "id": "black-forest-labs/flux-dev-lora",
            "provider": "replicate",
            "label": "Flux Dev LoRA - Black Forest Labs",
        },
        {
            "constant": "FLUX_DEV",
            "id": "black-forest-labs/flux-dev",
            "provider": "replicate",
            "label": "Flux Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_PRO",
            "id": "black-forest-labs/flux-2-pro",
            "provider": "replicate",
            "label": "Flux 2 Pro - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_MAX",
            "id": "black-forest-labs/flux-2-max",
            "provider": "replicate",
            "label": "Flux 2 Max - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_KLEIN_9B",
            "id": "black-forest-labs/flux-2-klein-9b",
            "provider": "replicate",
            "label": "Flux 2 Klein 9B - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_KLEIN_4B",
            "id": "black-forest-labs/flux-2-klein-4b",
            "provider": "replicate",
            "label": "Flux 2 Klein 4B - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_FLEX",
            "id": "black-forest-labs/flux-2-flex",
            "provider": "replicate",
            "label": "Flux 2 Flex - Black Forest Labs",
        },
        {
            "constant": "FLUX_2_DEV",
            "id": "black-forest-labs/flux-2-dev",
            "provider": "replicate",
            "label": "Flux 2 Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_1_1_PRO_ULTRA",
            "id": "black-forest-labs/flux-1.1-pro-ultra",
            "provider": "replicate",
            "label": "Flux 1.1 Pro Ultra - Black Forest Labs",
        },
        {
            "constant": "FLUX_1_1_PRO",
            "id": "black-forest-labs/flux-1.1-pro",
            "provider": "replicate",
            "label": "Flux Pro 1.1 - Black Forest Labs",
        },
        {
            "constant": "DZINE",
            "id": "dzine",
            "provider": "dzine",
            "label": "Dzine AI",
        },
        {
            "constant": "GEMINI_3_1_FLASH_IMAGE_PREVIEW",
            "id": "gemini-3.1-flash-image-preview",
            "provider": "googleai",
            "label": "Gemini 3.1 Flash Image (Nano Banana 2) - GoogleAI",
        },
        {
            "constant": "GEMINI_3_PRO_IMAGE_PREVIEW",
            "id": "gemini-3-pro-image-preview",
            "provider": "googleai",
            "label": "Gemini 3 Pro Image Preview - GoogleAI",
        },
        {
            "constant": "GEMINI_2_5_FLASH_IMAGE",
            "id": "gemini-2.5-flash-image",
            "provider": "googleai",
            "label": "Gemini 2.5 Flash Image (Nano Banana) - GoogleAI",
        },
        {
            "constant": "IDEOGRAM_3",
            "id": "ideogram-3",
            "provider": "ideogram",
            "label": "Ideogram 3.0",
        },
        {
            "constant": "LEONARDO_ANIME_XL_LEONARDOAI",
            "id": "e71a1c2f-4f80-4800-934f-2c68979d8cc8",
            "provider": "leonardoai",
            "label": "Leonardo Anime XL - LeonardoAI",
        },
        {
            "constant": "LEONARDO_LIGHTNING_XL_LEONARDOAI",
            "id": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
            "provider": "leonardoai",
            "label": "Leonardo Lightning XL - LeonardoAI",
        },
        {
            "constant": "LEONARDO_PHOENIX_LEONARDOAI",
            "id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",
            "provider": "leonardoai",
            "label": "Leonardo Phoenix - LeonardoAI",
        },
        {
            "constant": "LEONARDO_ALBEDOBASE_XL_LEONARDOAI",
            "id": "2067ae52-33fd-4a82-bb92-c2c55e7d2786",
            "provider": "leonardoai",
            "label": "Leonardo AlbedoBase XL - LeonardoAI",
        },
        {
            "constant": "MAGIC_ART_7_0",
            "id": "magic-art_7_0",
            "provider": "ttapi",
            "label": "Magic Art 7.0",
        },
        {
            "constant": "MAGIC_ART_6_1",
            "id": "magic-art_6_1",
            "provider": "ttapi",
            "label": "Magic Art 6.1",
        },
        {
            "constant": "MAGIC_ART",
            "id": "magic-art",
            "provider": "ttapi",
            "label": "Magic Art 5.2",
        },
        {
            "constant": "GPT_IMAGE_2",
            "id": "gpt-image-2",
            "provider": "openai",
            "label": "GPT Image 2 - OpenAI",
        },
        {
            "constant": "GPT_IMAGE_1_MINI",
            "id": "gpt-image-1-mini",
            "provider": "openai",
            "label": "GPT Image 1 Mini - OpenAI",
        },
        {
            "constant": "GPT_IMAGE_1",
            "id": "gpt-image-1",
            "provider": "openai",
            "label": "GPT Image 1 - OpenAI",
        },
        {
            "constant": "RECRAFT",
            "id": "recraft",
            "provider": "recraft",
            "label": "Recraft",
        },
        {
            "constant": "STABLE_IMAGE_ULTRA",
            "id": "stable-image-ultra",
            "provider": "stabilityai",
            "label": "Stable Image Ultra - StabilityAI",
        },
        {
            "constant": "SD3_5_MEDIUM",
            "id": "sd3.5-medium",
            "provider": "stabilityai",
            "label": "Stable Diffusion 3.5 Medium - StabilityAI",
        },
        {
            "constant": "SD3_5_LARGE_TURBO",
            "id": "sd3.5-large-turbo",
            "provider": "stabilityai",
            "label": "Stable Diffusion 3.5 Large Turbo - StabilityAI",
        },
        {
            "constant": "SD3_5_LARGE",
            "id": "sd3.5-large",
            "provider": "stabilityai",
            "label": "Stable Diffusion 3.5 Large - StabilityAI",
        },
        {
            "constant": "SD3_5_FLASH",
            "id": "sd3.5-flash",
            "provider": "stabilityai",
            "label": "Stable Diffusion 3.5 Flash - StabilityAI",
        },
        {
            "constant": "GROK_IMAGINE_IMAGE",
            "id": "grok-imagine-image",
            "provider": "xai",
            "label": "xAI - Grok Imagine Image",
        },
        {
            "constant": "IMG2PROMPT",
            "id": "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5",
            "provider": "replicate",
            "label": "Stable Diffusion - StabilityAI",
        },
        {
            "constant": "FLUX_REDUX_SCHNELL",
            "id": "black-forest-labs/flux-redux-schnell",
            "provider": "replicate",
            "label": "Flux Redux Schnell - Black Forest Labs",
        },
        {
            "constant": "FLUX_REDUX_DEV",
            "id": "black-forest-labs/flux-redux-dev",
            "provider": "replicate",
            "label": "Flux Redux Dev - Black Forest Labs",
        },
        {
            "constant": "CLIPDROP",
            "id": "clipdrop",
            "provider": "clipdrop",
            "label": "Stable Diffusion XL - StabilityAI",
        },
        {
            "constant": "QWEN_IMAGE_EDIT_PLUS",
            "id": "qwen-image-edit-plus",
            "provider": "alibaba",
            "label": "Qwen Image Edit Plus - Alibaba Cloud",
        },
        {
            "constant": "FLUX_KONTEXT_PRO",
            "id": "black-forest-labs/flux-kontext-pro",
            "provider": "replicate",
            "label": "Flux Kontext Pro - Black Forest Labs",
        },
        {
            "constant": "FLUX_KONTEXT_MAX",
            "id": "black-forest-labs/flux-kontext-max",
            "provider": "replicate",
            "label": "Flux Kontext Max - Black Forest Labs",
        },
        {
            "constant": "FLUX_KONTEXT_DEV_LORA",
            "id": "black-forest-labs/flux-kontext-dev-lora",
            "provider": "replicate",
            "label": "Flux Kontext Dev LoRA - Black Forest Labs",
        },
        {
            "constant": "FLUX_KONTEXT_DEV",
            "id": "black-forest-labs/flux-kontext-dev",
            "provider": "replicate",
            "label": "Flux Kontext Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_DEPTH_PRO",
            "id": "black-forest-labs/flux-depth-pro",
            "provider": "replicate",
            "label": "Flux Depth Pro - Black Forest Labs",
        },
        {
            "constant": "FLUX_DEPTH_DEV",
            "id": "black-forest-labs/flux-depth-dev",
            "provider": "replicate",
            "label": "Flux Depth Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_CANNY_PRO",
            "id": "black-forest-labs/flux-canny-pro",
            "provider": "replicate",
            "label": "Flux Canny Pro - Black Forest Labs",
        },
        {
            "constant": "FLUX_CANNY_DEV",
            "id": "black-forest-labs/flux-canny-dev",
            "provider": "replicate",
            "label": "Flux Canny Dev - Black Forest Labs",
        },
        {
            "constant": "FLUX_FILL_PRO",
            "id": "black-forest-labs/flux-fill-pro",
            "provider": "replicate",
            "label": "Flux Fill Pro - Black Forest Labs",
        },
        {
            "constant": "FLUX_FILL_DEV",
            "id": "black-forest-labs/flux-fill-dev",
            "provider": "replicate",
            "label": "Flux Fill Dev - Black Forest Labs",
        },
        {
            "constant": "ERASER",
            "id": "bria/eraser",
            "provider": "replicate",
            "label": "Bria Eraser - Bria",
        },
        {
            "constant": "IMAGE_TOOLKIT",
            "id": "Qubico/image-toolkit",
            "provider": "piapi",
            "label": "Qubico AI",
        },
        {
            "constant": "TRELLIS",
            "id": "Qubico/trellis",
            "provider": "piapi",
            "label": "Trellis 3D - Microsoft",
        },
    ],
    "audio": [
        {
            "constant": "TTS_1",
            "id": "tts-1",
            "provider": "openai",
            "label": "OpenAI TTS-1",
            "tags": ["tts"],
        },
        {
            "constant": "TTS_1_HD",
            "id": "tts-1-hd",
            "provider": "openai",
            "label": "OpenAI TTS-1 HD",
            "tags": ["tts"],
        },
        {
            "constant": "ELEVENLABS_TTS",
            "id": "elevenlabs-tts",
            "provider": "elevenlabs",
            "label": "ElevenLabs TTS",
            "tags": ["tts"],
        },
        {
            "constant": "GOOGLE_TTS",
            "id": "google-tts",
            "provider": "google",
            "label": "Google TTS",
            "tags": ["tts"],
        },
        {
            "constant": "WHISPER_1",
            "id": "whisper-1",
            "provider": "openai",
            "label": "Whisper-1",
            "tags": ["stt"],
        },
        {
            "constant": "UDIO",
            "id": "music-u",
            "provider": "udio",
            "label": "Udio (music)",
            "tags": ["music"],
        },
        {
            "constant": "QWEN3_TTS_FLASH",
            "id": "qwen3-tts-flash",
            "provider": "alibaba",
            "label": "Qwen3 TTS Flash - Alibaba Cloud",
            "tags": ["tts"],
        },
        {
            "constant": "QWEN3_ASR_FLASH",
            "id": "qwen3-asr-flash",
            "provider": "alibaba",
            "label": "Qwen3 ASR Flash - Alibaba Cloud",
            "tags": ["stt"],
        },
        {
            "constant": "ELEVENLABS_SPEECH_TO_TEXT",
            "id": "elevenlabs-speech-to-text",
            "provider": "elevenlabs",
            "label": "Speech to Text - ElevenLabs",
            "tags": ["stt"],
        },
        {
            "constant": "TELEPHONY_SHORT",
            "id": "telephony_short",
            "provider": "unknown",
            "label": "Speech to Text - Telephony Short - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "TELEPHONY",
            "id": "telephony",
            "provider": "unknown",
            "label": "Speech to Text - Telephony - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "PHONE_CALL",
            "id": "phone_call",
            "provider": "unknown",
            "label": "Speech to Text - Phone Call - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "MEDICAL_DICTATION",
            "id": "medical_dictation",
            "provider": "unknown",
            "label": "Speech to Text - Medical Dictation - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "MEDICAL_CONVERSATION",
            "id": "medical_conversation",
            "provider": "unknown",
            "label": "Speech to Text - Medical Conversation - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "LATEST_SHORT",
            "id": "latest_short",
            "provider": "unknown",
            "label": "Speech to Text - Short Form Content - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "LATEST_LONG",
            "id": "latest_long",
            "provider": "unknown",
            "label": "Speech to Text - Long Form Content - GoogleAI",
            "tags": ["stt"],
        },
        {
            "constant": "GPT_4O_TRANSCRIBE_DIARIZE",
            "id": "gpt-4o-transcribe-diarize",
            "provider": "openai",
            "label": "GPT-4o Transcribe Diarize - OpenAI",
            "tags": ["stt"],
        },
        {
            "constant": "GPT_4O_TRANSCRIBE",
            "id": "gpt-4o-transcribe",
            "provider": "openai",
            "label": "GPT-4o Transcribe - OpenAI",
            "tags": ["stt"],
        },
        {
            "constant": "ELEVENLABS_MUSIC",
            "id": "elevenlabs-music-v1",
            "provider": "elevenlabs",
            "label": "Music V1 - ElevenLabs",
            "tags": ["music"],
        },
        {
            "constant": "LYRIA_3_PRO_PREVIEW",
            "id": "lyria-3-pro-preview",
            "provider": "googleai",
            "label": "Lyria 3 Pro - Google",
            "tags": ["music"],
        },
        {
            "constant": "LYRIA_3_CLIP_PREVIEW",
            "id": "lyria-3-clip-preview",
            "provider": "googleai",
            "label": "Lyria 3 Clip - Google",
            "tags": ["music"],
        },
        {
            "constant": "LYRIA_002",
            "id": "lyria-002",
            "provider": "googleai",
            "label": "Lyria 2 - Google",
            "tags": ["music"],
        },
        {
            "constant": "MUSICGEN",
            "id": "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
            "provider": "replicate",
            "label": "MusicGen - Meta",
            "tags": ["music"],
        },
        {
            "constant": "SUNO_TTAPI",
            "id": "suno-ttapi",
            "provider": "ttapi",
            "label": "Suno - TTAPI",
            "tags": ["music"],
        },
        {
            "constant": "QWEN3_LIVETRANSLATE_FLASH",
            "id": "qwen3-livetranslate-flash",
            "provider": "alibaba",
            "label": "Qwen3 LiveTranslate Flash - Alibaba Cloud",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_8_FLASH",
            "id": "gemini-3.8-flash",
            "provider": "googleai",
            "label": "Gemini 3.8 Flash - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_7_FLASH",
            "id": "gemini-3.7-flash",
            "provider": "googleai",
            "label": "Gemini 3.7 Flash - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_6_FLASH",
            "id": "gemini-3.6-flash",
            "provider": "googleai",
            "label": "Gemini 3.6 Flash - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_5_FLASH",
            "id": "gemini-3.5-flash",
            "provider": "googleai",
            "label": "Gemini 3.5 Flash - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_1_PRO_PREVIEW",
            "id": "gemini-3.1-pro-preview",
            "provider": "googleai",
            "label": "Gemini 3.1 Pro - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_1_FLASH_LITE_PREVIEW",
            "id": "gemini-3.1-flash-lite-preview",
            "provider": "googleai",
            "label": "Gemini 3.1 Flash Lite - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_3_FLASH_PREVIEW",
            "id": "gemini-3-flash-preview",
            "provider": "googleai",
            "label": "Gemini 3 Flash - GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_2_5_PRO",
            "id": "gemini-2.5-pro",
            "provider": "googleai",
            "label": "Gemini 2.5 Pro -  GoogleAI",
            "tags": ["translate"],
        },
        {
            "constant": "GEMINI_2_5_FLASH",
            "id": "gemini-2.5-flash",
            "provider": "googleai",
            "label": "Gemini 2.5 Flash -  GoogleAI",
            "tags": ["translate"],
        },
    ],
    "video": [
        {
            "constant": "KLING",
            "id": "kling",
            "provider": "kuaishou",
            "label": "Kling",
        },
        {
            "constant": "DAMO_TEXT_TO_VIDEO",
            "id": "cjwbw/damo-text-to-video:1e205ea73084bd17a0a3b43396e49ba0d6bc2e754e9283b2df49fad2dcf95755",
            "provider": "replicate",
            "label": "Tongyi - Alibaba Cloud AI (Beta)",
        },
        {
            "constant": "WAN2_7_T2V",
            "id": "wan2.7-t2v",
            "provider": "alibaba",
            "label": "Wan 2.7 - Alibaba Cloud",
        },
        {
            "constant": "PIKA",
            "id": "pika",
            "provider": "falai",
            "label": "Pika AI",
        },
        {
            "constant": "SEEDANCE_2_5",
            "id": "bytedance/seedance-2.5",
            "provider": "openrouter",
            "label": "Seedance 2.5 - ByteDance",
        },
        {
            "constant": "SEEDANCE_2_0_MINI",
            "id": "bytedance/seedance-2.0-mini",
            "provider": "openrouter",
            "label": "Seedance 2.0 Mini - ByteDance",
        },
        {
            "constant": "SEEDANCE_2_0_FAST",
            "id": "bytedance/seedance-2.0-fast",
            "provider": "openrouter",
            "label": "Seedance 2.0 Fast - ByteDance",
        },
        {
            "constant": "SEEDANCE_2_0",
            "id": "bytedance/seedance-2.0",
            "provider": "openrouter",
            "label": "Seedance 2.0 - ByteDance",
        },
        {
            "constant": "VEO3_VIDEO",
            "id": "veo3-video",
            "provider": "piapi",
            "label": "Veo3 Video",
        },
        {
            "constant": "HAILUO",
            "id": "hailuo",
            "provider": "piapi",
            "label": "Hailuo AI",
        },
        {
            "constant": "HUNYUAN",
            "id": "Qubico/hunyuan",
            "provider": "piapi",
            "label": "Hunyuan AI",
        },
        {
            "constant": "WANX",
            "id": "Qubico/wanx",
            "provider": "piapi",
            "label": "Wanx AI",
        },
        {
            "constant": "ANIMATE_DIFF",
            "id": "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
            "provider": "replicate",
            "label": "Animate Diff - StabilityAI",
        },
        {
            "constant": "WAN2_7_I2V",
            "id": "wan2.7-i2v",
            "provider": "alibaba",
            "label": "Wan 2.7 - Alibaba Cloud",
        },
        {
            "constant": "SKYREELS",
            "id": "Qubico/skyreels",
            "provider": "piapi",
            "label": "Skyreels",
        },
    ],
}


# Feature type -> model used when a method is called without ``model=``.
DEFAULT_MODELS: dict[str, str] = {
    "UNIFY_CHAT_WITH_AI": "gpt-4o",
    "IMAGE_GENERATOR": "stable-diffusion-xl-1024-v1-0",
    "IMAGE_TO_PROMPT": "ideogram-3",
    "IMAGE_VARIATOR": "black-forest-labs/flux-redux-schnell",
    "IMAGE_UPSCALER": "stable-image",
    "IMAGE_EXTENDER": "stable-image",
    "IMAGE_EDITOR": "gpt-image-1-mini",
    "IMAGE_INPAINTER": "stable-image",
    "IMAGE_OBJECT_REMOVER": "stable-image",
    "BACKGROUND_REMOVER": "stable-image",
    "BACKGROUND_REPLACER": "gpt-image-1-mini",
    "TEXT_REMOVER": "clipdrop",
    "SEARCH_AND_REPLACE": "stable-image",
    "FACE_SWAPPER": "Qubico/image-toolkit",
    "IMAGE_3D_GENERATOR": "stable-image",
    "TEXT_TO_SPEECH": "tts-1",
    "SPEECH_TO_TEXT": "whisper-1",
    "MUSIC_GENERATOR": "music-u",
    "AUDIO_TRANSLATOR": "whisper-1",
    "TEXT_TO_VIDEO": "kling",
    "IMAGE_TO_VIDEO": "kling",
    "SUMMARIZER": "gpt-4o",
    "REWRITER": "gpt-4o",
    "PARAPHRASER": "gpt-4o",
    "CONTENT_EXPANDER": "gpt-4o",
    "CONTENT_SHORTENER": "gpt-4o",
    "CONTENT_TRANSLATOR": "gpt-4o",
    "GRAMMAR_CHECKER": "gpt-4o",
    "KEYWORD_RESEARCH": "gpt-4o",
    "CONTENT_GENERATOR_BLOG_ARTICLE": "gpt-4o",
    "YOUTUBE_SUMMARIZER": "gpt-4o",
}

# Feature type -> every model id the API accepts for it.
FEATURE_MODELS: dict[str, list[str]] = {
    "UNIFY_CHAT_WITH_AI": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-vl-plus", "qwen3-vl-flash", "qwen3-vl-8b-thinking", "qwen3-max", "qwen3-8b", "qwen-vl-plus", "qwen-vl-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "gpt-5.3-codex", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.7-code", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "sonar-reasoning-pro", "sonar-pro", "sonar-deep-research", "sonar", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "IMAGE_GENERATOR": ["qwen-image-plus", "qwen-image-max", "black-forest-labs/flux-schnell-lora", "black-forest-labs/flux-krea-dev", "black-forest-labs/flux-dev-lora", "black-forest-labs/flux-dev", "black-forest-labs/flux-2-pro", "black-forest-labs/flux-2-max", "black-forest-labs/flux-2-klein-9b", "black-forest-labs/flux-2-klein-4b", "black-forest-labs/flux-2-flex", "black-forest-labs/flux-2-dev", "black-forest-labs/flux-1.1-pro-ultra", "black-forest-labs/flux-1.1-pro", "dzine", "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview", "gemini-2.5-flash-image", "ideogram-3", "e71a1c2f-4f80-4800-934f-2c68979d8cc8", "b24e16ff-06e3-43eb-8d33-4416c2d75876", "aa77f04e-3eec-4034-9c07-d0f619684628", "6b645e3a-d64f-4341-a6d8-7a3690fbf042", "5c232a9e-9061-4777-980a-ddc8e65647c6", "2067ae52-33fd-4a82-bb92-c2c55e7d2786", "1e60896f-3c26-4296-8ecc-53e2afecc132", "magic-art_7_0", "magic-art_6_1", "magic-art", "gpt-image-2", "gpt-image-1-mini", "gpt-image-1", "recraft", "stable-diffusion-xl-1024-v1-0", "stable-image-ultra", "stable-image", "sd3.5-medium", "sd3.5-large-turbo", "sd3.5-large", "sd3.5-flash", "grok-imagine-image"],
    "IMAGE_TO_PROMPT": ["ideogram-3", "magic-art", "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5"],
    "IMAGE_VARIATOR": ["black-forest-labs/flux-redux-schnell", "black-forest-labs/flux-redux-dev", "dzine", "ideogram-3", "magic-art_7_0", "magic-art_6_1", "magic-art", "recraft"],
    "IMAGE_UPSCALER": ["dzine", "recraft", "stable-image"],
    "IMAGE_EXTENDER": ["clipdrop", "ideogram-3", "stable-image"],
    "IMAGE_EDITOR": ["qwen-image-edit-plus", "black-forest-labs/flux-kontext-pro", "black-forest-labs/flux-kontext-max", "black-forest-labs/flux-kontext-dev-lora", "black-forest-labs/flux-kontext-dev", "black-forest-labs/flux-depth-pro", "black-forest-labs/flux-depth-dev", "black-forest-labs/flux-canny-pro", "black-forest-labs/flux-canny-dev", "black-forest-labs/flux-2-pro", "black-forest-labs/flux-2-max", "black-forest-labs/flux-2-klein-4b", "black-forest-labs/flux-2-flex", "black-forest-labs/flux-2-dev", "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview", "gemini-2.5-flash-image", "gpt-image-2", "gpt-image-1-mini", "gpt-image-1", "stable-diffusion-xl-1024-v1-0"],
    "IMAGE_INPAINTER": ["black-forest-labs/flux-fill-pro", "black-forest-labs/flux-fill-dev", "ideogram-3", "gpt-image-2", "gpt-image-1-mini", "gpt-image-1", "stable-image"],
    "IMAGE_OBJECT_REMOVER": ["bria/eraser", "recraft", "stable-image"],
    "BACKGROUND_REMOVER": ["clipdrop", "recraft", "stable-image"],
    "BACKGROUND_REPLACER": ["clipdrop", "ideogram-3", "gpt-image-2", "gpt-image-1-mini", "gpt-image-1", "recraft"],
    "TEXT_REMOVER": ["clipdrop"],
    "SEARCH_AND_REPLACE": ["stable-image"],
    "FACE_SWAPPER": ["dzine", "Qubico/image-toolkit"],
    "IMAGE_3D_GENERATOR": ["Qubico/trellis", "stable-image"],
    "TEXT_TO_SPEECH": ["qwen3-tts-flash", "elevenlabs-tts", "google-tts", "tts-1-hd", "tts-1"],
    "SPEECH_TO_TEXT": ["qwen3-asr-flash", "elevenlabs-speech-to-text", "telephony_short", "telephony", "phone_call", "medical_dictation", "medical_conversation", "latest_short", "latest_long", "gpt-4o-transcribe-diarize", "gpt-4o-transcribe", "whisper-1"],
    "MUSIC_GENERATOR": ["elevenlabs-music-v1", "lyria-3-pro-preview", "lyria-3-clip-preview", "lyria-002", "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb", "suno-ttapi", "music-u"],
    "AUDIO_TRANSLATOR": ["qwen3-livetranslate-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "whisper-1"],
    "TEXT_TO_VIDEO": ["cjwbw/damo-text-to-video:1e205ea73084bd17a0a3b43396e49ba0d6bc2e754e9283b2df49fad2dcf95755", "wan2.7-t2v", "pika", "kling", "bytedance/seedance-2.5", "bytedance/seedance-2.0-mini", "bytedance/seedance-2.0-fast", "bytedance/seedance-2.0", "veo3-video", "hailuo", "Qubico/hunyuan", "Qubico/wanx", "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f"],
    "IMAGE_TO_VIDEO": ["wan2.7-i2v", "pika", "kling", "bytedance/seedance-2.5", "bytedance/seedance-2.0-mini", "bytedance/seedance-2.0-fast", "bytedance/seedance-2.0", "veo3-video", "Qubico/skyreels", "hailuo", "Qubico/hunyuan", "Qubico/wanx"],
    "SUMMARIZER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "REWRITER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "PARAPHRASER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "CONTENT_EXPANDER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "CONTENT_SHORTENER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "CONTENT_TRANSLATOR": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "GRAMMAR_CHECKER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "KEYWORD_RESEARCH": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "CONTENT_GENERATOR_BLOG_ARTICLE": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
    "YOUTUBE_SUMMARIZER": ["qwen3.7-plus", "qwen3.7-max", "qwen3.7-flash", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.6-flash", "qwen3-max", "qwen-plus", "qwen-max", "qwen-flash", "us.anthropic.claude-sonnet-5", "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5", "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5", "command-r-08-2024", "deepseek-v4-pro", "deepseek-flash", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", "meta/meta-llama-3-70b-instruct", "meta/llama-4-maverick-instruct", "magistral-small-latest", "magistral-medium-latest", "ministral-14b-latest", "open-mistral-nemo", "mistral-small-latest", "mistral-small-2603", "mistral-medium-latest", "mistral-medium-3-5", "mistral-large-latest", "mistral-large-2512", "o3-mini", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna", "gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4-pro", "gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2-pro", "gpt-5.2", "gpt-5.1", "gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4-turbo", "gpt-3.5-turbo", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "o3-pro", "o3", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6", "meta/muse-spark-1.3", "meta/muse-spark-1.2", "meta/muse-spark-1.1", "grok-4.7", "grok-4.6", "grok-4.5", "grok-4.3", "glm-5.3", "glm-5.2", "glm-5.1", "glm-5"],
}


def all_ids(domain: str | None = None) -> list[str]:
    """Return every known model id, optionally filtered by domain."""
    if domain is None:
        return [m['id'] for entries in MODEL_CATALOGUE.values() for m in entries]
    return [m['id'] for m in MODEL_CATALOGUE.get(domain, [])]
