"""File upload helper for the 1min.ai SDK.

Normalizes various file input types (bytes, path, tuple) and uploads them
to /api/assets via multipart POST, returning the URL string from the response.

The API returns the uploaded asset URL nested at response['asset']['location'].
"""

import os
from pathlib import Path
from typing import Any, Union

import httpx

from onemin._constants import API_KEY_HEADER
from onemin._exceptions import APIError

# FileInput accepts:
#   bytes           — raw bytes (filename defaults to "upload")
#   os.PathLike[str] — Path object: reads the file, uses basename as filename
#   str             — string path: reads the file, uses basename as filename
#   tuple[str, bytes] — explicit (filename, bytes) pair
FileInput = Union[bytes, "os.PathLike[str]", str, tuple[str, bytes]]

def normalize_file(file: FileInput) -> tuple[str, bytes]:
    """Normalize various file input types to a (filename, bytes) pair.

    Args:
        file: One of:
            - bytes: Raw bytes content (filename becomes "upload").
            - os.PathLike or str: File path — the file is read and the
              basename is used as the filename.
            - tuple[str, bytes]: Explicit (filename, content) pair.

    Returns:
        A (filename, bytes) tuple ready for multipart upload.

    Raises:
        TypeError: If the input type is not supported or a tuple is malformed.
    """
    if isinstance(file, bytes):
        return ("upload", file)

    if isinstance(file, (str, os.PathLike)):
        p = Path(file)
        return (p.name, p.read_bytes())

    if isinstance(file, tuple):
        if (
            len(file) == 2
            and isinstance(file[0], str)
            and isinstance(file[1], bytes)
        ):
            return (file[0], file[1])
        raise TypeError(
            f"File tuple must be (str, bytes) with exactly 2 elements, got {file!r}"
        )

    raise TypeError(f"Unsupported file input type: {type(file).__name__!r}")


def _extract_url(response_data: dict[str, Any]) -> str:
    """Extract uploaded asset URL from nested response: data['asset']['location'].

    Args:
        response_data: Parsed JSON response from the /api/assets endpoint.

    Returns:
        The URL string for the uploaded asset.

    Raises:
        APIError: If the expected nested structure is not found in the response.
    """
    asset = response_data.get("asset")
    if isinstance(asset, dict):
        location = asset.get("location")
        if isinstance(location, str) and location:
            return location
    raise APIError(
        f"No asset URL found in upload response. "
        f"Expected data['asset']['location']. "
        f"Response: {response_data}",
        status_code=0,
    )


def upload_file(
    client: httpx.Client,
    base_url: str,
    api_key: str,
    file: FileInput,
    *,
    timeout: float = 30.0,
) -> str:
    """Upload a file to /api/assets and return the URL string.

    Args:
        client: An httpx.Client instance (from BaseOneMinClient._client).
        base_url: The API base URL (e.g., "https://api.1min.ai").
        api_key: The 1min.ai API key for the API-KEY header.
        file: The file to upload — bytes, path, or (filename, bytes) tuple.
        timeout: Request timeout in seconds (default 30).

    Returns:
        The URL string of the uploaded asset.

    Raises:
        TypeError: If the file input type is not supported.
        httpx.HTTPStatusError: If the API returns a non-2xx status.
        APIError: If the response does not contain a recognized URL field.
    """
    filename, content = normalize_file(file)
    response = client.post(
        f"{base_url}/api/assets",
        headers={API_KEY_HEADER: api_key},
        files={"asset": (filename, content)},
        timeout=httpx.Timeout(timeout),
    )
    response.raise_for_status()
    return _extract_url(response.json())


async def async_upload_file(
    client: httpx.AsyncClient,
    base_url: str,
    api_key: str,
    file: FileInput,
    *,
    timeout: float = 30.0,
) -> str:
    """Async version: upload a file to /api/assets and return the URL string.

    Args:
        client: An httpx.AsyncClient instance.
        base_url: The API base URL (e.g., "https://api.1min.ai").
        api_key: The 1min.ai API key for the API-KEY header.
        file: The file to upload — bytes, path, or (filename, bytes) tuple.
        timeout: Request timeout in seconds (default 30).

    Returns:
        The URL string of the uploaded asset.

    Raises:
        TypeError: If the file input type is not supported.
        httpx.HTTPStatusError: If the API returns a non-2xx status.
        APIError: If the response does not contain a recognized URL field.
    """
    filename, content = normalize_file(file)
    response = await client.post(
        f"{base_url}/api/assets",
        headers={API_KEY_HEADER: api_key},
        files={"asset": (filename, content)},
        timeout=httpx.Timeout(timeout),
    )
    response.raise_for_status()
    return _extract_url(response.json())
