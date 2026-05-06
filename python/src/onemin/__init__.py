"""1min.ai Python SDK.

Provides the OneMinClient and a complete exception hierarchy for the 1min.ai API.

Usage:
    from onemin import OneMinClient
    client = OneMinClient(api_key="your-key")
    # or set the ONEMIN_API_KEY environment variable and call:
    client = OneMinClient()
"""

from onemin._version import __version__
from onemin._client import OneMinClient
from onemin._async_client import AsyncOneMinClient
from onemin._exceptions import (
    OneMinError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    BadRequestError,
    UnsupportedModelError,
    InternalServerError,
    ConnectionError,
    TimeoutError,
)
from onemin.models import (
    TextResult,
    ImageResult,
    AudioResult,
    VideoResult,
    WritingResult,
    ConversationResult,
    AssetResult,
)
from onemin.constants import Models

__all__ = [
    "__version__",
    "OneMinClient",
    "AsyncOneMinClient",
    "OneMinError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "BadRequestError",
    "UnsupportedModelError",
    "InternalServerError",
    "ConnectionError",
    "TimeoutError",
    "TextResult",
    "ImageResult",
    "AudioResult",
    "VideoResult",
    "WritingResult",
    "ConversationResult",
    "AssetResult",
    "Models",
]
