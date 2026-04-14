"""Image domain resource for the 1min.ai API.

Domain timeout: 90s (per INFRA-07) — image generation takes significant time.

Provides 14 public methods:
  generate, to_prompt, variation, upscale, extend,
  remove_background, replace_background, remove_text,
  remove_object, search_and_replace, inpaint, edit_text,
  swap_face, generate_3d.

All editing methods follow the upload-then-feature pattern:
  1. Upload the image file to /api/assets to get an asset URL.
  2. POST to /api/features with the asset URL in promptObject.

generate() supports Midjourney auto-polling via poll_job.
"""

from __future__ import annotations

from typing import Any, Union

from onemin._file_upload import FileInput, upload_file
from onemin._polling import poll_job
from onemin.models import ImageResult
from onemin.resources._base_resource import BaseResource

# Midjourney model UUID — triggers async job polling instead of direct result
MIDJOURNEY_MODEL = "5c232a9e-9061-4777-980a-ddc8e65647c6"

# ImageInput accepts either a file (for upload) or an HTTP URL string (used as-is)
ImageInput = Union[FileInput, str]


class ImageResource(BaseResource):
    """Image generation and editing operations.

    Domain timeout: 90s (per INFRA-07).

    Methods:
        generate: Generate an image from a text prompt (supports Midjourney polling).
        to_prompt: Convert an image to a text description.
        variation: Generate a variation of an existing image.
        upscale: Upscale an image to higher resolution.
        extend: Extend the canvas of an image outward.
        remove_background: Remove the background from an image.
        replace_background: Replace the background with a new scene.
        remove_text: Remove text overlays from an image.
        remove_object: Remove a specified object from an image.
        search_and_replace: Find and replace an element in an image.
        inpaint: Fill a masked area in an image.
        edit_text: Edit text within an image.
        swap_face: Swap a face from one image to another.
        generate_3d: Generate a 3D representation of an object.
    """

    _domain = "image"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _upload(self, image: ImageInput) -> str:
        """Upload a file to /api/assets or return a URL string as-is.

        Args:
            image: A file input (bytes, path, tuple) or an HTTP URL string.
                   If the image is already an HTTP URL, it is returned unchanged.

        Returns:
            The URL string of the uploaded (or passed-through) asset.
        """
        if isinstance(image, str) and image.startswith("http"):
            return image
        return upload_file(
            self._client._client,
            self._client._base_url,
            self._client._api_key,
            image,  # type: ignore[arg-type]
        )

    def _upload_and_call(
        self,
        feature_type: str,
        image: ImageInput,
        model: str,
        prompt_object_extra: dict[str, Any],
    ) -> ImageResult:
        """Upload an image and POST to /api/features.

        This helper encapsulates the repeated pattern used by all editing methods:
          upload file -> build payload with imageUrl -> POST /api/features -> parse.

        Args:
            feature_type: The API feature type constant (e.g., "BACKGROUND_REMOVER").
            image: File input or URL string for the image to process.
            model: Model name to pass in the payload.
            prompt_object_extra: Additional fields to merge into promptObject.

        Returns:
            An ImageResult with url, model, optional urls, and metadata.
        """
        asset_url = self._upload(image)
        payload: dict[str, Any] = {
            "type": feature_type,
            "model": model,
            "promptObject": {
                "imageUrl": asset_url,
                **prompt_object_extra,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    def _parse_image_result(
        self, response: dict[str, Any], model: str
    ) -> ImageResult:
        """Extract an ImageResult from a raw /api/features response.

        Handles these response shapes:
          - response['aiRecord']['resultObject']['url']
          - response['aiRecord']['resultObject']['imageUrl']
          - response['aiRecord']['resultObject']['urls'] or ['images'] for multiple

        Args:
            response: Raw JSON response dictionary from the API.
            model: Model name to include in the result.

        Returns:
            An ImageResult with url, model, optional urls, and metadata.
        """
        ai_record = response.get("aiRecord", {})
        result_obj: dict[str, Any] = ai_record.get("resultObject", {})

        url: str = (
            result_obj.get("url")
            or result_obj.get("imageUrl")
            or ""
        )
        urls: list[str] | None = (
            result_obj.get("urls") or result_obj.get("images") or None
        )

        return ImageResult(url=url, model=model, urls=urls, metadata=result_obj)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        *,
        model: str = "dall-e-3",
        width: int = 1024,
        height: int = 1024,
        n: int = 1,
        **kwargs: Any,
    ) -> ImageResult:
        """Generate an image from a text prompt.

        For Midjourney models the request is submitted as an async job and
        automatically polled until completion (up to 5 minutes).

        Args:
            prompt: Text description of the image to generate.
            model: Model to use (default "dall-e-3"). Pass "midjourney" or the
                   Midjourney UUID to use Midjourney with auto-polling.
            width: Image width in pixels (default 1024).
            height: Image height in pixels (default 1024).
            n: Number of images to generate (default 1).
            **kwargs: Additional model-specific parameters forwarded to promptObject.

        Returns:
            An ImageResult with the generated image URL and optional metadata.

        Example:
            result = client.image.generate("a cat sitting on a red cushion")
            print(result.url)
        """
        # Normalise Midjourney model references to the UUID
        is_midjourney = (
            model == MIDJOURNEY_MODEL
            or model.lower().startswith("midjourney")
        )
        effective_model = MIDJOURNEY_MODEL if is_midjourney else model

        payload: dict[str, Any] = {
            "type": "IMAGE_GENERATOR",
            "model": effective_model,
            "promptObject": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "n": n,
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        if is_midjourney:
            # Midjourney returns a job ID that must be polled for the result
            job_id: str = response.get("aiRecord", {}).get("id", "")
            response = poll_job(
                self._client._client,
                self._client._base_url,
                self._client._api_key,
                job_id,
            )

        return self._parse_image_result(response, effective_model)

    def to_prompt(
        self,
        image: ImageInput,
        *,
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> ImageResult:
        """Convert an image to a text description (image-to-prompt).

        Args:
            image: Image file or URL to describe.
            model: Model to use (default "gpt-4o").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult whose ``url`` field contains the description text.

        Example:
            result = client.image.to_prompt("https://example.com/photo.jpg")
            print(result.url)
        """
        return self._upload_and_call("IMAGE_TO_PROMPT", image, model, kwargs)

    def variation(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        n: int = 1,
        **kwargs: Any,
    ) -> ImageResult:
        """Generate a variation of an existing image.

        Args:
            image: Source image file or URL.
            model: Model to use (default "dall-e-2").
            n: Number of variations to generate (default 1).
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the variation URL(s).

        Example:
            result = client.image.variation("photo.jpg")
            print(result.url)
        """
        return self._upload_and_call(
            "IMAGE_VARIATOR", image, model, {"n": n, **kwargs}
        )

    def upscale(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Upscale an image to higher resolution.

        Args:
            image: Image file or URL to upscale.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the upscaled image URL.

        Example:
            result = client.image.upscale("photo.jpg")
            print(result.url)
        """
        return self._upload_and_call("IMAGE_UPSCALER", image, model, kwargs)

    def extend(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Extend the canvas of an image outward (outpainting).

        Args:
            image: Image file or URL to extend.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject (e.g. direction).

        Returns:
            An ImageResult with the extended image URL.

        Example:
            result = client.image.extend("photo.jpg")
            print(result.url)
        """
        return self._upload_and_call("IMAGE_EXTENDER", image, model, kwargs)

    def remove_background(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Remove the background from an image.

        Args:
            image: Image file or URL.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the background-removed image URL.

        Example:
            result = client.image.remove_background("photo.jpg")
            print(result.url)
        """
        return self._upload_and_call("BACKGROUND_REMOVER", image, model, kwargs)

    def replace_background(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Replace the background of an image with a new scene.

        Args:
            image: Image file or URL with the foreground subject.
            prompt: Text description of the new background.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the new-background image URL.

        Example:
            result = client.image.replace_background("photo.jpg", "a sunny beach")
            print(result.url)
        """
        return self._upload_and_call(
            "BACKGROUND_REPLACER", image, model, {"prompt": prompt, **kwargs}
        )

    def remove_text(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Remove text overlays from an image.

        Args:
            image: Image file or URL containing text to remove.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the text-removed image URL.

        Example:
            result = client.image.remove_text("photo.jpg")
            print(result.url)
        """
        return self._upload_and_call("TEXT_REMOVER", image, model, kwargs)

    def remove_object(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Remove a specified object from an image.

        Args:
            image: Image file or URL.
            prompt: Description of the object to remove.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the object-removed image URL.

        Example:
            result = client.image.remove_object("photo.jpg", "the red car")
            print(result.url)
        """
        return self._upload_and_call(
            "IMAGE_OBJECT_REMOVER", image, model, {"prompt": prompt, **kwargs}
        )

    def search_and_replace(
        self,
        image: ImageInput,
        search_prompt: str,
        replace_prompt: str,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Find an element in an image and replace it.

        Args:
            image: Image file or URL.
            search_prompt: Description of the element to find and replace.
            replace_prompt: Description of what to replace it with.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the modified image URL.

        Example:
            result = client.image.search_and_replace("photo.jpg", "cat", "dog")
            print(result.url)
        """
        return self._upload_and_call(
            "SEARCH_AND_REPLACE",
            image,
            model,
            {
                "searchPrompt": search_prompt,
                "replacePrompt": replace_prompt,
                **kwargs,
            },
        )

    def inpaint(
        self,
        image: ImageInput,
        mask: ImageInput,
        prompt: str,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Fill a masked area of an image guided by a text prompt.

        Args:
            image: Source image file or URL.
            mask: Mask image file or URL (white = area to fill, black = keep).
            prompt: Text description of what to generate in the masked area.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the inpainted image URL.

        Example:
            result = client.image.inpaint("photo.jpg", "mask.jpg", "a red rose")
            print(result.url)
        """
        image_url = self._upload(image)
        mask_url = self._upload(mask)
        payload: dict[str, Any] = {
            "type": "IMAGE_INPAINTER",
            "model": model,
            "promptObject": {
                "imageUrl": image_url,
                "maskUrl": mask_url,
                "prompt": prompt,
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    def edit_text(
        self,
        image: ImageInput,
        text_config: dict[str, Any],
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Edit text content within an image.

        Args:
            image: Image file or URL containing text to edit.
            text_config: Configuration dict describing the text edits.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the text-edited image URL.

        Example:
            result = client.image.edit_text("photo.jpg", {"text": "Hello", "x": 10, "y": 10})
            print(result.url)
        """
        return self._upload_and_call(
            "IMAGE_EDITOR", image, model, {"textConfig": text_config, **kwargs}
        )

    def swap_face(
        self,
        source_image: ImageInput,
        target_image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Swap a face from the source image onto the target image.

        Args:
            source_image: Image file or URL containing the face to copy.
            target_image: Image file or URL to place the face onto.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the face-swapped image URL.

        Example:
            result = client.image.swap_face("source.jpg", "target.jpg")
            print(result.url)
        """
        source_url = self._upload(source_image)
        target_url = self._upload(target_image)
        payload: dict[str, Any] = {
            "type": "FACE_SWAPPER",
            "model": model,
            "promptObject": {
                "sourceImageUrl": source_url,
                "targetImageUrl": target_url,
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    # ------------------------------------------------------------------
    # Async helpers and methods
    # ------------------------------------------------------------------

    async def _aupload(self, image: ImageInput) -> str:
        """Async upload a file to /api/assets or return a URL string as-is.

        Args:
            image: A file input (bytes, path, tuple) or an HTTP URL string.
                   If the image is already an HTTP URL, it is returned unchanged.

        Returns:
            The URL string of the uploaded (or passed-through) asset.
        """
        if isinstance(image, str) and image.startswith("http"):
            return image
        from onemin._file_upload import async_upload_file
        return await async_upload_file(
            self._client._http,
            self._client._base_url,
            self._client._api_key,
            image,  # type: ignore[arg-type]
        )

    async def _aupload_and_call(
        self,
        feature_type: str,
        image: ImageInput,
        model: str,
        prompt_object_extra: dict[str, Any],
    ) -> ImageResult:
        """Async upload an image and POST to /api/features.

        Args:
            feature_type: The API feature type constant (e.g., "BACKGROUND_REMOVER").
            image: File input or URL string for the image to process.
            model: Model name to pass in the payload.
            prompt_object_extra: Additional fields to merge into promptObject.

        Returns:
            An ImageResult with url, model, optional urls, and metadata.
        """
        asset_url = await self._aupload(image)
        payload: dict[str, Any] = {
            "type": feature_type,
            "model": model,
            "promptObject": {
                "imageUrl": asset_url,
                **prompt_object_extra,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    async def agenerate(
        self,
        prompt: str,
        *,
        model: str = "dall-e-3",
        width: int = 1024,
        height: int = 1024,
        n: int = 1,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of generate().

        For Midjourney models the request is submitted as an async job and
        automatically polled until completion (up to 5 minutes).

        Args:
            prompt: Text description of the image to generate.
            model: Model to use (default "dall-e-3"). Pass "midjourney" or the
                   Midjourney UUID to use Midjourney with async polling.
            width: Image width in pixels (default 1024).
            height: Image height in pixels (default 1024).
            n: Number of images to generate (default 1).
            **kwargs: Additional model-specific parameters forwarded to promptObject.

        Returns:
            An ImageResult with the generated image URL and optional metadata.

        Example:
            result = await client.image.agenerate("a cat sitting on a red cushion")
            print(result.url)
        """
        is_midjourney = (
            model == MIDJOURNEY_MODEL
            or model.lower().startswith("midjourney")
        )
        effective_model = MIDJOURNEY_MODEL if is_midjourney else model

        payload: dict[str, Any] = {
            "type": "IMAGE_GENERATOR",
            "model": effective_model,
            "promptObject": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "n": n,
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )

        if is_midjourney:
            from onemin._polling import apoll_job
            job_id: str = response.get("aiRecord", {}).get("id", "")
            response = await apoll_job(
                self._client._http,
                self._client._base_url,
                self._client._api_key,
                job_id,
            )

        return self._parse_image_result(response, effective_model)

    async def ato_prompt(self, image: ImageInput, *, model: str = "gpt-4o", **kwargs: Any) -> ImageResult:
        """Convert an image to a text description asynchronously.

        Args:
            image: Image file or URL to describe.
            model: Model to use (default "gpt-4o").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult whose ``url`` field contains the description text.

        Example:
            result = await client.image.ato_prompt("https://example.com/photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_TO_PROMPT", image, model, kwargs)

    async def avariation(self, image: ImageInput, *, model: str = "dall-e-2", n: int = 1, **kwargs: Any) -> ImageResult:
        """Generate a variation of an existing image asynchronously.

        Args:
            image: Source image file or URL.
            model: Model to use (default "dall-e-2").
            n: Number of variations to generate (default 1).
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the variation URL(s).

        Example:
            result = await client.image.avariation("photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_VARIATOR", image, model, {"n": n, **kwargs})

    async def aupscale(self, image: ImageInput, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Upscale an image to higher resolution asynchronously.

        Args:
            image: Image file or URL to upscale.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the upscaled image URL.

        Example:
            result = await client.image.aupscale("photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_UPSCALER", image, model, kwargs)

    async def aextend(self, image: ImageInput, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Extend the canvas of an image outward asynchronously.

        Args:
            image: Image file or URL to extend.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject (e.g. direction).

        Returns:
            An ImageResult with the extended image URL.

        Example:
            result = await client.image.aextend("photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_EXTENDER", image, model, kwargs)

    async def aremove_background(self, image: ImageInput, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Remove the background from an image asynchronously.

        Args:
            image: Image file or URL.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the background-removed image URL.

        Example:
            result = await client.image.aremove_background("photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("BACKGROUND_REMOVER", image, model, kwargs)

    async def areplace_background(self, image: ImageInput, prompt: str, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Replace the background of an image with a new scene asynchronously.

        Args:
            image: Image file or URL with the foreground subject.
            prompt: Text description of the new background.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the new-background image URL.

        Example:
            result = await client.image.areplace_background("photo.jpg", "a sunny beach")
            print(result.url)
        """
        return await self._aupload_and_call("BACKGROUND_REPLACER", image, model, {"prompt": prompt, **kwargs})

    async def aremove_text(self, image: ImageInput, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Remove text overlays from an image asynchronously.

        Args:
            image: Image file or URL containing text to remove.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the text-removed image URL.

        Example:
            result = await client.image.aremove_text("photo.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("TEXT_REMOVER", image, model, kwargs)

    async def aremove_object(self, image: ImageInput, prompt: str, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Remove a specified object from an image asynchronously.

        Args:
            image: Image file or URL.
            prompt: Description of the object to remove.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the object-removed image URL.

        Example:
            result = await client.image.aremove_object("photo.jpg", "the red car")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_OBJECT_REMOVER", image, model, {"prompt": prompt, **kwargs})

    async def asearch_and_replace(
        self, image: ImageInput, search_prompt: str, replace_prompt: str,
        *, model: str = "dall-e-2", **kwargs: Any
    ) -> ImageResult:
        """Find an element in an image and replace it asynchronously.

        Args:
            image: Image file or URL.
            search_prompt: Description of the element to find and replace.
            replace_prompt: Description of what to replace it with.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the modified image URL.

        Example:
            result = await client.image.asearch_and_replace("photo.jpg", "cat", "dog")
            print(result.url)
        """
        return await self._aupload_and_call(
            "SEARCH_AND_REPLACE", image, model,
            {"searchPrompt": search_prompt, "replacePrompt": replace_prompt, **kwargs},
        )

    async def ainpaint(
        self, image: ImageInput, mask: ImageInput, prompt: str,
        *, model: str = "dall-e-2", **kwargs: Any
    ) -> ImageResult:
        """Fill a masked area of an image guided by a text prompt asynchronously.

        Args:
            image: Source image file or URL.
            mask: Mask image file or URL (white = area to fill, black = keep).
            prompt: Text description of what to generate in the masked area.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the inpainted image URL.

        Example:
            result = await client.image.ainpaint("photo.jpg", "mask.jpg", "a red rose")
            print(result.url)
        """
        image_url = await self._aupload(image)
        mask_url = await self._aupload(mask)
        payload: dict[str, Any] = {
            "type": "IMAGE_INPAINTER",
            "model": model,
            "promptObject": {
                "imageUrl": image_url,
                "maskUrl": mask_url,
                "prompt": prompt,
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    async def aedit_text(self, image: ImageInput, text_config: dict[str, Any], *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Edit text content within an image asynchronously.

        Args:
            image: Image file or URL containing text to edit.
            text_config: Configuration dict describing the text edits.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the text-edited image URL.

        Example:
            result = await client.image.aedit_text("photo.jpg", {"text": "Hello", "x": 10, "y": 10})
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_EDITOR", image, model, {"textConfig": text_config, **kwargs})

    async def aswap_face(
        self, source_image: ImageInput, target_image: ImageInput,
        *, model: str = "dall-e-2", **kwargs: Any
    ) -> ImageResult:
        """Swap a face from the source image onto the target image asynchronously.

        Args:
            source_image: Image file or URL containing the face to copy.
            target_image: Image file or URL to place the face onto.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the face-swapped image URL.

        Example:
            result = await client.image.aswap_face("source.jpg", "target.jpg")
            print(result.url)
        """
        source_url = await self._aupload(source_image)
        target_url = await self._aupload(target_image)
        payload: dict[str, Any] = {
            "type": "FACE_SWAPPER",
            "model": model,
            "promptObject": {
                "sourceImageUrl": source_url,
                "targetImageUrl": target_url,
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        return self._parse_image_result(response, model)

    async def agenerate_3d(self, image: ImageInput, *, model: str = "dall-e-2", **kwargs: Any) -> ImageResult:
        """Generate a 3D representation of an object from an image asynchronously.

        Args:
            image: Image file or URL of the object to convert to 3D.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the 3D model URL.

        Example:
            result = await client.image.agenerate_3d("object.jpg")
            print(result.url)
        """
        return await self._aupload_and_call("IMAGE_3D_GENERATOR", image, model, kwargs)

    def generate_3d(
        self,
        image: ImageInput,
        *,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> ImageResult:
        """Generate a 3D representation of an object from an image.

        Args:
            image: Image file or URL of the object to convert to 3D.
            model: Model to use (default "dall-e-2").
            **kwargs: Additional parameters forwarded to promptObject.

        Returns:
            An ImageResult with the 3D model URL.

        Example:
            result = client.image.generate_3d("object.jpg")
            print(result.url)
        """
        return self._upload_and_call("IMAGE_3D_GENERATOR", image, model, kwargs)
