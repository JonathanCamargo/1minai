"""Audio domain resource for the 1min.ai API.

Domain timeout: 90s (per INFRA-07).

Provides 4 public methods: speak, transcribe, translate, generate_music
(plus async twins prefixed with ``a``).

Every method works with any model the API lists for its feature (see
``FEATURE_MODELS``). ``model=None`` picks ``DEFAULT_MODELS[feature]``, and the
fields that default model requires are filled in for you. Other models take
their own fields -- pass them as keyword arguments; they go into promptObject
unchanged. Field reference per model: https://docs.1min.ai/docs/api/intro
"""

from __future__ import annotations

import json
from typing import Any, Optional, Union

from onemin._file_upload import FileInput
from onemin.models import AudioResult
from onemin.resources._base_resource import BaseResource, feature_payload, result_items

# A file to upload (path, bytes, (filename, bytes)), an http(s) URL, or the
# asset key of an earlier upload or result.
AudioInput = Union[FileInput, str]

_OPENAI_TTS = {"voice": "alloy", "response_format": "mp3", "speed": 1}

# Fields each default model requires, keyed by (feature, model). Only applied
# when that exact model is used; caller keyword arguments override them.
_MODEL_DEFAULTS: dict[tuple[str, str], dict[str, Any]] = {
    ("TEXT_TO_SPEECH", "tts-1"): _OPENAI_TTS,
    ("TEXT_TO_SPEECH", "tts-1-hd"): _OPENAI_TTS,
    ("SPEECH_TO_TEXT", "whisper-1"): {"response_format": "text"},
    ("MUSIC_GENERATOR", "music-u"): {
        "lyrics_type": "generate",
        "task_type": "generate_music",
        "prompt": "",
        "make_instrumental": False,
        "seed": -1,
    },
}


def _file_result(ai_record: dict[str, Any], model: str) -> AudioResult:
    """AudioResult for features that produce an audio file."""
    keys = [str(i) for i in result_items(ai_record)]
    return AudioResult(
        url=ai_record.get("temporaryUrl") or None,
        keys=keys or None,
        model=model,
        metadata=ai_record,
    )


def _text_result(ai_record: dict[str, Any], model: str) -> AudioResult:
    """AudioResult for features that produce text.

    Items are plain text, or a JSON string such as ``{"text": "..."}``.
    """
    parts: list[str] = []
    for item in result_items(ai_record):
        if isinstance(item, str) and item.lstrip().startswith("{"):
            try:
                item = json.loads(item)
            except ValueError:
                pass
        if isinstance(item, dict):
            item = item.get("text") or item.get("content") or json.dumps(item)
        parts.append(str(item))
    return AudioResult(content="\n".join(parts), model=model, metadata=ai_record)


