"""Conversation domain resource for the 1min.ai API."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING

from onemin.resources._base_resource import BaseResource
from onemin.models import ConversationResult

if TYPE_CHECKING:
    from onemin._base_client import BaseOneMinClient


class ConversationResource(BaseResource):
    """Conversation management. Uses /api/conversations endpoint."""

    _domain = "conversation"

    def raw(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a raw request to /api/conversations.

        Args:
            payload: Raw request body to send to the conversations API.

        Returns:
            Raw API response as a dictionary.

        Example:
            response = client.conversation.raw({"title": "Test", "type": "CHAT_WITH_AI", "model": "gpt-4o"})
            print(response)
        """
        return self._client._request(
            "POST", "/api/conversations", json=payload, timeout=self._timeout,
        )

    async def araw(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a raw request to /api/conversations asynchronously.

        Args:
            payload: Raw request body to send to the conversations API.

        Returns:
            Raw API response as a dictionary.

        Example:
            response = await client.conversation.araw({"title": "Test", "type": "CHAT_WITH_AI", "model": "gpt-4o"})
            print(response)
        """
        return await self._client._request(
            "POST", "/api/conversations", json=payload, timeout=self._timeout,
        )

    async def acreate(
        self,
        *,
        title: str = "Untitled",
        model: str = "gpt-4o",
        conversation_type: str = "CHAT_WITH_AI",
        **kwargs: Any,
    ) -> ConversationResult:
        """Create a new conversation asynchronously.

        Args:
            title: Conversation title.
            model: Model to use for the conversation.
            conversation_type: One of CHAT_WITH_AI, CHAT_WITH_IMAGE, CHAT_WITH_PDF.
            **kwargs: Extra fields for the request body.

        Returns:
            ConversationResult with conversation_id.

        Example:
            conv = await client.conversation.acreate(title="My Chat")
            print(conv.conversation_id)
        """
        payload: dict[str, Any] = {
            "title": title,
            "type": conversation_type,
            "model": model,
            **kwargs,
        }
        response = await self.araw(payload)
        conv = response.get("conversation", {})
        return ConversationResult(
            content="",
            conversation_id=conv.get("id", ""),
            model=model,
            metadata=conv,
        )

    async def asend(
        self,
        conversation_id: str,
        prompt: str,
        *,
        model: str = "gpt-4o",
        chat_history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> ConversationResult:
        """Send a message within an existing conversation asynchronously.

        Args:
            conversation_id: ID from a previous acreate() call.
            prompt: The message to send.
            model: Model name.
            chat_history: Previous messages as [{"role": "user"|"assistant", "message": "..."}].
            **kwargs: Extra fields for promptObject.

        Returns:
            ConversationResult with response content and conversation_id.

        Example:
            conv = await client.conversation.acreate()
            reply = await client.conversation.asend(conv.conversation_id, "Hello!")
            print(reply.content)
        """
        payload: dict[str, Any] = {
            "type": "CHAT_WITH_AI",
            "model": model,
            "conversationId": conversation_id,
            "promptObject": {
                "prompt": prompt,
                "chatList": chat_history or [],
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        ai_record = response.get("aiRecord", {})
        result_obj = ai_record.get("resultObject", {})
        content = (
            result_obj.get("message")
            or result_obj.get("content")
            or result_obj.get("text")
            or str(result_obj)
        )
        return ConversationResult(
            content=content,
            conversation_id=conversation_id,
            model=model,
            metadata=result_obj,
        )

    def create(
        self,
        *,
        title: str = "Untitled",
        model: str = "gpt-4o",
        conversation_type: str = "CHAT_WITH_AI",
        **kwargs: Any,
    ) -> ConversationResult:
        """Create a new conversation.

        Args:
            title: Conversation title.
            model: Model to use for the conversation.
            conversation_type: One of CHAT_WITH_AI, CHAT_WITH_IMAGE, CHAT_WITH_PDF.
            **kwargs: Extra fields for the request body.

        Returns:
            ConversationResult with conversation_id.

        Example:
            conv = client.conversation.create(title="My Chat")
            print(conv.conversation_id)
        """
        payload: dict[str, Any] = {
            "title": title,
            "type": conversation_type,
            "model": model,
            **kwargs,
        }
        response = self.raw(payload)
        conv = response.get("conversation", {})
        return ConversationResult(
            content="",
            conversation_id=conv.get("id", ""),
            model=model,
            metadata=conv,
        )

    def send(
        self,
        conversation_id: str,
        prompt: str,
        *,
        model: str = "gpt-4o",
        chat_history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> ConversationResult:
        """Send a message within an existing conversation.

        Args:
            conversation_id: ID from a previous create() call.
            prompt: The message to send.
            model: Model name.
            chat_history: Previous messages.
            **kwargs: Extra fields for promptObject.

        Returns:
            ConversationResult with response content and conversation_id.

        Example:
            conv = client.conversation.create()
            reply = client.conversation.send(conv.conversation_id, "Hello!")
            print(reply.content)
        """
        payload: dict[str, Any] = {
            "type": "CHAT_WITH_AI",
            "model": model,
            "conversationId": conversation_id,
            "promptObject": {
                "prompt": prompt,
                "chatList": chat_history or [],
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        ai_record = response.get("aiRecord", {})
        result_obj = ai_record.get("resultObject", {})
        content = (
            result_obj.get("message")
            or result_obj.get("content")
            or result_obj.get("text")
            or str(result_obj)
        )
        return ConversationResult(
            content=content,
            conversation_id=conversation_id,
            model=model,
            metadata=result_obj,
        )
