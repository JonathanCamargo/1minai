"""Video domain resource for the 1min.ai API.

Domain timeout: 300s (per INFRA-07) — video generation is the most time-intensive
operation and can take several minutes to complete.

Provides 2 methods:
- generate: text-to-video using Luma AI, Kling, AnimateDiff, Tongyi
- from_image: image-to-video using Luma AI, Kling

Both methods auto-poll for completion since all video models are async.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from onemin.resources._base_resource import BaseResource
from onemin.models import VideoResult
from onemin._file_upload import FileInput, upload_file
from onemin._polling import poll_job


class VideoResource(BaseResource):
    """Video generation operations.

    Domain timeout: 300s (per INFRA-07) — longest timeout due to
    video generation duration.

    Both methods auto-poll for completion since all video models are asynchronous.

    Example::

        client.video.generate("sunset over the ocean", model="luma-ai")
        client.video.from_image("/path/to/photo.jpg", "animate the scene")
    """

    _domain = "video"

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

    async def _aupload(self, file: Union[FileInput, str]) -> str:
        """Async upload a file or return URL if already a remote URL."""
        if isinstance(file, str) and file.startswith("http"):
            return file
        from onemin._file_upload import async_upload_file
        return await async_upload_file(
            self._client._http,
            self._client._base_url,
            self._client._api_key,
            file,  # type: ignore[arg-type]
        )

    async def _apoll_and_parse(self, response: dict[str, Any], model: str) -> VideoResult:
        """Async poll for async job completion and parse the video result.

        Args:
            response: Initial API response containing aiRecord.id.
            model: Model name for the VideoResult.

        Returns:
            VideoResult with url and metadata from the completed job.
        """
        from onemin._polling import apoll_job
        ai_record = response.get("aiRecord", {})
        job_id = ai_record.get("id") or ai_record.get("jobId") or response.get("id", "")

        result = await apoll_job(
            self._client._http,
            self._client._base_url,
            self._client._api_key,
            str(job_id),
        )

        url = (
            result.get("result")
            or (result.get("output", {}) or {}).get("url")
            or result.get("url")
            or ""
        )

        return VideoResult(url=str(url), model=model, metadata=result)

    async def agenerate(
        self,
        prompt: str,
        *,
        model: str = "luma-ai",
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Async version of generate().

        All video generation models are asynchronous — this method automatically
        polls until completion and returns the final VideoResult.

        Args:
            prompt: Text description of the video to generate.
            model: Video model. Options: 'luma-ai', 'kling', 'animate-diff',
                   'tongyi'. Default: 'luma-ai'.
            duration: Optional video duration in seconds (e.g., 5).
            aspect_ratio: Optional aspect ratio (e.g., '16:9', '9:16', '1:1').
            **kwargs: Additional model parameters passed to the API.

        Returns:
            VideoResult with url pointing to the generated video file.

        Example:
            result = await client.video.agenerate("sunset over the ocean")
            print(result.url)
        """
        prompt_object: dict[str, Any] = {"prompt": prompt}
        if duration is not None:
            prompt_object["duration"] = duration
        if aspect_ratio is not None:
            prompt_object["aspectRatio"] = aspect_ratio
        prompt_object.update(kwargs)

        payload = {
            "type": "TEXT_TO_VIDEO",
            "model": model,
            "promptObject": prompt_object,
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        return await self._apoll_and_parse(response, model)

    async def afrom_image(
        self,
        image: Union[FileInput, str],
        prompt: str = "",
        *,
        model: str = "luma-ai",
        **kwargs: Any,
    ) -> VideoResult:
        """Async version of from_image().

        All video generation models are asynchronous — this method automatically
        polls until completion and returns the final VideoResult.

        Args:
            image: Source image as a file path, bytes, (filename, bytes) tuple,
                   or HTTP URL pointing to an already-uploaded image.
            prompt: Optional text description to guide the animation.
            model: Video model. Options: 'luma-ai', 'kling'. Default: 'luma-ai'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            VideoResult with url pointing to the generated video file.

        Example:
            result = await client.video.afrom_image("photo.jpg", "animate the scene")
            print(result.url)
        """
        image_url = await self._aupload(image)

        prompt_object: dict[str, Any] = {
            "prompt": prompt,
            "imageUrl": image_url,
            **kwargs,
        }

        payload = {
            "type": "IMAGE_TO_VIDEO",
            "model": model,
            "promptObject": prompt_object,
        }

        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        return await self._apoll_and_parse(response, model)

    def _poll_and_parse(self, response: dict[str, Any], model: str) -> VideoResult:
        """Poll for async job completion and parse the video result.

        Args:
            response: Initial API response containing aiRecord.id.
            model: Model name for the VideoResult.

        Returns:
            VideoResult with url and metadata from the completed job.
        """
        ai_record = response.get("aiRecord", {})
        job_id = ai_record.get("id") or ai_record.get("jobId") or response.get("id", "")

        result = poll_job(
            self._client._client,
            self._client._base_url,
            self._client._api_key,
            str(job_id),
        )

        url = (
            result.get("result")
            or (result.get("output", {}) or {}).get("url")
            or result.get("url")
            or ""
        )

        return VideoResult(url=str(url), model=model, metadata=result)

    def generate(
        self,
        prompt: str,
        *,
        model: str = "luma-ai",
        duration: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        **kwargs: Any,
    ) -> VideoResult:
        """Generate a video from a text prompt.

        All video generation models are asynchronous — this method automatically
        polls until completion and returns the final VideoResult.

        Args:
            prompt: Text description of the video to generate.
            model: Video model. Options: 'luma-ai', 'kling', 'animate-diff',
                   'tongyi'. Default: 'luma-ai'.
            duration: Optional video duration in seconds (e.g., 5).
            aspect_ratio: Optional aspect ratio (e.g., '16:9', '9:16', '1:1').
            **kwargs: Additional model parameters passed to the API.

        Returns:
            VideoResult with url pointing to the generated video file.

        Example:
            result = client.video.generate("sunset over the ocean")
            print(result.url)
        """
        prompt_object: dict[str, Any] = {"prompt": prompt}
        if duration is not None:
            prompt_object["duration"] = duration
        if aspect_ratio is not None:
            prompt_object["aspectRatio"] = aspect_ratio
        prompt_object.update(kwargs)

        payload = {
            "type": "TEXT_TO_VIDEO",
            "model": model,
            "promptObject": prompt_object,
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        return self._poll_and_parse(response, model)

    def from_image(
        self,
        image: Union[FileInput, str],
        prompt: str = "",
        *,
        model: str = "luma-ai",
        **kwargs: Any,
    ) -> VideoResult:
        """Generate a video from an image and optional text prompt.

        All video generation models are asynchronous — this method automatically
        polls until completion and returns the final VideoResult.

        Args:
            image: Source image as a file path, bytes, (filename, bytes) tuple,
                   or HTTP URL pointing to an already-uploaded image.
            prompt: Optional text description to guide the animation.
            model: Video model. Options: 'luma-ai', 'kling'. Default: 'luma-ai'.
            **kwargs: Additional model parameters passed to the API.

        Returns:
            VideoResult with url pointing to the generated video file.

        Example:
            result = client.video.from_image("photo.jpg", "animate the scene")
            print(result.url)
        """
        image_url = self._upload(image)

        prompt_object: dict[str, Any] = {
            "prompt": prompt,
            "imageUrl": image_url,
            **kwargs,
        }

        payload = {
            "type": "IMAGE_TO_VIDEO",
            "model": model,
            "promptObject": prompt_object,
        }

        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        return self._poll_and_parse(response, model)
