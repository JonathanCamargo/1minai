"""Typed result models for all 1min.ai API domain responses.

All domain methods return one of these pydantic v2 models instead of raw dicts.
Models use ConfigDict(extra="ignore") to tolerate additional/undocumented API fields.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TextResult(BaseModel):
    """Result from a text generation or chat request.

    Returned by ``client.text.chat()`` and ``client.text.achat()``.
    Contains the generated text, the model that produced it, and optional
    token usage metadata.
    """

    model_config = ConfigDict(extra="ignore")
    content: str
    model: str
    usage: Optional[dict] = None


class ImageResult(BaseModel):
    """Result from an image generation or editing request.

    Returned by all ``client.image.*`` methods. The ``url`` field holds
    the primary image URL. For multi-image responses (e.g. n>1), ``urls``
    contains all image URLs. ``metadata`` holds the raw API result object.
    """

    model_config = ConfigDict(extra="ignore")
    url: str
    model: str
    urls: Optional[list[str]] = None
    metadata: Optional[dict] = None


class AudioResult(BaseModel):
    """Result from an audio generation, transcription, or translation request.

    Returned by all ``client.audio.*`` methods. TTS and music methods populate
    ``url`` with a link to the audio file. STT and translation methods populate
    ``content`` with the transcript or translated text.
    """

    model_config = ConfigDict(extra="ignore")
    url: Optional[str] = None
    content: Optional[str] = None
    model: str
    metadata: Optional[dict] = None


class VideoResult(BaseModel):
    """Result from a video generation request.

    Returned by ``client.video.generate()`` and ``client.video.from_image()``
    (and their async variants). The ``url`` field points to the generated video
    file after job polling completes.
    """

    model_config = ConfigDict(extra="ignore")
    url: str
    model: str
    metadata: Optional[dict] = None


class WritingResult(BaseModel):
    """Result from a writing assistance request.

    Returned by all ``client.writing.*`` methods. The ``content`` field contains
    the generated or transformed text (article, summary, translation, etc.).
    """

    model_config = ConfigDict(extra="ignore")
    content: str
    model: str
    metadata: Optional[dict] = None


class ConversationResult(BaseModel):
    """Result from a conversation management request.

    Returned by ``client.conversation.create()``, ``client.conversation.send()``,
    and their async variants. After ``create()``, ``conversation_id`` identifies
    the session for subsequent ``send()`` calls. After ``send()``, ``content``
    holds the assistant's reply.
    """

    model_config = ConfigDict(extra="ignore")
    content: str
    conversation_id: str
    model: str
    metadata: Optional[dict] = None


class AssetResult(BaseModel):
    """Result from an asset upload or retrieval request.

    Returned by ``client.asset.upload()``, ``client.asset.get()``, and their
    async variants. The ``url`` field is the publicly accessible asset URL.
    ``asset_id`` can be used to reference the asset in subsequent API calls.
    """

    model_config = ConfigDict(extra="ignore")
    url: str
    asset_id: str
    content_type: Optional[str] = None
    metadata: Optional[dict] = None
