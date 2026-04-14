"""Base resource class for all 1min.ai API domain resources.

Each domain resource inherits from BaseResource, which provides:
- A reference to the parent client for HTTP calls
- Per-domain timeout lookup from DOMAIN_TIMEOUTS (INFRA-07)
- A low-level raw() passthrough to /api/features (or overridden endpoint)
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from onemin._constants import DOMAIN_TIMEOUTS

if TYPE_CHECKING:
    from onemin._base_client import BaseOneMinClient


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
        self._timeout = DOMAIN_TIMEOUTS.get(self._domain, 30.0)

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
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
