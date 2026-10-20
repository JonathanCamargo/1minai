"""Base resource class for all 1min.ai API domain resources.

Each domain resource inherits from BaseResource, which provides:
- A reference to the parent client for HTTP calls
- Per-domain timeout lookup from DOMAIN_TIMEOUTS (INFRA-07)
- A low-level raw() passthrough to /api/features (or overridden endpoint)
"""

from __future__ import annotations

import os
from typing import Any, TYPE_CHECKING

from onemin._constants import DOMAIN_TIMEOUTS
from onemin._exceptions import APIError
from onemin._models_data import DEFAULT_MODELS
from onemin._polling import apoll_job, poll_job

if TYPE_CHECKING:
    from onemin._base_client import BaseOneMinClient


def is_asset_key(file: Any) -> bool:
    """A string that is neither a URL nor an existing file is an asset key."""
    return (
        isinstance(file, str)
        and not file.startswith(("http://", "https://"))
        and not os.path.exists(file)
    )


def _url_filename(url: str) -> str:
    return url.split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1] or "file"


def feature_payload(
    feature: str,
    model: str | None,
    fields: dict[str, Any],
    model_defaults: dict[tuple[str, str], dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], str]:
    """Build a /api/features body.

    ``model=None`` resolves to ``DEFAULT_MODELS[feature]``. ``model_defaults``
    maps (feature, model) to the fields that model requires; they are applied
    only for that exact model and overridden by ``fields``.
    """
    model = model or DEFAULT_MODELS[feature]
    defaults = (model_defaults or {}).get((feature, model), {})
    payload = {"type": feature, "model": model, "promptObject": {**defaults, **fields}}
    return payload, model


def result_items(ai_record: dict[str, Any]) -> list[Any]:
    """Return ``aiRecordDetail.resultObject`` as a list (asset keys or text)."""
    detail = ai_record.get("aiRecordDetail") or {}
    items = detail.get("resultObject")
    if items is None:
        items = ai_record.get("resultObject")
    if isinstance(items, list):
        return items
    return [] if items is None else [items]


def _checked(response: dict[str, Any]) -> dict[str, Any]:
    """Return the aiRecord of a finished response, raising if it failed."""
    record = response.get("aiRecord") or {}
    if str(record.get("status", "")).upper() == "FAILURE":
        detail = (record.get("aiRecordDetail") or {}).get("resultObject")
        message = detail.get("message") if isinstance(detail, dict) else detail
        raise APIError(f"{record.get('type')} failed: {message}", status_code=0)
    return record


class BaseResource:
    """Base class for all domain resources.

    Each resource has a domain name (e.g., 'image', 'text') used to
    look up the per-domain timeout default from DOMAIN_TIMEOUTS (INFRA-07).

    Subclasses set the ``_domain`` class attribute to configure their
    timeout automatically on instantiation.
    """

    _domain: str = "text"  # Subclasses override with their domain name

    def __init__(self, client: BaseOneMinClient) -> None:
        self._client = client
        # The domain default is a floor: a longer client-level timeout wins,
        # so OneMinClient(timeout=300) is honoured for slow long-document calls.
        self._timeout = max(DOMAIN_TIMEOUTS.get(self._domain, 30.0), client.timeout)

    def _get_http_client(self):
        """Return the underlying httpx client (sync or async).

        AsyncOneMinClient stores the async client in ``_http``.
        Sync OneMinClient stores the sync client in ``_client``.
        """
        return getattr(self._client, '_http', getattr(self._client, '_client', None))

    def _is_async(self) -> bool:
        """Check if attached to an async client.

        Returns True when the parent client is an AsyncOneMinClient (which
        exposes ``_http`` instead of ``_client``).
        """
        return hasattr(self._client, '_http')

    # ------------------------------------------------------------------
    # /api/features helpers shared by the image, audio and video resources
    # ------------------------------------------------------------------

    def _upload_asset(self, file: Any) -> str:
        """Return the asset key for a file, uploading it when needed.

        Accepts a path, bytes, a (filename, bytes) tuple, an http(s) URL
        (downloaded and re-uploaded: the API only reads its own asset store),
        or an existing asset key, which is returned unchanged.
        """
        if is_asset_key(file):
            return file
        if isinstance(file, str) and file.startswith(("http://", "https://")):
            fetched = self._client._client.get(file, follow_redirects=True)
            fetched.raise_for_status()
            file = (_url_filename(file), fetched.content)
        return self._client.asset.upload(file).metadata["key"]

    async def _aupload_asset(self, file: Any) -> str:
        """Async version of :meth:`_upload_asset`."""
        if is_asset_key(file):
            return file
        if isinstance(file, str) and file.startswith(("http://", "https://")):
            fetched = await self._client._http.get(file, follow_redirects=True)
            fetched.raise_for_status()
            file = (_url_filename(file), fetched.content)
        return (await self._client.asset.aupload(file)).metadata["key"]

    def _call_feature(
        self, payload: dict[str, Any], *, background: bool = False
    ) -> dict[str, Any]:
        """POST to /api/features and return the finished aiRecord.

        With ``background=True`` the request is sent with ``"async": true`` and
        the result polled from /api/results/{uuid} -- needed for slow jobs
        (video) that outlive the gateway timeout.

        Raises:
            APIError: If the record finishes with status FAILURE.
            TimeoutError: If a background job does not finish in time.
        """
        if background:
            payload = {**payload, "async": True}
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        record = response.get("aiRecord") or {}
        if str(record.get("status", "")).upper() == "PROCESSING":
            response = poll_job(
                self._client._client,
                self._client._base_url,
                self._client._api_key,
                record["uuid"],
                max_wait=max(self._timeout * 3, 300.0),
            )
        return _checked(response)

    async def _acall_feature(
        self, payload: dict[str, Any], *, background: bool = False
    ) -> dict[str, Any]:
        """Async version of :meth:`_call_feature`."""
        if background:
            payload = {**payload, "async": True}
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout
        )
        record = response.get("aiRecord") or {}
        if str(record.get("status", "")).upper() == "PROCESSING":
            response = await apoll_job(
                self._client._http,
                self._client._base_url,
                self._client._api_key,
                record["uuid"],
                max_wait=max(self._timeout * 3, 300.0),
            )
        return _checked(response)

    def download(self, result: Any, path: str | os.PathLike[str]) -> str:
        """Save the generated file of ``result`` (its ``url``) to ``path``.

        Result URLs are signed links that expire, so download promptly.
        """
        import httpx

        response = httpx.get(result.url, timeout=self._timeout, follow_redirects=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        return str(path)

    def raw(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Low-level passthrough -- send any payload to /api/features.

        Uses the per-domain timeout default (INFRA-07). Override in
        subclasses if the endpoint differs (e.g., conversations, assets).

        Args:
            payload: Raw request body to send to the API.

        Returns:
            Raw API response as a dictionary.
        """
        return self._client._request(
            "POST", "/api/chat-with-ai", json=payload, timeout=self._timeout,
        )
