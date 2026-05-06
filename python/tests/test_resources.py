"""Tests for domain resource stubs and lazy initialization on OneMinClient.

Covers:
- All 7 domain resources are accessible via lazy properties on OneMinClient
- Resources are instances of the correct type
- Lazy initialization: same instance returned on repeated access
- High-level stub methods raise NotImplementedError (for unimplemented resources)
- raw() method is callable on each resource
- Per-domain timeouts (INFRA-07)
- ConversationResource and AssetResource use their own endpoints
- TextResource.chat() returns TextResult (with mocked _request)
- TextResource.chat(stream=True) returns a generator (with mocked stream_sse)
- ConversationResource.create() calls /api/conversations and returns ConversationResult
- ConversationResource.send() sends correct payload and returns ConversationResult
"""

from unittest.mock import MagicMock, patch
import pytest

from onemin import OneMinClient
from onemin.resources import (
    ImageResource,
    TextResource,
    AudioResource,
    VideoResource,
    WritingResource,
    ConversationResource,
    AssetResource,
)
from onemin.resources._base_resource import BaseResource
from onemin.models import TextResult, ConversationResult


@pytest.fixture
def client() -> OneMinClient:
    """Create a OneMinClient with a test API key."""
    return OneMinClient(api_key="test-key-12345678")


# ---------------------------------------------------------------------------
# Resource type tests
# ---------------------------------------------------------------------------

def test_image_resource_type(client: OneMinClient) -> None:
    """client.image returns an ImageResource instance."""
    assert isinstance(client.image, ImageResource)


def test_text_resource_type(client: OneMinClient) -> None:
    """client.text returns a TextResource instance."""
    assert isinstance(client.text, TextResource)


def test_audio_resource_type(client: OneMinClient) -> None:
    """client.audio returns an AudioResource instance."""
    assert isinstance(client.audio, AudioResource)


def test_video_resource_type(client: OneMinClient) -> None:
    """client.video returns a VideoResource instance."""
    assert isinstance(client.video, VideoResource)


def test_writing_resource_type(client: OneMinClient) -> None:
    """client.writing returns a WritingResource instance."""
    assert isinstance(client.writing, WritingResource)


def test_conversation_resource_type(client: OneMinClient) -> None:
    """client.conversation returns a ConversationResource instance."""
    assert isinstance(client.conversation, ConversationResource)


def test_asset_resource_type(client: OneMinClient) -> None:
    """client.asset returns an AssetResource instance."""
    assert isinstance(client.asset, AssetResource)


# ---------------------------------------------------------------------------
# BaseResource inheritance
# ---------------------------------------------------------------------------

def test_all_resources_inherit_base_resource(client: OneMinClient) -> None:
    """All domain resources inherit from BaseResource."""
    assert isinstance(client.image, BaseResource)
    assert isinstance(client.text, BaseResource)
    assert isinstance(client.audio, BaseResource)
    assert isinstance(client.video, BaseResource)
    assert isinstance(client.writing, BaseResource)
    assert isinstance(client.conversation, BaseResource)
    assert isinstance(client.asset, BaseResource)


# ---------------------------------------------------------------------------
# Lazy initialization tests (Pattern 5)
# ---------------------------------------------------------------------------

def test_image_lazy_same_instance(client: OneMinClient) -> None:
    """client.image returns the same instance on repeated access."""
    assert client.image is client.image


def test_text_lazy_same_instance(client: OneMinClient) -> None:
    """client.text returns the same instance on repeated access."""
    assert client.text is client.text


def test_audio_lazy_same_instance(client: OneMinClient) -> None:
    """client.audio returns the same instance on repeated access."""
    assert client.audio is client.audio


def test_video_lazy_same_instance(client: OneMinClient) -> None:
    """client.video returns the same instance on repeated access."""
    assert client.video is client.video


def test_writing_lazy_same_instance(client: OneMinClient) -> None:
    """client.writing returns the same instance on repeated access."""
    assert client.writing is client.writing


def test_conversation_lazy_same_instance(client: OneMinClient) -> None:
    """client.conversation returns the same instance on repeated access."""
    assert client.conversation is client.conversation


def test_asset_lazy_same_instance(client: OneMinClient) -> None:
    """client.asset returns the same instance on repeated access."""
    assert client.asset is client.asset


