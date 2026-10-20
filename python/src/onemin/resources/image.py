"""Image domain resource for the 1min.ai API.

Domain timeout: 90s (per INFRA-07) — image generation takes significant time.

Provides 14 public methods:
  generate, to_prompt, variation, upscale, extend,
  remove_background, replace_background, remove_text,
  remove_object, search_and_replace, inpaint, edit,
  swap_face, generate_3d.

All editing methods follow the upload-then-feature pattern:
  1. Upload the image file to /api/assets to get an asset key.
  2. POST to /api/features with the asset key in promptObject.

Every method works with any model the API lists for its feature (see
``FEATURE_MODELS``). ``model=None`` picks ``DEFAULT_MODELS[feature]``, and the
fields that default model requires are filled in for you. Other models take
their own fields -- pass them as keyword arguments; they go into promptObject
unchanged. Field reference per model: https://docs.1min.ai/docs/api/intro
"""

from __future__ import annotations

from typing import Any, Union

from onemin._file_upload import FileInput
from onemin._models_data import DEFAULT_MODELS
from onemin.models import ImageResult
from onemin.resources._base_resource import BaseResource, feature_payload, result_items

# ImageInput accepts a file to upload (path, bytes, (filename, bytes)), an
# http(s) URL (downloaded, then uploaded), or the asset key of an earlier
# upload or result (e.g. ``result.keys[0]``), which is used as-is.
ImageInput = Union[FileInput, str]

# Fields each default model requires (or misbehaves without), keyed by
# (feature, model). Only applied when that exact model is used; caller
# keyword arguments override them.
_MODEL_DEFAULTS: dict[tuple[str, str], dict[str, Any]] = {
    ("IMAGE_GENERATOR", "stable-diffusion-xl-1024-v1-0"): {
        "samples": 1, "size": "1024x1024", "cfg_scale": 7, "steps": 30, "seed": 0,
    },
    ("IMAGE_UPSCALER", "stable-image"): {"output_format": "png"},
    ("IMAGE_EXTENDER", "stable-image"): {"output_format": "png"},
    ("IMAGE_INPAINTER", "stable-image"): {"output_format": "png"},
    ("IMAGE_OBJECT_REMOVER", "stable-image"): {"output_format": "png"},
    ("BACKGROUND_REMOVER", "stable-image"): {"output_format": "png"},
    ("SEARCH_AND_REPLACE", "stable-image"): {"output_format": "png"},
    ("IMAGE_EDITOR", "gpt-image-1-mini"): {
        "size": "1024x1024", "n": 1, "quality": "medium",
    },
    ("BACKGROUND_REPLACER", "gpt-image-1-mini"): {
        "size": "1024x1024", "quality": "medium",
    },
    ("FACE_SWAPPER", "Qubico/image-toolkit"): {"output_format": "png"},
}


def _parse_image_result(ai_record: dict[str, Any], model: str) -> ImageResult:
    """Build an ImageResult from a finished aiRecord.

    Results live at ``aiRecord.aiRecordDetail.resultObject`` as a list: asset
    keys for generated files, or text for IMAGE_TO_PROMPT. ``temporaryUrl`` is
    a signed, time-limited download link for the first generated file.
    """
    items = result_items(ai_record)
    url: str = ai_record.get("temporaryUrl") or ""
    if ai_record.get("type") == "IMAGE_TO_PROMPT":
        return ImageResult(
            url="", model=model, content="\n".join(str(i) for i in items),
            metadata=ai_record,
        )
    return ImageResult(
        url=url,
        model=model,
        urls=[url] if url else None,
        keys=[str(i) for i in items] or None,
        metadata=ai_record,
    )


