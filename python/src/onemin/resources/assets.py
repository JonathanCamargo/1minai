"""Asset domain resource for the 1min.ai API."""
from __future__ import annotations

from typing import Any

import httpx

from onemin.resources._base_resource import BaseResource
from onemin.models import AssetResult
from onemin._file_upload import FileInput, normalize_file
from onemin._constants import API_KEY_HEADER


class AssetResource(BaseResource):
    """Asset management operations. Uses /api/assets endpoint."""

    _domain = "asset"

    def raw(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Low-level passthrough to /api/assets (POST).

        Args:
            payload: Raw request body to send to the assets API.

        Returns:
            Raw API response as a dictionary.

        Example:
            response = client.asset.raw({"some": "payload"})
            print(response)
        """
        return self._client._request(
            "POST", "/api/assets", json=payload, timeout=self._timeout,
        )

    def upload(self, file: FileInput, **kwargs: Any) -> AssetResult:
        """Upload a file to /api/assets and return AssetResult.

        Args:
            file: File to upload — bytes, path string, Path object, or (filename, bytes) tuple.
            **kwargs: Ignored (reserved for future options).

        Returns:
            AssetResult with url, asset_id, and content_type.

        Example:
            result = client.asset.upload("/path/to/image.jpg")
            print(result.url)
        """
        filename, content = normalize_file(file)
        response = self._client._client.post(
            f"{self._client._base_url}/api/assets",
            headers={API_KEY_HEADER: self._client._api_key},
            files={"asset": (filename, content)},
            timeout=httpx.Timeout(self._timeout),
        )
        response.raise_for_status()
        data = response.json()
        asset = data.get("asset", {})
        return AssetResult(
            url=asset.get("location", ""),
            asset_id=asset.get("id", ""),
            content_type=asset.get("contentType"),
            metadata=asset,
        )

    async def aupload(self, file: FileInput, **kwargs: Any) -> AssetResult:
        """Upload a file to /api/assets asynchronously and return AssetResult.

        Args:
            file: File to upload — bytes, path string, Path object, or (filename, bytes) tuple.
            **kwargs: Ignored (reserved for future options).

        Returns:
            AssetResult with url, asset_id, and content_type.

        Example:
            result = await client.asset.aupload("/path/to/image.jpg")
            print(result.url)
        """
        from onemin._file_upload import async_upload_file
        # async_upload_file returns the URL string directly; we need full asset data
        # Use async httpx client directly for multipart upload to get full response
        filename, content = normalize_file(file)
        response = await self._client._http.post(
            f"{self._client._base_url}/api/assets",
            headers={API_KEY_HEADER: self._client._api_key},
            files={"asset": (filename, content)},
            timeout=httpx.Timeout(self._timeout),
        )
        response.raise_for_status()
        data = response.json()
        asset = data.get("asset", {})
        return AssetResult(
            url=asset.get("location", ""),
            asset_id=asset.get("id", ""),
            content_type=asset.get("contentType"),
            metadata=asset,
        )

    async def alist(self, **kwargs: Any) -> list[dict[str, Any]]:
        """List available assets asynchronously.

        Args:
            **kwargs: Query parameters (pagination, filters).

        Returns:
            List of asset dicts from the API.

        Example:
            assets = await client.asset.alist()
            for a in assets:
                print(a.get("id"))
        """
        return await self._client._request(
            "GET", "/api/assets", timeout=self._timeout, params=kwargs if kwargs else None,
        )

    async def aget(self, asset_id: str) -> AssetResult:
        """Get a single asset by ID asynchronously.

        Args:
            asset_id: The asset ID to retrieve.

        Returns:
            AssetResult with url, asset_id, and content_type.

        Example:
            result = await client.asset.aget("asset-id-123")
            print(result.url)
        """
        data = await self._client._request(
            "GET", f"/api/assets/{asset_id}", timeout=self._timeout,
        )
        asset = data.get("asset", data)
        return AssetResult(
            url=asset.get("location", asset.get("url", "")),
            asset_id=asset.get("id", asset_id),
            content_type=asset.get("contentType"),
            metadata=asset,
        )

    def list(self, **kwargs: Any) -> list[dict[str, Any]]:
        """List available assets.

        Args:
            **kwargs: Query parameters (pagination, filters).

        Returns:
            List of asset dicts from the API.

        Example:
            assets = client.asset.list()
            for a in assets:
                print(a.get("id"))
        """
        return self._client._request(
            "GET", "/api/assets", timeout=self._timeout, params=kwargs if kwargs else None,
        )

    def get(self, asset_id: str) -> AssetResult:
        """Get a single asset by ID.

        Args:
            asset_id: The asset ID to retrieve.

        Returns:
            AssetResult with url, asset_id, and content_type.

        Example:
            result = client.asset.get("asset-id-123")
            print(result.url)
        """
        data = self._client._request(
            "GET", f"/api/assets/{asset_id}", timeout=self._timeout,
        )
        asset = data.get("asset", data)
        return AssetResult(
            url=asset.get("location", asset.get("url", "")),
            asset_id=asset.get("id", asset_id),
            content_type=asset.get("contentType"),
            metadata=asset,
        )
