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
        CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
        CLAUDE_HAIKU_4_5 = "claude-haiku-4-5-20251001"
        GEMINI_2_5_FLASH = "gemini-2.5-flash"
        MISTRAL_LARGE = "mistral-large-latest"
        MISTRAL_SMALL = "mistral-small-latest"
        LLAMA_3_70B = "meta/meta-llama-3-70b-instruct"
        DEEPSEEK_CHAT = "deepseek-chat"

    class Image:
        """Image models -- IMAGE_GENERATOR via /api/features."""

        MIDJOURNEY = "5c232a9e-9061-4777-980a-ddc8e65647c6"
        DALL_E_3 = "dall-e-3"
        DALL_E_2 = "dall-e-2"
        STABLE_DIFFUSION_XL = "stable-diffusion-xl-1024-v1-0"
        STABLE_DIFFUSION_768 = "stable-diffusion-v1-6"
        STABLE_IMAGE = "stable-image"
        LEONARDO_DIFFUSION_XL = "1e60896f-3c26-4296-8ecc-53e2afecc132"
        LEONARDO_KINO_XL = "aa77f04e-3eec-4034-9c07-d0f619684628"

    class Audio:
        """Audio models -- TEXT_TO_SPEECH via /api/features."""

        TTS_1 = "tts-1"
        TTS_1_HD = "tts-1-hd"
        ELEVENLABS_TTS = "elevenlabs-tts"
        GOOGLE_TTS = "google-tts"
        WHISPER_1 = "whisper-1"
        UDIO = "music-u"

    class Video:
        """Video models -- TEXT_TO_VIDEO via /api/features."""

        KLING = "kling"


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
            "constant": "CLAUDE_SONNET_4",
            "id": "claude-sonnet-4-20250514",
            "provider": "anthropic",
            "label": "Claude Sonnet 4",
        },
        {
            "constant": "CLAUDE_HAIKU_4_5",
            "id": "claude-haiku-4-5-20251001",
            "provider": "anthropic",
            "label": "Claude Haiku 4.5",
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
            "constant": "DEEPSEEK_CHAT",
            "id": "deepseek-chat",
            "provider": "deepseek",
            "label": "DeepSeek Chat",
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
            "constant": "DALL_E_3",
            "id": "dall-e-3",
            "provider": "openai",
            "label": "DALL-E 3",
        },
        {
            "constant": "DALL_E_2",
            "id": "dall-e-2",
            "provider": "openai",
            "label": "DALL-E 2",
        },
        {
            "constant": "STABLE_DIFFUSION_XL",
            "id": "stable-diffusion-xl-1024-v1-0",
            "provider": "stability",
            "label": "Stable Diffusion XL 1024",
        },
        {
            "constant": "STABLE_DIFFUSION_768",
            "id": "stable-diffusion-v1-6",
            "provider": "stability",
            "label": "Stable Diffusion v1.6",
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
    ],
    "video": [
        {
            "constant": "KLING",
            "id": "kling",
            "provider": "kuaishou",
            "label": "Kling",
        },
    ],
}


def all_ids(domain: str | None = None) -> list[str]:
    """Return every known model id, optionally filtered by domain."""
    if domain is None:
        return [m['id'] for entries in MODEL_CATALOGUE.values() for m in entries]
    return [m['id'] for m in MODEL_CATALOGUE.get(domain, [])]