def test_resources_not_created_at_construction() -> None:
    """Resources are NOT initialized at client construction time."""
    client = OneMinClient(api_key="test-key-12345678")
    # Private backing attributes should not exist yet
    assert not hasattr(client, "_image")
    assert not hasattr(client, "_text")
    assert not hasattr(client, "_audio")
    assert not hasattr(client, "_video")
    assert not hasattr(client, "_writing")
    assert not hasattr(client, "_conversation")
    assert not hasattr(client, "_asset")


# ---------------------------------------------------------------------------
# High-level methods exist and are callable on each resource
# ---------------------------------------------------------------------------

def test_image_generate_is_callable(client: OneMinClient) -> None:
    """client.image.generate is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.image, "generate", None))


def test_audio_speak_is_callable(client: OneMinClient) -> None:
    """client.audio.speak is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.audio, "speak", None))


def test_video_generate_is_callable(client: OneMinClient) -> None:
    """client.video.generate is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.video, "generate", None))


def test_writing_summarize_is_callable(client: OneMinClient) -> None:
    """client.writing.summarize is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.writing, "summarize", None))


def test_writing_rewrite_is_callable(client: OneMinClient) -> None:
    """client.writing.rewrite is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.writing, "rewrite", None))


def test_asset_list_is_callable(client: OneMinClient) -> None:
    """client.asset.list is callable (fully implemented in Phase 3)."""
    assert callable(getattr(client.asset, "list", None))


# ---------------------------------------------------------------------------
# raw() method exists and is callable
# ---------------------------------------------------------------------------

def test_image_has_raw_method(client: OneMinClient) -> None:
    """client.image has a callable raw() method."""
    assert callable(getattr(client.image, "raw", None))


def test_text_has_raw_method(client: OneMinClient) -> None:
    """client.text has a callable raw() method."""
    assert callable(getattr(client.text, "raw", None))


def test_audio_has_raw_method(client: OneMinClient) -> None:
    """client.audio has a callable raw() method."""
    assert callable(getattr(client.audio, "raw", None))


def test_video_has_raw_method(client: OneMinClient) -> None:
    """client.video has a callable raw() method."""
    assert callable(getattr(client.video, "raw", None))


def test_writing_has_raw_method(client: OneMinClient) -> None:
    """client.writing has a callable raw() method."""
    assert callable(getattr(client.writing, "raw", None))


def test_conversation_has_raw_method(client: OneMinClient) -> None:
    """client.conversation has a callable raw() method."""
    assert callable(getattr(client.conversation, "raw", None))


def test_asset_has_raw_method(client: OneMinClient) -> None:
    """client.asset has a callable raw() method."""
    assert callable(getattr(client.asset, "raw", None))


# ---------------------------------------------------------------------------
# Per-domain timeout tests (INFRA-07)
# ---------------------------------------------------------------------------

def test_image_timeout_is_90s(client: OneMinClient) -> None:
    """ImageResource uses 90s domain timeout (INFRA-07)."""
    assert client.image._timeout == 90.0


def test_text_timeout_is_30s(client: OneMinClient) -> None:
    """TextResource uses 30s domain timeout (INFRA-07)."""
    assert client.text._timeout == 30.0


def test_audio_timeout_is_90s(client: OneMinClient) -> None:
    """AudioResource uses 90s domain timeout (INFRA-07)."""
    assert client.audio._timeout == 90.0


def test_video_timeout_is_300s(client: OneMinClient) -> None:
    """VideoResource uses 300s domain timeout (INFRA-07)."""
    assert client.video._timeout == 300.0


def test_writing_timeout_is_30s(client: OneMinClient) -> None:
    """WritingResource uses 30s domain timeout (INFRA-07)."""
    assert client.writing._timeout == 30.0


def test_conversation_timeout_is_30s(client: OneMinClient) -> None:
    """ConversationResource uses 30s domain timeout (INFRA-07)."""
    assert client.conversation._timeout == 30.0


def test_asset_timeout_is_30s(client: OneMinClient) -> None:
    """AssetResource uses 30s domain timeout (INFRA-07)."""
    assert client.asset._timeout == 30.0


# ---------------------------------------------------------------------------
# Domain name tests
# ---------------------------------------------------------------------------

def test_image_domain_name(client: OneMinClient) -> None:
    """ImageResource._domain is 'image'."""
    assert client.image._domain == "image"


def test_text_domain_name(client: OneMinClient) -> None:
    """TextResource._domain is 'text'."""
    assert client.text._domain == "text"


def test_audio_domain_name(client: OneMinClient) -> None:
    """AudioResource._domain is 'audio'."""
    assert client.audio._domain == "audio"


def test_video_domain_name(client: OneMinClient) -> None:
    """VideoResource._domain is 'video'."""
    assert client.video._domain == "video"


def test_writing_domain_name(client: OneMinClient) -> None:
    """WritingResource._domain is 'writing'."""
    assert client.writing._domain == "writing"


def test_conversation_domain_name(client: OneMinClient) -> None:
    """ConversationResource._domain is 'conversation'."""
    assert client.conversation._domain == "conversation"


def test_asset_domain_name(client: OneMinClient) -> None:
    """AssetResource._domain is 'asset'."""
    assert client.asset._domain == "asset"


# ---------------------------------------------------------------------------
# TextResource.chat() implementation tests
# ---------------------------------------------------------------------------

def test_text_chat_returns_text_result(client: OneMinClient) -> None:
    """text.chat('hello') sends UNIFY_CHAT_WITH_AI payload and returns TextResult."""
    mock_response = {
        "aiRecord": {
            "resultObject": ["Hello there!"],
        }
    }
    with patch.object(client, "_request", return_value=mock_response):
        result = client.text.chat("hello")

    assert isinstance(result, TextResult)
    assert result.content == "Hello there!"
    assert result.model == "gpt-4o"


def test_text_chat_sends_correct_payload(client: OneMinClient) -> None:
    """text.chat() POSTs /api/chat-with-ai with type=UNIFY_CHAT_WITH_AI."""
    mock_response = {
        "aiRecord": {"resultObject": ["Response"]}
    }
    captured_args: list = []
    captured_kwargs: dict = {}

    def capture_request(method, path, **kwargs):
        captured_args.extend([method, path])
        captured_kwargs.update(kwargs)
        return mock_response

    with patch.object(client, "_request", side_effect=capture_request):
        client.text.chat("hello world", model="gpt-4o")

    assert "/api/chat-with-ai" in captured_args
    payload = captured_kwargs.get("json", {})
    assert payload["type"] == "UNIFY_CHAT_WITH_AI"
    assert payload["model"] == "gpt-4o"
    assert payload["promptObject"]["prompt"] == "hello world"
    # chat_history was dropped from the surface API; ensure we no longer send it.
    assert "chatList" not in payload["promptObject"]


def test_text_chat_stream_returns_generator(client: OneMinClient) -> None:
    """text.chat('hello', stream=True) returns a generator yielding tokens."""
    import types

    def mock_stream_gen():
        yield "token1"
        yield "token2"

    with patch("onemin.resources.text.stream_sse", return_value=mock_stream_gen()):
        result = client.text.chat("hello", stream=True)
        # Must consume the generator inside the patch context since stream_sse is lazy
        assert isinstance(result, types.GeneratorType)
        tokens = list(result)

    assert tokens == ["token1", "token2"]


def test_text_chat_default_model_is_gpt4o(client: OneMinClient) -> None:
    """text.chat() defaults to gpt-4o model."""
    mock_response = {
        "aiRecord": {"resultObject": ["OK"]}
    }
    captured_kwargs: dict = {}

    def capture_request(method, path, **kwargs):
        captured_kwargs.update(kwargs)
        return mock_response

    with patch.object(client, "_request", side_effect=capture_request):
        result = client.text.chat("test prompt")

    assert result.model == "gpt-4o"
    assert captured_kwargs["json"]["model"] == "gpt-4o"


def test_text_chat_web_search_nests_in_settings(client: OneMinClient) -> None:
    """text.chat(web_search=True) nests under promptObject.settings.webSearchSettings."""
    mock_response = {"aiRecord": {"resultObject": ["x"]}}
    captured_kwargs: dict = {}

    def capture_request(method, path, **kwargs):
        captured_kwargs.update(kwargs)
        return mock_response

    with patch.object(client, "_request", side_effect=capture_request):
        client.text.chat("q", web_search=True)

    settings = captured_kwargs["json"]["promptObject"].get("settings", {})
    assert settings.get("webSearchSettings", {}).get("webSearch") is True


def test_text_chat_parses_legacy_dict_result_object(client: OneMinClient) -> None:
    """Parser still accepts the older dict-shaped resultObject."""
    mock_response = {
        "aiRecord": {"resultObject": {"message": "legacy"}}
    }
    with patch.object(client, "_request", return_value=mock_response):
        result = client.text.chat("hello")
    assert result.content == "legacy"


# ---------------------------------------------------------------------------
# UnsupportedModelError detection
# ---------------------------------------------------------------------------

def test_unsupported_model_error_is_raised_with_suggestions() -> None:
    """A 400 with errorCode UNSUPPORTED_MODEL is promoted to UnsupportedModelError.

    The error attaches the rejected model id and a non-empty suggestion list
    sourced from the generated catalogue.
    """
    import httpx
    from onemin import OneMinClient, UnsupportedModelError

    body = (
        '{"errorCode":"UNSUPPORTED_MODEL",'
        '"message":"Model totally-not-a-model is not supported"}'
    )
    client = OneMinClient(api_key="test-key-12345678")
    fake_response = httpx.Response(status_code=400, text=body)
    with pytest.raises(UnsupportedModelError) as excinfo:
        client._handle_response(fake_response)
    err = excinfo.value
    assert err.requested_model == "totally-not-a-model"
    assert err.suggestions, "expected non-empty suggestions"
    assert "Try one of:" in str(err)


def test_other_400_still_maps_to_bad_request_error() -> None:
    """Non-UNSUPPORTED_MODEL 400s keep their existing BadRequestError mapping."""
    import httpx
    from onemin import OneMinClient, BadRequestError, UnsupportedModelError

    body = '{"errorCode":"REQUEST_BODY_VALIDATION_FAILED","message":"bad payload"}'
    client = OneMinClient(api_key="test-key-12345678")
    fake_response = httpx.Response(status_code=400, text=body)
    with pytest.raises(BadRequestError) as excinfo:
        client._handle_response(fake_response)
    assert not isinstance(excinfo.value, UnsupportedModelError)


# ---------------------------------------------------------------------------
# ConversationResource implementation tests
# ---------------------------------------------------------------------------

def test_conversation_create_returns_conversation_result(client: OneMinClient) -> None:
    """conversation.create() calls /api/conversations and returns ConversationResult."""
    mock_response = {
        "conversation": {
            "id": "conv_abc123",
            "title": "Test",
            "model": "gpt-4o",
        }
    }

    with patch.object(client, "_request", return_value=mock_response) as mock_req:
        result = client.conversation.create(title="Test")

    assert isinstance(result, ConversationResult)
    assert result.conversation_id == "conv_abc123"
    assert result.model == "gpt-4o"
    assert result.content == ""

    # Verify it called /api/conversations
    call_args = mock_req.call_args
    assert call_args[0][1] == "/api/conversations"


def test_conversation_create_payload(client: OneMinClient) -> None:
    """conversation.create() sends title, type, and model fields."""
    mock_response = {
        "conversation": {"id": "conv_xyz", "title": "My Chat"}
    }
    captured_kwargs: dict = {}

    def capture_request(method, path, **kwargs):
        captured_kwargs.update(kwargs)
        return mock_response

    with patch.object(client, "_request", side_effect=capture_request):
        client.conversation.create(title="My Chat", model="claude-3-5-sonnet")

    payload = captured_kwargs.get("json", {})
    assert payload["title"] == "My Chat"
    assert payload["model"] == "claude-3-5-sonnet"
    assert payload["type"] == "UNIFY_CHAT_WITH_AI"


def test_conversation_send_returns_conversation_result(client: OneMinClient) -> None:
    """conversation.send() sends message within conversation and returns ConversationResult."""
    mock_response = {
        "aiRecord": {
            "resultObject": ["Follow-up answer"],
        }
    }

    with patch.object(client, "_request", return_value=mock_response):
        result = client.conversation.send("conv_abc123", "Follow-up question")

    assert isinstance(result, ConversationResult)
    assert result.content == "Follow-up answer"
    assert result.conversation_id == "conv_abc123"


def test_conversation_send_sends_correct_payload(client: OneMinClient) -> None:
    """conversation.send() posts to /api/chat-with-ai with conversationId in promptObject."""
    mock_response = {
        "aiRecord": {"resultObject": ["Answer"]}
    }
    captured_args: list = []
    captured_kwargs: dict = {}

    def capture_request(method, path, **kwargs):
        captured_args.extend([method, path])
        captured_kwargs.update(kwargs)
        return mock_response

    with patch.object(client, "_request", side_effect=capture_request):
        client.conversation.send("conv_id_123", "msg", model="gpt-4o")

    assert "/api/chat-with-ai" in captured_args
    payload = captured_kwargs.get("json", {})
    assert payload["type"] == "UNIFY_CHAT_WITH_AI"
    assert payload["promptObject"]["prompt"] == "msg"
    assert payload["promptObject"]["conversationId"] == "conv_id_123"
    # conversationId moved into promptObject — no longer at top level.
    assert "conversationId" not in {k for k in payload if k != "promptObject"}
