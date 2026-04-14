"""Synchronous client for the 1min.ai API."""

from __future__ import annotations

from onemin._base_client import BaseOneMinClient
from onemin.resources.image import ImageResource
from onemin.resources.text import TextResource
from onemin.resources.audio import AudioResource
from onemin.resources.video import VideoResource
from onemin.resources.writing import WritingResource
from onemin.resources.conversations import ConversationResource
from onemin.resources.assets import AssetResource


class OneMinClient(BaseOneMinClient):
    """Synchronous client for the 1min.ai API.

    Usage::

        client = OneMinClient(api_key="your-key")
        # or set the ONEMIN_API_KEY environment variable and call:
        client = OneMinClient()

    All configuration is via constructor kwargs (per D-05)::

        client = OneMinClient(
            api_key="your-key",
            timeout=60.0,
            max_retries=3,
            base_delay=1.0,
        )

    Domain resources are lazy-initialized on first access (Pattern 5)::

        client.image.generate("a cat", model="midjourney")
        client.text.chat("Hello!", model="gpt-4o")
        client.audio.speak("Hello!", model="tts-1")
        client.video.generate("a sunset", model="luma-ai")
        client.writing.summarize("long text...")
        client.conversation.create()
        client.asset.list()
    """

    @property
    def image(self) -> ImageResource:
        """Image generation and editing resource (90s domain timeout)."""
        if not hasattr(self, "_image"):
            self._image = ImageResource(self)
        return self._image

    @property
    def text(self) -> TextResource:
        """Text generation and LLM chat resource (30s domain timeout)."""
        if not hasattr(self, "_text"):
            self._text = TextResource(self)
        return self._text

    @property
    def audio(self) -> AudioResource:
        """Audio generation and processing resource (90s domain timeout)."""
        if not hasattr(self, "_audio"):
            self._audio = AudioResource(self)
        return self._audio

    @property
    def video(self) -> VideoResource:
        """Video generation resource (300s domain timeout)."""
        if not hasattr(self, "_video"):
            self._video = VideoResource(self)
        return self._video

    @property
    def writing(self) -> WritingResource:
        """Writing assistance resource (30s domain timeout)."""
        if not hasattr(self, "_writing"):
            self._writing = WritingResource(self)
        return self._writing

    @property
    def conversation(self) -> ConversationResource:
        """Conversation management resource (30s domain timeout, /api/conversations endpoint)."""
        if not hasattr(self, "_conversation"):
            self._conversation = ConversationResource(self)
        return self._conversation

    @property
    def asset(self) -> AssetResource:
        """Asset management resource (30s domain timeout, /api/assets endpoint)."""
        if not hasattr(self, "_asset"):
            self._asset = AssetResource(self)
        return self._asset
