"""Tests for the file upload normalization and upload helpers."""

import io
import tempfile
from pathlib import Path

import httpx
import pytest
import respx

from onemin._file_upload import (
    FileInput,
    _extract_url,
    async_upload_file,
    normalize_file,
    upload_file,
)
from onemin._exceptions import APIError


# ---------------------------------------------------------------------------
# normalize_file tests
# ---------------------------------------------------------------------------


def test_normalize_bytes_returns_upload_filename():
    """normalize_file(b'data') should return ('upload', b'data')."""
    result = normalize_file(b"image data")
    assert result == ("upload", b"image data")


def test_normalize_path_object(tmp_path):
    """normalize_file(Path) reads the file and returns (filename, bytes)."""
    f = tmp_path / "test.png"
    f.write_bytes(b"\x89PNG\r\n")
    result = normalize_file(f)
    assert result == ("test.png", b"\x89PNG\r\n")


def test_normalize_str_path(tmp_path):
    """normalize_file('str/path') reads the file and returns (filename, bytes)."""
    f = tmp_path / "photo.jpg"
    f.write_bytes(b"JPEG data")
    result = normalize_file(str(f))
    assert result == ("photo.jpg", b"JPEG data")


def test_normalize_tuple_returns_as_is():
    """normalize_file(('name.png', b'bytes')) returns the tuple unchanged."""
    result = normalize_file(("my_image.png", b"image data"))
    assert result == ("my_image.png", b"image data")


def test_normalize_integer_raises_type_error():
    """normalize_file(12345) must raise TypeError."""
    with pytest.raises(TypeError):
        normalize_file(12345)  # type: ignore[arg-type]


def test_normalize_invalid_tuple_one_element_raises_type_error():
    """normalize_file(('only_name',)) must raise TypeError."""
    with pytest.raises(TypeError):
        normalize_file(("only_name",))  # type: ignore[arg-type]


def test_normalize_invalid_tuple_wrong_types_raises_type_error():
    """normalize_file((b'bytes', 'str')) must raise TypeError — wrong element types."""
    with pytest.raises(TypeError):
        normalize_file((b"bytes", "string"))  # type: ignore[arg-type]


def test_normalize_none_raises_type_error():
    """normalize_file(None) must raise TypeError."""
    with pytest.raises(TypeError):
        normalize_file(None)  # type: ignore[arg-type]


def test_normalize_list_raises_type_error():
    """normalize_file([]) must raise TypeError — list is not a valid input."""
    with pytest.raises(TypeError):
        normalize_file([])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _extract_url tests
# ---------------------------------------------------------------------------


def test_extract_url_nested_asset_location():
    """_extract_url should return data['asset']['location'] (nested path)."""
    result = _extract_url({"asset": {"location": "https://cdn.example.com/file.png"}})
    assert result == "https://cdn.example.com/file.png"


def test_extract_url_raises_api_error_when_asset_key_missing():
    """_extract_url must raise APIError when 'asset' key is absent."""
    with pytest.raises(APIError) as exc_info:
        _extract_url({"someOtherField": "value", "count": 1})
    assert "No asset URL found" in str(exc_info.value)
    # Should include the response body for debugging
    assert "someOtherField" in str(exc_info.value)


def test_extract_url_raises_api_error_when_location_missing():
    """_extract_url must raise APIError when asset['location'] is absent."""
    with pytest.raises(APIError) as exc_info:
        _extract_url({"asset": {"otherField": "value"}})
    assert "No asset URL found" in str(exc_info.value)


def test_extract_url_raises_api_error_when_location_empty():
    """_extract_url must raise APIError when asset['location'] is an empty string."""
    with pytest.raises(APIError):
        _extract_url({"asset": {"location": ""}})


def test_extract_url_raises_api_error_when_asset_not_dict():
    """_extract_url must raise APIError when 'asset' is not a dict."""
    with pytest.raises(APIError):
        _extract_url({"asset": "not-a-dict"})


# ---------------------------------------------------------------------------
# upload_file tests (sync, with respx mocking)
# ---------------------------------------------------------------------------


@respx.mock
def test_upload_file_posts_to_assets_and_returns_url():
    """upload_file sends multipart POST to /api/assets and returns the URL string."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(200, json={"asset": {"location": "development/images/abc.png"}})
    )
    client = httpx.Client()
    url = upload_file(client, "https://api.1min.ai", "test-api-key", b"image data")
    assert url == "development/images/abc.png"
    client.close()


@respx.mock
def test_upload_file_sends_correct_api_key_header():
    """upload_file must include the API-KEY header in the request."""
    received_headers = {}

    def capture(request):
        received_headers.update(dict(request.headers))
        return httpx.Response(200, json={"asset": {"location": "some/path.png"}})

    respx.post("https://api.1min.ai/api/assets").mock(side_effect=capture)
    client = httpx.Client()
    upload_file(client, "https://api.1min.ai", "my-secret-key", b"data")
    assert received_headers.get("api-key") == "my-secret-key"
    client.close()


@respx.mock
def test_upload_file_uses_filename_from_normalized_tuple():
    """upload_file passes the filename from a normalized (name, bytes) tuple."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(200, json={"asset": {"location": "uploads/audio.mp3"}})
    )
    client = httpx.Client()
    url = upload_file(client, "https://api.1min.ai", "key", ("audio.mp3", b"mp3 data"))
    assert url == "uploads/audio.mp3"
    client.close()


@respx.mock
def test_upload_file_raises_api_error_on_missing_url():
    """upload_file raises APIError when response has no recognized URL field."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(200, json={"unknownField": "value"})
    )
    client = httpx.Client()
    with pytest.raises(APIError) as exc_info:
        upload_file(client, "https://api.1min.ai", "key", b"data")
    assert "No asset URL found" in str(exc_info.value)
    client.close()


@respx.mock
def test_upload_file_raises_http_error_on_4xx():
    """upload_file propagates HTTP errors (e.g., 401) from /api/assets."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    client = httpx.Client()
    with pytest.raises(httpx.HTTPStatusError):
        upload_file(client, "https://api.1min.ai", "bad-key", b"data")
    client.close()


# ---------------------------------------------------------------------------
# async_upload_file tests
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.anyio
async def test_async_upload_file_posts_to_assets_and_returns_url():
    """async_upload_file sends multipart POST to /api/assets and returns the URL string."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(200, json={"asset": {"location": "development/images/async.png"}})
    )
    async with httpx.AsyncClient() as client:
        url = await async_upload_file(client, "https://api.1min.ai", "test-api-key", b"image data")
    assert url == "development/images/async.png"


@respx.mock
@pytest.mark.anyio
async def test_async_upload_file_raises_api_error_on_missing_url():
    """async_upload_file raises APIError when response has no recognized URL field."""
    respx.post("https://api.1min.ai/api/assets").mock(
        return_value=httpx.Response(200, json={"unrecognized": "value"})
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError):
            await async_upload_file(client, "https://api.1min.ai", "key", b"data")
