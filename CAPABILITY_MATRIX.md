# Capability Matrix

Tracks feature parity between Python and TypeScript SDK implementations.

**Status legend:** done = fully implemented and tested | - = not applicable

## Infrastructure

| Capability | Python | TypeScript |
|-----------|--------|------------|
| Package installable | done | done |
| Auth (constructor + env var) | done | done |
| Typed exceptions | done | done |
| Retry with backoff + jitter | done | done |
| Configurable timeouts | done | done |
| Per-domain timeout defaults | done | done |
| Connection pooling | done | - (fetch) |
| API key redaction | done | done |
| Dual ESM+CJS output | - | done |
| Model constants | done | done |

## Transport

| Capability | Python | TypeScript |
|-----------|--------|------------|
| Sync HTTP client | done | - (fetch is async) |
| Async HTTP client | done | done (native) |
| SSE streaming | done (sync+async) | done (async) |
| File upload | done (sync+async) | done (async) |
| Auto-polling (jobs) | done (sync+async) | done (async) |

## Domain Resources

| Method | Python | TypeScript |
|--------|--------|------------|
| **Text** | | |
| text.chat() | done | done |
| **Image** | | |
| image.generate() | done | done |
| image.to_prompt() / toPrompt() | done | done |
| image.variation() | done | done |
| image.upscale() | done | done |
| image.extend() | done | done |
| image.remove_background() / removeBackground() | done | done |
| image.replace_background() / replaceBackground() | done | done |
| image.remove_text() / removeText() | done | done |
| image.remove_object() / removeObject() | done | done |
| image.search_and_replace() / searchAndReplace() | done | done |
| image.inpaint() | done | done |
| image.edit_text() / editText() | done | done |
| image.swap_face() / swapFace() | done | done |
| image.generate_3d() / generate3d() | done | done |
| **Audio** | | |
| audio.speak() | done | done |
| audio.transcribe() | done | done |
| audio.translate() | done | done |
| audio.generate_music() / generateMusic() | done | done |
| **Video** | | |
| video.generate() | done | done |
| video.from_image() / fromImage() | done | done |
| **Writing** | | |
| writing.keyword_research() / keywordResearch() | done | done |
| writing.blog_article() / blogArticle() | done | done |
| writing.rewrite() | done | done |
| writing.expand() | done | done |
| writing.shorten() | done | done |
| writing.translate() | done | done |
| writing.paraphrase() | done | done |
| writing.summarize() | done | done |
| writing.check_grammar() / checkGrammar() | done | done |
| writing.summarize_youtube() / summarizeYoutube() | done | done |
| **Conversation** | | |
| conversation.create() | done | done |
| conversation.send() | done | done |
| **Asset** | | |
| asset.upload() | done | done |
| asset.list() | done | done |
| asset.get() | done | done |

---

*Last updated: v1.0 milestone complete — full parity across all domains*
