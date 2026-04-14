"""Audio domain resource for the 1min.ai API.

Domain timeout: 90s (per INFRA-07) — audio processing takes significant time.

Provides 4 methods:
- speak: text-to-speech (TTS) using ElevenLabs, OpenAI TTS, Google TTS
- transcribe: speech-to-text (STT) using Whisper
- translate: audio translation using Whisper
- generate_music: music generation using Suno, Udio, MusicGen
"""

from __future__ import annotations

from typing import Any, Optional, Union

from onemin.resources._base_resource import BaseResource
from onemin.models import AudioResult
from onemin._file_upload import FileInput, upload_file


class AudioResource(BaseResource):
    """Audio generation and processing operations.

    Domain timeout: 90s (per INFRA-07).

    Supports TTS (text-to-speech), STT (speech-to-text), audio translation,
    and music generation using various AI models.

    Example::

        client.audio.speak("Hello world", model="tts-1")
        client.audio.transcribe("/path/to/audio.mp3")
        client.audio.translate("/path/to/audio.mp3")
        client.audio.generate_music("upbeat electronic", duration=30)
    """

    _domain = "audio"

    def _upload(self, file: Union[FileInput, str]) -> str:
        """Upload a file or return URL if already a remote URL.

        Args:
            file: A file path, bytes, (filename, bytes) tuple, or HTTP URL string.

        Returns:
            URL string pointing to the uploaded (or existing) asset.
        """
        if isinstance(file, str) and file.startswith("http"):
            return file
        return upload_file(
            self._client._client,
            self._client._base_url,
            self._client._api_key,
            file,  # type: ignore[arg-type]
        )

    def speak(
        self,
        text: str,
        *,
        model: str = "tts-1",
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> AudioResult:
        """Convert text to speech audio.

        Args:
            text: The text to convert to speech.
            model: TTS model to use. Options: 'tts-1', 'tts-1-hd',
                   'elevenlabs-tts', 'google-tts'. Default: 'tts-1'.
            voice: Optional voice name (e.g., 'Rachel' for ElevenLabs).
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with url pointing to the generated audio file.

        Example:
            result = client.audio.speak("Hello, world!")
            print(result.url)
        """
        prompt_object: dict[str, Any] = {"prompt": text}
        if voice is not None:
            prompt_object["voice"] = voice
        prompt_object.update(kwargs)

        payload = {
            "type": "TEXT_TO_SPEECH",
            "model": model,
            "promptObject": prompt_object,
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, str):
            url = result_obj
        else:
            url = (
                result_obj.get("url")
                or result_obj.get("audioUrl")
                or ""
            )

        return AudioResult(url=url, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    def transcribe(
        self,
        audio: Union[FileInput, str],
        *,
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> AudioResult:
        """Transcribe speech from an audio file to text.

        Args:
            audio: Audio file as a path, bytes, (filename, bytes) tuple, or
                   HTTP URL pointing to an already-uploaded audio file.
            model: STT model. Options: 'whisper-1', 'latest_long',
                   'latest_short', 'phone_call'. Default: 'whisper-1'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with content containing the transcript text.

        Example:
            result = client.audio.transcribe("/path/to/recording.mp3")
            print(result.content)
        """
        audio_url = self._upload(audio)

        payload = {
            "type": "SPEECH_TO_TEXT",
            "model": model,
            "promptObject": {"audioUrl": audio_url, **kwargs},
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, dict):
            text = (
                result_obj.get("text")
                or result_obj.get("content")
                or result_obj.get("message")
                or ""
            )
        else:
            text = str(result_obj) if result_obj else ""

        return AudioResult(content=text, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    def translate(
        self,
        audio: Union[FileInput, str],
        *,
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> AudioResult:
        """Translate speech in an audio file to English text.

        Args:
            audio: Audio file as a path, bytes, (filename, bytes) tuple, or
                   HTTP URL pointing to an already-uploaded audio file.
            model: Translation model. Default: 'whisper-1'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with content containing the translated text.

        Example:
            result = client.audio.translate("/path/to/foreign_audio.mp3")
            print(result.content)
        """
        audio_url = self._upload(audio)

        payload = {
            "type": "AUDIO_TRANSLATOR",
            "model": model,
            "promptObject": {"audioUrl": audio_url, **kwargs},
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, dict):
            text = (
                result_obj.get("text")
                or result_obj.get("content")
                or result_obj.get("message")
                or ""
            )
        else:
            text = str(result_obj) if result_obj else ""

        return AudioResult(content=text, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    async def _aupload(self, file: Union[FileInput, str]) -> str:
        """Async upload a file or return URL if already a remote URL.

        Args:
            file: A file path, bytes, (filename, bytes) tuple, or HTTP URL string.

        Returns:
            URL string pointing to the uploaded (or existing) asset.
        """
        if isinstance(file, str) and file.startswith("http"):
            return file
        from onemin._file_upload import async_upload_file
        return await async_upload_file(
            self._client._http,
            self._client._base_url,
            self._client._api_key,
            file,  # type: ignore[arg-type]
        )

    async def aspeak(
        self,
        text: str,
        *,
        model: str = "tts-1",
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> AudioResult:
        """Convert text to speech audio asynchronously.

        Args:
            text: The text to convert to speech.
            model: TTS model to use. Options: 'tts-1', 'tts-1-hd',
                   'elevenlabs-tts', 'google-tts'. Default: 'tts-1'.
            voice: Optional voice name (e.g., 'Rachel' for ElevenLabs).
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with url pointing to the generated audio file.

        Example:
            result = await client.audio.aspeak("Hello, world!")
            print(result.url)
        """
        prompt_object: dict[str, Any] = {"prompt": text}
        if voice is not None:
            prompt_object["voice"] = voice
        prompt_object.update(kwargs)

        payload = {
            "type": "TEXT_TO_SPEECH",
            "model": model,
            "promptObject": prompt_object,
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, str):
            url = result_obj
        else:
            url = (
                result_obj.get("url")
                or result_obj.get("audioUrl")
                or ""
            )

        return AudioResult(url=url, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    async def atranscribe(
        self,
        audio: Union[FileInput, str],
        *,
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> AudioResult:
        """Transcribe speech from an audio file to text asynchronously.

        Args:
            audio: Audio file as a path, bytes, (filename, bytes) tuple, or
                   HTTP URL pointing to an already-uploaded audio file.
            model: STT model. Options: 'whisper-1', 'latest_long',
                   'latest_short', 'phone_call'. Default: 'whisper-1'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with content containing the transcript text.

        Example:
            result = await client.audio.atranscribe("/path/to/recording.mp3")
            print(result.content)
        """
        audio_url = await self._aupload(audio)

        payload = {
            "type": "SPEECH_TO_TEXT",
            "model": model,
            "promptObject": {"audioUrl": audio_url, **kwargs},
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, dict):
            text = (
                result_obj.get("text")
                or result_obj.get("content")
                or result_obj.get("message")
                or ""
            )
        else:
            text = str(result_obj) if result_obj else ""

        return AudioResult(content=text, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    async def atranslate(
        self,
        audio: Union[FileInput, str],
        *,
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> AudioResult:
        """Translate speech in an audio file to English text asynchronously.

        Args:
            audio: Audio file as a path, bytes, (filename, bytes) tuple, or
                   HTTP URL pointing to an already-uploaded audio file.
            model: Translation model. Default: 'whisper-1'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with content containing the translated text.

        Example:
            result = await client.audio.atranslate("/path/to/foreign_audio.mp3")
            print(result.content)
        """
        audio_url = await self._aupload(audio)

        payload = {
            "type": "AUDIO_TRANSLATOR",
            "model": model,
            "promptObject": {"audioUrl": audio_url, **kwargs},
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, dict):
            text = (
                result_obj.get("text")
                or result_obj.get("content")
                or result_obj.get("message")
                or ""
            )
        else:
            text = str(result_obj) if result_obj else ""

        return AudioResult(content=text, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    async def agenerate_music(
        self,
        prompt: str,
        *,
        model: str = "music-s",
        duration: int = 30,
        **kwargs: Any,
    ) -> AudioResult:
        """Generate music from a text description asynchronously.

        Args:
            prompt: Text description of the music to generate.
            model: Music model. Options: 'music-s' (Suno), 'music-u' (Udio),
                   'meta/musicgen:...' (MusicGen). Default: 'music-s'.
            duration: Length of the generated audio in seconds. Default: 30.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with url pointing to the generated music file.

        Example:
            result = await client.audio.agenerate_music("upbeat electronic track")
            print(result.url)
        """
        payload = {
            "type": "MUSIC_GENERATOR",
            "model": model,
            "promptObject": {"prompt": prompt, "duration": duration, **kwargs},
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, str):
            url = result_obj
        else:
            url = (
                result_obj.get("url")
                or result_obj.get("audioUrl")
                or ""
            )

        return AudioResult(url=url, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)

    def generate_music(
        self,
        prompt: str,
        *,
        model: str = "music-s",
        duration: int = 30,
        **kwargs: Any,
    ) -> AudioResult:
        """Generate music from a text description.

        Args:
            prompt: Text description of the music to generate.
            model: Music model. Options: 'music-s' (Suno), 'music-u' (Udio),
                   'meta/musicgen:...' (MusicGen). Default: 'music-s'.
            duration: Length of the generated audio in seconds. Default: 30.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            AudioResult with url pointing to the generated music file.

        Example:
            result = client.audio.generate_music("upbeat electronic track")
            print(result.url)
        """
        payload = {
            "type": "MUSIC_GENERATOR",
            "model": model,
            "promptObject": {"prompt": prompt, "duration": duration, **kwargs},
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        ai_record = response.get("aiRecord", response)
        result_obj = ai_record.get("resultObject", ai_record)
        if isinstance(result_obj, str):
            url = result_obj
        else:
            url = (
                result_obj.get("url")
                or result_obj.get("audioUrl")
                or ""
            )

        return AudioResult(url=url, model=model, metadata=result_obj if isinstance(result_obj, dict) else None)
