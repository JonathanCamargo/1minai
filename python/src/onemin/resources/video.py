"""Video domain resource for the 1min.ai API.

Domain timeout: 300s (per INFRA-07).

Provides 2 public methods: generate (text to video) and from_image (image to
video), plus async twins prefixed with ``a``.

Video jobs outlive the HTTP gateway timeout, so requests are sent with
``"async": true`` and the result is polled from /api/results/{uuid} until it
finishes.

Every method works with any model the API lists for its feature (see
``FEATURE_MODELS``). ``model=None`` picks ``DEFAULT_MODELS[feature]``, and the
fields that default model requires are filled in for you. Other models take
their own fields -- pass them as keyword arguments; they go into promptObject
unchanged. Field reference per model: https://docs.1min.ai/docs/api/intro
"""

from __future__ import annotations

from typing import Any, Optional, Union

from onemin._file_upload import FileInput
from onemin.models import VideoResult
from onemin.resources._base_resource import BaseResource, feature_payload, result_items

_KLING = {"duration": 5, "mode": "std", "version": "1.6", "aspect_ratio": "16:9"}

# Fields each default model requires, keyed by (feature, model). Only applied
# when that exact model is used; caller keyword arguments override them.
_MODEL_DEFAULTS: dict[tuple[str, str], dict[str, Any]] = {
    ("TEXT_TO_VIDEO", "kling"): _KLING,
    ("IMAGE_TO_VIDEO", "kling"): _KLING,
}


def _video_payload(
    feature: str,
    model: str | None,
    fields: dict[str, Any],
    duration: Optional[int],
    aspect_ratio: Optional[str],
    kwargs: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    if duration is not None:
        fields["duration"] = duration
    if aspect_ratio is not None:
        fields["aspect_ratio"] = aspect_ratio
    payload, model = feature_payload(feature, model, {**fields, **kwargs}, _MODEL_DEFAULTS)
    payload["conversationId"] = feature
    return payload, model


def _parse_video_result(ai_record: dict[str, Any], model: str) -> VideoResult:
    keys = [str(i) for i in result_items(ai_record)]
    return VideoResult(
        url=ai_record.get("temporaryUrl") or "",
        keys=keys or None,
        model=model,
        metadata=ai_record,
    )


class VideoResource(BaseResource):
    """Video generation operations.

    Domain timeout: 300s (per INFRA-07).
    """

    _domain = "video"

    def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Generate a video from a text prompt, waiting until it is ready.

        Args:
            prompt: Description of the video.
            model: Model id; defaults to ``DEFAULT_MODELS["TEXT_TO_VIDEO"]``
                (Kling).
            duration: Length in seconds (Kling: 5 or 10).
            aspect_ratio: e.g. "16:9", "9:16", "1:1".
            **kwargs: Extra promptObject fields (Kling: ``mode``, ``version``,
                ``negative_prompt``, ``cfg_scale``).

        Returns:
            VideoResult: ``url`` is a temporary download link.

        Example:
            result = client.video.generate("a sunset over the ocean")
            client.video.download(result, "sunset.mp4")
        """
        payload, model = _video_payload(
            "TEXT_TO_VIDEO", model, {"prompt": prompt}, duration, aspect_ratio, kwargs
        )
        return _parse_video_result(self._call_feature(payload, background=True), model)

    def from_image(
        self,
        image: Union[FileInput, str],
        prompt: str = "",
        *,
        model: str | None = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Animate an image into a video, waiting until it is ready.

        Args:
            image: Start frame (path, bytes, URL, or asset key).
            prompt: Description of the desired motion.
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_TO_VIDEO"]``
                (Kling).
            duration: Length in seconds (Kling: 5 or 10).
            aspect_ratio: e.g. "16:9", "9:16", "1:1".
            **kwargs: Extra promptObject fields.

        Returns:
            VideoResult: ``url`` is a temporary download link.

        Example:
            result = client.video.from_image("photo.jpg", "slow zoom in")
            print(result.url)
        """
        fields = {"imageUrl": self._upload_asset(image), "prompt": prompt}
        payload, model = _video_payload(
            "IMAGE_TO_VIDEO", model, fields, duration, aspect_ratio, kwargs
        )
        return _parse_video_result(self._call_feature(payload, background=True), model)

    # ------------------------------------------------------------------
    # Async methods (same arguments and results as the sync versions)
    # ------------------------------------------------------------------

    async def agenerate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Async version of :meth:`generate`."""
        payload, model = _video_payload(
            "TEXT_TO_VIDEO", model, {"prompt": prompt}, duration, aspect_ratio, kwargs
        )
        record = await self._acall_feature(payload, background=True)
        return _parse_video_result(record, model)

    async def afrom_image(
        self,
        image: Union[FileInput, str],
        prompt: str = "",
        *,
        model: str | None = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Async version of :meth:`from_image`."""
        fields = {"imageUrl": await self._aupload_asset(image), "prompt": prompt}
        payload, model = _video_payload(
            "IMAGE_TO_VIDEO", model, fields, duration, aspect_ratio, kwargs
        )
        record = await self._acall_feature(payload, background=True)
        return _parse_video_result(record, model)
