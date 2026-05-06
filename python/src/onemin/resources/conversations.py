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
            response = client.conversation.raw({"title": "Test", "type": "UNIFY_CHAT_WITH_AI", "model": "gpt-4o"})
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
            response = await client.conversation.araw({"title": "Test", "type": "UNIFY_CHAT_WITH_AI", "model": "gpt-4o"})
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
        conversation_type: str = "UNIFY_CHAT_WITH_AI",
        **kwargs: Any,
    ) -> ConversationResult:
        """Create a new conversation asynchronously.

        Args:
            title: Conversation title.
            model: Model to use for the conversation.
            conversation_type: API conversation type. Defaults to
                "UNIFY_CHAT_WITH_AI" -- the recommended unified flow that
                handles text, images, files, and YouTube URLs in one shape.
                Legacy values (CHAT_WITH_IMAGE, CHAT_WITH_PDF,
                CHAT_WITH_YOUTUBE_VIDEO) are deprecated upstream.
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
        **kwargs: Any,
    ) -> ConversationResult:
        """Send a message within an existing conversation asynchronously.

        Args:
            conversation_id: ID from a previous acreate() call.
            prompt: The message to send.
            model: Model name.
            **kwargs: Extra fields for promptObject.

        Returns:
            ConversationResult with response content and conversation_id.

        Example:
            conv = await client.conversation.acreate()
            reply = await client.conversation.asend(conv.conversation_id, "Hello!")
            print(reply.content)
        """
        payload: dict[str, Any] = {
            "type": "UNIFY_CHAT_WITH_AI",
            "model": model,
            "promptObject": {
                "prompt": prompt,
                "conversationId": conversation_id,
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/chat-with-ai", json=payload, timeout=self._timeout,
        )
        return _parse_conversation_response(response, conversation_id, model)

    def create(
        self,
        *,
        title: str = "Untitled",
        model: str = "gpt-4o",
        conversation_type: str = "UNIFY_CHAT_WITH_AI",
        **kwargs: Any,
    ) -> ConversationResult:
        """Create a new conversation.

        Args:
            title: Conversation title.
            model: Model to use for the conversation.
            conversation_type: API conversation type. Defaults to
                "UNIFY_CHAT_WITH_AI" -- the recommended unified flow that
                handles text, images, files, and YouTube URLs in one shape.
                Legacy values (CHAT_WITH_IMAGE, CHAT_WITH_PDF,
                CHAT_WITH_YOUTUBE_VIDEO) are deprecated upstream.
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
        **kwargs: Any,
    ) -> ConversationResult:
        """Send a message within an existing conversation.

        Args:
            conversation_id: ID from a previous create() call.
            prompt: The message to send.
            model: Model name.
            **kwargs: Extra fields for promptObject.

        Returns:
            ConversationResult with response content and conversation_id.

        Example:
            conv = client.conversation.create()
            reply = client.conversation.send(conv.conversation_id, "Hello!")
            print(reply.content)
        """
        payload: dict[str, Any] = {
            "type": "UNIFY_CHAT_WITH_AI",
            "model": model,
            "promptObject": {
                "prompt": prompt,
                "conversationId": conversation_id,
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/chat-with-ai", json=payload, timeout=self._timeout,
        )
        return _parse_conversation_response(response, conversation_id, model)


def _parse_conversation_response(
    response: dict[str, Any],
    conversation_id: str,
    model: str,
) -> ConversationResult:
    """Build a ConversationResult from a /api/chat-with-ai response.

    Handles both the new ``resultObject`` list-of-strings format and the
    legacy dict shape.
    """
    ai_record = response.get("aiRecord", {})
    detail = ai_record.get("aiRecordDetail") or {}
    result_obj = detail.get("resultObject")
    if result_obj is None:
        result_obj = ai_record.get("resultObject")
    if isinstance(result_obj, list):
        content = "".join(str(c) for c in result_obj)
        metadata: dict[str, Any] = {"resultObject": result_obj}
    elif isinstance(result_obj, dict):
        content = (
            result_obj.get("message")
            or result_obj.get("content")
            or result_obj.get("text")
            or str(result_obj)
        )
        metadata = result_obj
    else:
        content = "" if result_obj is None else str(result_obj)
        metadata = {}
    return ConversationResult(
        content=content,
        conversation_id=conversation_id,
        model=model,
        metadata=metadata,
    )
