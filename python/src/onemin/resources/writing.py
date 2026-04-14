"""Writing domain resource for the 1min.ai API.

Domain timeout: 30s (per INFRA-07).

Provides 10 writing capabilities: keyword_research, blog_article, rewrite,
expand, shorten, translate, paraphrase, summarize, check_grammar, summarize_youtube.

All methods use the conversationId sentinel pattern — conversationId must equal
the feature type string or the API will reject the request.
"""

from __future__ import annotations

from typing import Any

from onemin.resources._base_resource import BaseResource
from onemin.models import WritingResult


class WritingResource(BaseResource):
    """Writing assistance and text manipulation operations.

    Domain timeout: 30s (per INFRA-07).

    All methods include the ``conversationId`` sentinel (must equal the type
    string). ``summarize_youtube`` additionally requires ``videoUrl`` at both
    the payload root and inside ``promptObject``.
    """

    _domain = "writing"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _writing_call(
        self,
        feature_type: str,
        prompt: str,
        model: str,
        extra_payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> WritingResult:
        """Common method for all writing endpoints with sentinel conversationId.

        Args:
            feature_type: The API feature type string (e.g. ``"SUMMARIZER"``).
            prompt: The text or topic to process.
            model: The AI model to use.
            extra_payload: Additional top-level payload fields (merged last).
            **kwargs: Extra fields merged into ``promptObject``.

        Returns:
            Typed :class:`~onemin.models.WritingResult`.
        """
        payload: dict[str, Any] = {
            "type": feature_type,
            "model": model,
            "conversationId": feature_type,  # SENTINEL — must equal the type string
            "promptObject": {
                "prompt": prompt,
                **kwargs,
            },
        }
        if extra_payload:
            payload.update(extra_payload)
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_writing_result(response, model)

    @staticmethod
    def _parse_writing_result(response: dict[str, Any], model: str) -> WritingResult:
        """Extract a :class:`~onemin.models.WritingResult` from a raw API response.

        Args:
            response: Raw API response dictionary.
            model: The model name used for the request.

        Returns:
            Typed :class:`~onemin.models.WritingResult`.
        """
        ai_record = response.get("aiRecord", {})
        result_obj = ai_record.get("resultObject", {})
        content = (
            result_obj.get("message")
            or result_obj.get("content")
            or result_obj.get("text")
            or str(result_obj)
        )
        return WritingResult(content=content, model=model, metadata=result_obj)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def _awriting_call(
        self,
        feature_type: str,
        prompt: str,
        model: str,
        extra_payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> WritingResult:
        """Async version of _writing_call().

        Args:
            feature_type: The API feature type string (e.g. ``"SUMMARIZER"``).
            prompt: The text or topic to process.
            model: The AI model to use.
            extra_payload: Additional top-level payload fields (merged last).
            **kwargs: Extra fields merged into ``promptObject``.

        Returns:
            Typed :class:`~onemin.models.WritingResult`.
        """
        payload: dict[str, Any] = {
            "type": feature_type,
            "model": model,
            "conversationId": feature_type,  # SENTINEL — must equal the type string
            "promptObject": {
                "prompt": prompt,
                **kwargs,
            },
        }
        if extra_payload:
            payload.update(extra_payload)
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_writing_result(response, model)

    async def akeyword_research(self, topic: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Research keywords for SEO or content planning asynchronously.

        Args:
            topic: The topic or niche to research keywords for.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with keyword suggestions.

        Example:
            result = await client.writing.akeyword_research("AI productivity tools")
            print(result.content)
        """
        return await self._awriting_call("KEYWORD_RESEARCH", topic, model, **kwargs)

    async def ablog_article(self, topic: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Generate a full blog article on the given topic asynchronously.

        Args:
            topic: The subject of the blog article.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the generated article.

        Example:
            result = await client.writing.ablog_article("The future of AI assistants")
            print(result.content)
        """
        return await self._awriting_call("CONTENT_GENERATOR_BLOG_ARTICLE", topic, model, **kwargs)

    async def arewrite(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Rewrite a block of text while preserving its meaning asynchronously.

        Args:
            text: The text to rewrite.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters (tone, style, etc.).

        Returns:
            :class:`~onemin.models.WritingResult` with the rewritten text.

        Example:
            result = await client.writing.arewrite("The quick brown fox jumps.")
            print(result.content)
        """
        return await self._awriting_call("REWRITER", text, model, **kwargs)

    async def aexpand(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Expand a short passage into a longer, more detailed version asynchronously.

        Args:
            text: The text to expand.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the expanded text.

        Example:
            result = await client.writing.aexpand("AI is transforming industries.")
            print(result.content)
        """
        return await self._awriting_call("CONTENT_EXPANDER", text, model, **kwargs)

    async def ashorten(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Shorten a piece of text while retaining key information asynchronously.

        Args:
            text: The text to shorten.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the shortened text.

        Example:
            result = await client.writing.ashorten("This is a very long paragraph...")
            print(result.content)
        """
        return await self._awriting_call("CONTENT_SHORTENER", text, model, **kwargs)

    async def atranslate(
        self,
        text: str,
        *,
        target_language: str = "en",
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> WritingResult:
        """Translate text into the target language asynchronously.

        Args:
            text: The text to translate.
            target_language: The target language code (default ``"en"``).
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the translated text.

        Example:
            result = await client.writing.atranslate("Hello world", target_language="es")
            print(result.content)
        """
        return await self._awriting_call(
            "CONTENT_TRANSLATOR", text, model, targetLanguage=target_language, **kwargs
        )

    async def aparaphrase(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Paraphrase text to express the same idea with different wording asynchronously.

        Args:
            text: The text to paraphrase.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the paraphrased text.

        Example:
            result = await client.writing.aparaphrase("The cat sat on the mat.")
            print(result.content)
        """
        return await self._awriting_call("PARAPHRASER", text, model, **kwargs)

    async def asummarize(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Summarize a block of text asynchronously.

        Args:
            text: The text to summarize.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the summary.

        Example:
            result = await client.writing.asummarize("Long article text here...")
            print(result.content)
        """
        return await self._awriting_call("SUMMARIZER", text, model, **kwargs)

    async def acheck_grammar(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Check and correct the grammar of a block of text asynchronously.

        Args:
            text: The text to grammar-check.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the corrected text.

        Example:
            result = await client.writing.acheck_grammar("Their going to the store.")
            print(result.content)
        """
        return await self._awriting_call("GRAMMAR_CHECKER", text, model, **kwargs)

    async def asummarize_youtube(
        self,
        video_url: str,
        *,
        model: str = "gpt-4o",
        prompt: str = "Summarize this video",
        **kwargs: Any,
    ) -> WritingResult:
        """Summarize a YouTube video asynchronously.

        Uses the double ``videoUrl`` pattern required by the API: ``videoUrl``
        must appear at the top-level payload AND inside ``promptObject``.

        Args:
            video_url: The YouTube video URL to summarize.
            model: The AI model to use (default ``"gpt-4o"``).
            prompt: The instruction prompt (default ``"Summarize this video"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the video summary.

        Example:
            result = await client.writing.asummarize_youtube("https://youtube.com/watch?v=abc123")
            print(result.content)
        """
        payload: dict[str, Any] = {
            "type": "YOUTUBE_SUMMARIZER",
            "model": model,
            "conversationId": "YOUTUBE_SUMMARIZER",  # SENTINEL
            "videoUrl": video_url,  # top-level field (REQUIRED)
            "promptObject": {
                "prompt": prompt,
                "videoUrl": video_url,  # also inside promptObject (REQUIRED)
                **kwargs,
            },
        }
        response = await self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_writing_result(response, model)

    def keyword_research(self, topic: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Research keywords for SEO or content planning.

        Args:
            topic: The topic or niche to research keywords for.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with keyword suggestions.

        Example:
            result = client.writing.keyword_research("AI productivity tools")
            print(result.content)
        """
        return self._writing_call("KEYWORD_RESEARCH", topic, model, **kwargs)

    def blog_article(self, topic: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Generate a full blog article on the given topic.

        Args:
            topic: The subject of the blog article.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the generated article.

        Example:
            result = client.writing.blog_article("The future of AI assistants")
            print(result.content)
        """
        return self._writing_call("CONTENT_GENERATOR_BLOG_ARTICLE", topic, model, **kwargs)

    def rewrite(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Rewrite a block of text while preserving its meaning.

        Args:
            text: The text to rewrite.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters (tone, style, etc.).

        Returns:
            :class:`~onemin.models.WritingResult` with the rewritten text.

        Example:
            result = client.writing.rewrite("The quick brown fox jumps.")
            print(result.content)
        """
        return self._writing_call("REWRITER", text, model, **kwargs)

    def expand(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Expand a short passage into a longer, more detailed version.

        Args:
            text: The text to expand.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the expanded text.

        Example:
            result = client.writing.expand("AI is transforming industries.")
            print(result.content)
        """
        return self._writing_call("CONTENT_EXPANDER", text, model, **kwargs)

    def shorten(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Shorten a piece of text while retaining key information.

        Args:
            text: The text to shorten.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the shortened text.

        Example:
            result = client.writing.shorten("This is a very long paragraph...")
            print(result.content)
        """
        return self._writing_call("CONTENT_SHORTENER", text, model, **kwargs)

    def translate(
        self,
        text: str,
        *,
        target_language: str = "en",
        model: str = "gpt-4o",
        **kwargs: Any,
    ) -> WritingResult:
        """Translate text into the target language.

        Args:
            text: The text to translate.
            target_language: The target language code (default ``"en"``).
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the translated text.

        Example:
            result = client.writing.translate("Hello world", target_language="es")
            print(result.content)
        """
        return self._writing_call(
            "CONTENT_TRANSLATOR", text, model, targetLanguage=target_language, **kwargs
        )

    def paraphrase(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Paraphrase text to express the same idea with different wording.

        Args:
            text: The text to paraphrase.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the paraphrased text.

        Example:
            result = client.writing.paraphrase("The cat sat on the mat.")
            print(result.content)
        """
        return self._writing_call("PARAPHRASER", text, model, **kwargs)

    def summarize(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Summarize a block of text.

        Args:
            text: The text to summarize.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the summary.

        Example:
            result = client.writing.summarize("Long article text here...")
            print(result.content)
        """
        return self._writing_call("SUMMARIZER", text, model, **kwargs)

    def check_grammar(self, text: str, *, model: str = "gpt-4o", **kwargs: Any) -> WritingResult:
        """Check and correct the grammar of a block of text.

        Args:
            text: The text to grammar-check.
            model: The AI model to use (default ``"gpt-4o"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the corrected text.

        Example:
            result = client.writing.check_grammar("Their going to the store.")
            print(result.content)
        """
        return self._writing_call("GRAMMAR_CHECKER", text, model, **kwargs)

    def summarize_youtube(
        self,
        video_url: str,
        *,
        model: str = "gpt-4o",
        prompt: str = "Summarize this video",
        **kwargs: Any,
    ) -> WritingResult:
        """Summarize a YouTube video.

        Uses the double ``videoUrl`` pattern required by the API: ``videoUrl``
        must appear at the top-level payload AND inside ``promptObject``.

        Args:
            video_url: The YouTube video URL to summarize.
            model: The AI model to use (default ``"gpt-4o"``).
            prompt: The instruction prompt (default ``"Summarize this video"``).
            **kwargs: Additional parameters forwarded into ``promptObject``.

        Returns:
            :class:`~onemin.models.WritingResult` with the video summary.

        Example:
            result = client.writing.summarize_youtube("https://youtube.com/watch?v=abc123")
            print(result.content)
        """
        payload: dict[str, Any] = {
            "type": "YOUTUBE_SUMMARIZER",
            "model": model,
            "conversationId": "YOUTUBE_SUMMARIZER",  # SENTINEL
            "videoUrl": video_url,  # top-level field (REQUIRED)
            "promptObject": {
                "prompt": prompt,
                "videoUrl": video_url,  # also inside promptObject (REQUIRED)
                **kwargs,
            },
        }
        response = self._client._request(
            "POST", "/api/features", json=payload, timeout=self._timeout,
        )
        return self._parse_writing_result(response, model)