class ImageResource(BaseResource):
    """Image generation and editing operations.

    Domain timeout: 90s (per INFRA-07).

    Methods:
        generate: Generate an image from a text prompt.
        to_prompt: Convert an image to a text description.
        variation: Generate a variation of an existing image.
        upscale: Upscale an image to higher resolution.
        extend: Extend the canvas of an image outward.
        remove_background: Remove the background from an image.
        replace_background: Replace the background with a new scene.
        remove_text: Remove text overlays from an image.
        remove_object: Remove the masked object from an image.
        search_and_replace: Find and replace an element in an image.
        inpaint: Fill a masked area in an image.
        edit: Edit an image following a text instruction.
        swap_face: Swap a face from one image to another.
        generate_3d: Generate a 3D model (.glb) of the pictured object.

    Each has an async twin prefixed with ``a`` for ``AsyncOneMinClient``.
    """

    _domain = "image"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run(
        self,
        feature: str,
        model: str | None,
        images: dict[str, ImageInput],
        fields: dict[str, Any],
    ) -> ImageResult:
        """Upload ``images`` (promptObject field -> image), call the feature, parse."""
        uploaded = {name: self._upload_asset(image) for name, image in images.items()}
        payload, model = feature_payload(
            feature, model, {**uploaded, **fields}, _MODEL_DEFAULTS
        )
        return _parse_image_result(self._call_feature(payload), model)

    async def _arun(
        self,
        feature: str,
        model: str | None,
        images: dict[str, ImageInput],
        fields: dict[str, Any],
    ) -> ImageResult:
        """Async version of :meth:`_run`."""
        uploaded = {
            name: await self._aupload_asset(image) for name, image in images.items()
        }
        payload, model = feature_payload(
            feature, model, {**uploaded, **fields}, _MODEL_DEFAULTS
        )
        return _parse_image_result(await self._acall_feature(payload), model)

    @staticmethod
    def _generate_fields(
        prompt: str, model: str | None, width: int | None, height: int | None,
        n: int | None, kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Map generate()'s width/height/n onto what the chosen model expects."""
        fields: dict[str, Any] = {"prompt": prompt}
        model = model or DEFAULT_MODELS["IMAGE_GENERATOR"]
        if model == "stable-diffusion-xl-1024-v1-0":
            if width or height:
                fields["size"] = f"{width or 1024}x{height or 1024}"
            if n:
                fields["samples"] = n
        else:
            # Other models name these differently (size, aspect_ratio,
            # num_outputs, ...): only forward what the caller set explicitly.
            for name, value in (("width", width), ("height", height), ("n", n)):
                if value is not None:
                    fields[name] = value
        fields.update(kwargs)
        return fields

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        width: int | None = None,
        height: int | None = None,
        n: int | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_GENERATOR"]``
                (Stable Diffusion XL). Any id in
                ``FEATURE_MODELS["IMAGE_GENERATOR"]`` works.
            width: Image width. For the default model, width x height must be
                one of its supported sizes (1024x1024, 1344x768, 768x1344, ...).
            height: Image height.
            n: Number of images.
            **kwargs: Model-specific promptObject fields (e.g. ``aspect_ratio``
                for Flux, ``size``/``quality`` for gpt-image, ``style_preset``
                for Stable Diffusion).

        Returns:
            ImageResult: ``url`` is a temporary download link for the first
            image, ``keys`` the asset keys of all images.

        Example:
            result = client.image.generate("A cat astronaut on Mars")
            print(result.url)
        """
        fields = self._generate_fields(prompt, model, width, height, n, kwargs)
        return self._run("IMAGE_GENERATOR", model, {}, fields)

    def to_prompt(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Describe an image as a text prompt.

        Args:
            image: Image to describe (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_TO_PROMPT"]``.
            **kwargs: Extra promptObject fields.

        Returns:
            ImageResult with the description in ``content``.

        Example:
            result = client.image.to_prompt("/path/to/photo.jpg")
            print(result.content)
        """
        return self._run("IMAGE_TO_PROMPT", model, {"imageUrl": image}, kwargs)

    def variation(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Generate a variation of an existing image.

        Args:
            image: Source image (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_VARIATOR"]``.
            **kwargs: Extra promptObject fields (e.g. ``num_outputs``,
                ``aspect_ratio`` for the default Flux Redux model).

        Example:
            result = client.image.variation("/path/to/photo.jpg")
            print(result.url)
        """
        return self._run("IMAGE_VARIATOR", model, {"imageUrl": image}, kwargs)

    def upscale(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Upscale an image to a higher resolution.

        Args:
            image: Image to upscale (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_UPSCALER"]``.
            **kwargs: Extra promptObject fields (e.g. ``output_format``).

        Example:
            result = client.image.upscale("/path/to/small.jpg")
            print(result.url)
        """
        return self._run("IMAGE_UPSCALER", model, {"imageUrl": image}, kwargs)

    def extend(
        self,
        image: ImageInput,
        *,
        left: int = 0,
        right: int = 0,
        up: int = 0,
        down: int = 0,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Extend the canvas of an image outward (outpainting).

        Args:
            image: Image to extend (path, bytes, URL, or asset key).
            left: Pixels to add on the left (0-2000).
            right: Pixels to add on the right (0-2000).
            up: Pixels to add on top (0-2000).
            down: Pixels to add at the bottom (0-2000).
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_EXTENDER"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.extend("/path/to/photo.jpg", left=200, right=200)
            print(result.url)
        """
        sides = {"left": left, "right": right, "up": up, "down": down}
        fields = {**{k: v for k, v in sides.items() if v}, **kwargs}
        return self._run("IMAGE_EXTENDER", model, {"imageUrl": image}, fields)

    def remove_background(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Remove the background from an image.

        Args:
            image: Image to process (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["BACKGROUND_REMOVER"]``.
            **kwargs: Extra promptObject fields (e.g. ``output_format``).

        Example:
            result = client.image.remove_background("/path/to/portrait.jpg")
            print(result.url)
        """
        return self._run("BACKGROUND_REMOVER", model, {"imageUrl": image}, kwargs)

    def replace_background(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Replace the background of an image with a described scene.

        Args:
            image: Image to process (path, bytes, URL, or asset key).
            prompt: Description of the new background.
            model: Model id; defaults to ``DEFAULT_MODELS["BACKGROUND_REPLACER"]``.
            **kwargs: Extra promptObject fields (e.g. ``quality``, ``size``).

        Example:
            result = client.image.replace_background("portrait.jpg", "a sunny beach")
            print(result.url)
        """
        return self._run(
            "BACKGROUND_REPLACER", model, {"imageUrl": image}, {"prompt": prompt, **kwargs}
        )

    def remove_text(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Remove text overlays from an image.

        Args:
            image: Image to process (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["TEXT_REMOVER"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.remove_text("/path/to/meme.jpg")
            print(result.url)
        """
        return self._run("TEXT_REMOVER", model, {"imageUrl": image}, kwargs)

    def remove_object(
        self,
        image: ImageInput,
        mask: ImageInput,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Remove the masked object from an image.

        Args:
            image: Image to process (path, bytes, URL, or asset key).
            mask: Mask image, same size: white = remove, black = keep.
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_OBJECT_REMOVER"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.remove_object("photo.jpg", "mask.png")
            print(result.url)
        """
        return self._run(
            "IMAGE_OBJECT_REMOVER", model, {"imageUrl": image, "maskUrl": mask}, kwargs
        )

    def search_and_replace(
        self,
        image: ImageInput,
        search_prompt: str,
        replace_prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Find an element in an image and replace it with something else.

        Args:
            image: Image to process (path, bytes, URL, or asset key).
            search_prompt: Description of the element to find.
            replace_prompt: Description of what to put in its place.
            model: Model id; defaults to ``DEFAULT_MODELS["SEARCH_AND_REPLACE"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.search_and_replace("photo.jpg", "red car", "blue bicycle")
            print(result.url)
        """
        fields = {"search_prompt": search_prompt, "prompt": replace_prompt, **kwargs}
        return self._run("SEARCH_AND_REPLACE", model, {"imageUrl": image}, fields)

    def inpaint(
        self,
        image: ImageInput,
        mask: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Fill a masked area of an image with generated content.

        Args:
            image: Source image (path, bytes, URL, or asset key).
            mask: Mask image, same size: white = edit, black = preserve.
            prompt: Description of what to generate in the masked area.
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_INPAINTER"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.inpaint("photo.jpg", "mask.png", "a blue sky")
            print(result.url)
        """
        return self._run(
            "IMAGE_INPAINTER", model, {"imageUrl": image, "maskUrl": mask},
            {"prompt": prompt, **kwargs},
        )

    def edit(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Edit an image following a text instruction.

        Args:
            image: Image to edit (path, bytes, URL, or asset key).
            prompt: The change to make (e.g. "turn it into a watercolor").
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_EDITOR"]``.
            **kwargs: Extra promptObject fields (e.g. ``quality``, ``size``).

        Example:
            result = client.image.edit("photo.jpg", "make it a watercolor painting")
            print(result.url)
        """
        return self._run(
            "IMAGE_EDITOR", model, {"imageUrl": image}, {"prompt": prompt, **kwargs}
        )

    def swap_face(
        self,
        source_image: ImageInput,
        target_image: ImageInput,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Put the face from ``source_image`` onto ``target_image``.

        Args:
            source_image: Image containing the face to transfer.
            target_image: Image whose face is replaced.
            model: Model id; defaults to ``DEFAULT_MODELS["FACE_SWAPPER"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.swap_face("my_face.jpg", "movie_poster.jpg")
            print(result.url)
        """
        images = {"swapImageUrl": source_image, "targetImageUrl": target_image}
        return self._run("FACE_SWAPPER", model, images, kwargs)

    def generate_3d(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Generate a 3D model (.glb) of the object in an image.

        Args:
            image: Source image (path, bytes, URL, or asset key).
            model: Model id; defaults to ``DEFAULT_MODELS["IMAGE_3D_GENERATOR"]``.
            **kwargs: Extra promptObject fields.

        Example:
            result = client.image.generate_3d("/path/to/object.jpg")
            client.image.download(result, "object.glb")
        """
        return self._run("IMAGE_3D_GENERATOR", model, {"imageUrl": image}, kwargs)

    # ------------------------------------------------------------------
    # Async methods (same arguments and results as the sync versions)
    # ------------------------------------------------------------------

    async def agenerate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        width: int | None = None,
        height: int | None = None,
        n: int | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`generate`."""
        fields = self._generate_fields(prompt, model, width, height, n, kwargs)
        return await self._arun("IMAGE_GENERATOR", model, {}, fields)

    async def ato_prompt(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`to_prompt`."""
        return await self._arun("IMAGE_TO_PROMPT", model, {"imageUrl": image}, kwargs)

    async def avariation(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`variation`."""
        return await self._arun("IMAGE_VARIATOR", model, {"imageUrl": image}, kwargs)

    async def aupscale(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`upscale`."""
        return await self._arun("IMAGE_UPSCALER", model, {"imageUrl": image}, kwargs)

    async def aextend(
        self,
        image: ImageInput,
        *,
        left: int = 0,
        right: int = 0,
        up: int = 0,
        down: int = 0,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`extend`."""
        sides = {"left": left, "right": right, "up": up, "down": down}
        fields = {**{k: v for k, v in sides.items() if v}, **kwargs}
        return await self._arun("IMAGE_EXTENDER", model, {"imageUrl": image}, fields)

    async def aremove_background(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`remove_background`."""
        return await self._arun("BACKGROUND_REMOVER", model, {"imageUrl": image}, kwargs)

    async def areplace_background(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`replace_background`."""
        return await self._arun(
            "BACKGROUND_REPLACER", model, {"imageUrl": image}, {"prompt": prompt, **kwargs}
        )

    async def aremove_text(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`remove_text`."""
        return await self._arun("TEXT_REMOVER", model, {"imageUrl": image}, kwargs)

    async def aremove_object(
        self,
        image: ImageInput,
        mask: ImageInput,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`remove_object`."""
        return await self._arun(
            "IMAGE_OBJECT_REMOVER", model, {"imageUrl": image, "maskUrl": mask}, kwargs
        )

    async def asearch_and_replace(
        self,
        image: ImageInput,
        search_prompt: str,
        replace_prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`search_and_replace`."""
        fields = {"search_prompt": search_prompt, "prompt": replace_prompt, **kwargs}
        return await self._arun("SEARCH_AND_REPLACE", model, {"imageUrl": image}, fields)

    async def ainpaint(
        self,
        image: ImageInput,
        mask: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`inpaint`."""
        return await self._arun(
            "IMAGE_INPAINTER", model, {"imageUrl": image, "maskUrl": mask},
            {"prompt": prompt, **kwargs},
        )

    async def aedit(
        self,
        image: ImageInput,
        prompt: str,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`edit`."""
        return await self._arun(
            "IMAGE_EDITOR", model, {"imageUrl": image}, {"prompt": prompt, **kwargs}
        )

    async def aswap_face(
        self,
        source_image: ImageInput,
        target_image: ImageInput,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> ImageResult:
        """Async version of :meth:`swap_face`."""
        images = {"swapImageUrl": source_image, "targetImageUrl": target_image}
        return await self._arun("FACE_SWAPPER", model, images, kwargs)

    async def agenerate_3d(
        self, image: ImageInput, *, model: str | None = None, **kwargs: Any
    ) -> ImageResult:
        """Async version of :meth:`generate_3d`."""
        return await self._arun("IMAGE_3D_GENERATOR", model, {"imageUrl": image}, kwargs)