def _speak_fields(text: str, voice: Optional[str], kwargs: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {"text": text}
    if voice is not None:
        fields["voice"] = voice
    return {**fields, **kwargs}


def _music_payload(
    prompt: str, model: str | None, kwargs: dict[str, Any]
) -> tuple[dict[str, Any], str]:
    payload, model = feature_payload("MUSIC_GENERATOR", model, {}, _MODEL_DEFAULTS)
    # Udio takes the description as gpt_description_prompt ("prompt" is lyrics).
    key = "gpt_description_prompt" if model == "music-u" else "prompt"
    payload["promptObject"].update({key: prompt, **kwargs})
    payload["conversationId"] = "MUSIC_GENERATOR"
    return payload, model


class AudioResource(BaseResource):
    """Audio generation and processing operations.

    Domain timeout: 90s (per INFRA-07).
    """

    _domain = "audio"

    def speak(
        self,
        text: str,
        *,
        model: str | None = None,
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> AudioResult:
        """Convert text to speech.

        Args:
            text: The text to speak.
            model: Model id; defaults to ``DEFAULT_MODELS["TEXT_TO_SPEECH"]``.
            voice: Voice name (default model: alloy, echo, fable, onyx, nova,
                shimmer).
            **kwargs: Extra promptObject fields (e.g. ``speed``,
                ``response_format``).

        Returns:
            AudioResult: ``url`` is a temporary download link, ``keys`` the
            asset key of the audio file.

        Example:
            result = client.audio.speak("Hello, world!")
            client.audio.download(result, "hello.mp3")
        """
        payload, model = feature_payload(
            "TEXT_TO_SPEECH", model, _speak_fields(text, voice, kwargs), _MODEL_DEFAULTS
        )
        return _file_result(self._call_feature(payload), model)

    def transcribe(
        self, audio: AudioInput, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Transcribe speech to text.

        Args:
            audio: Audio to transcribe (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["SPEECH_TO_TEXT"]``.
            **kwargs: Extra promptObject fields (e.g. ``language``,
                ``response_format``: text, json, srt, verbose_json, vtt).

        Returns:
            AudioResult with the transcript in ``content``.

        Example:
            result = client.audio.transcribe("/path/to/recording.mp3")
            print(result.content)
        """
        fields = {"audioUrl": self._upload_asset(audio), **kwargs}
        payload, model = feature_payload("SPEECH_TO_TEXT", model, fields, _MODEL_DEFAULTS)
        return _text_result(self._call_feature(payload), model)

    def translate(
        self, audio: AudioInput, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Translate spoken audio into text in another language.

        The default model (Whisper) translates to English. Gemini models take
        ``originalLanguage`` and ``targetLanguage`` keyword arguments.

        Args:
            audio: Audio to translate (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["AUDIO_TRANSLATOR"]``.
            **kwargs: Extra promptObject fields.

        Returns:
            AudioResult with the translated text in ``content``.

        Example:
            result = client.audio.translate("/path/to/spanish.mp3")
            print(result.content)
        """
        fields = {"audioUrl": self._upload_asset(audio), **kwargs}
        payload, model = feature_payload("AUDIO_TRANSLATOR", model, fields, _MODEL_DEFAULTS)
        return _text_result(self._call_feature(payload), model)

    def generate_music(
        self, prompt: str, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Generate music from a description of its style and mood.

        Args:
            prompt: Description of the music (e.g. "upbeat jazz piano").
            model: Model id; defaults to ``DEFAULT_MODELS["MUSIC_GENERATOR"]``.
            **kwargs: Extra promptObject fields (default model: ``tags``,
                ``negative_tags``, ``title``, ``make_instrumental``).

        Returns:
            AudioResult: ``url`` is a temporary download link.

        Example:
            result = client.audio.generate_music("upbeat jazz piano")
            print(result.url)
        """
        payload, model = _music_payload(prompt, model, kwargs)
        # Music takes minutes: run in the background and poll for the result.
        return _file_result(self._call_feature(payload, background=True), model)

    # ------------------------------------------------------------------
    # Async methods (same arguments and results as the sync versions)
    # ------------------------------------------------------------------

    async def aspeak(
        self,
        text: str,
        *,
        model: str | None = None,
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> AudioResult:
        """Async version of :meth:`speak`."""
        payload, model = feature_payload(
            "TEXT_TO_SPEECH", model, _speak_fields(text, voice, kwargs), _MODEL_DEFAULTS
        )
        return _file_result(await self._acall_feature(payload), model)

    async def atranscribe(
        self, audio: AudioInput, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Async version of :meth:`transcribe`."""
        fields = {"audioUrl": await self._aupload_asset(audio), **kwargs}
        payload, model = feature_payload("SPEECH_TO_TEXT", model, fields, _MODEL_DEFAULTS)
        return _text_result(await self._acall_feature(payload), model)

    async def atranslate(
        self, audio: AudioInput, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Async version of :meth:`translate`."""
        fields = {"audioUrl": await self._aupload_asset(audio), **kwargs}
        payload, model = feature_payload("AUDIO_TRANSLATOR", model, fields, _MODEL_DEFAULTS)
        return _text_result(await self._acall_feature(payload), model)

    async def agenerate_music(
        self, prompt: str, *, model: str | None = None, **kwargs: Any
    ) -> AudioResult:
        """Async version of :meth:`generate_music`."""
        payload, model = _music_payload(prompt, model, kwargs)
        return _file_result(await self._acall_feature(payload, background=True), model)
