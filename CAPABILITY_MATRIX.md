# Capability Matrix

Tracks feature parity between Python and TypeScript SDK implementations.

**Status legend:** done = fully implemented and tested | - = not applicable | stale = implemented against request/response shapes the live API no longer accepts

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
| Per-feature defaults (DEFAULT_MODELS / FEATURE_MODELS) | done | generated, not yet used |

## Transport

| Capability | Python | TypeScript |
|-----------|--------|------------|
| Sync HTTP client | done | - (fetch is async) |
| Async HTTP client | done | done (native) |
| SSE streaming | done (sync+async) | done (async) |
| File upload | done (sync+async) | done (async) |
| Auto-polling (GET /api/results) | done (sync+async) | stale (polls /api/jobs) |

## Domain Resources

| Method | Python | TypeScript |
|--------|--------|------------|
| **Text** | | |
| text.chat() | done | done |
| **Image** | | |
| image.generate() | done | stale |
| image.to_prompt() / toPrompt() | done | stale |
| image.variation() | done | stale |
| image.upscale() | done | stale |
| image.extend() | done | stale |
| image.remove_background() / removeBackground() | done | stale |
| image.replace_background() / replaceBackground() | done | stale |
| image.remove_text() / removeText() | done | stale |
| image.remove_object() / removeObject() | done | stale |
| image.search_and_replace() / searchAndReplace() | done | stale |
| image.inpaint() | done | stale |
| image.edit() (TS: editText(), old shape) | done | stale |
| image.swap_face() / swapFace() | done | stale |
| image.generate_3d() / generate3d() | done | stale |
| **Audio** | | |
| audio.speak() | done | stale |
| audio.transcribe() | done | stale |
| audio.translate() | done | stale |
| audio.generate_music() / generateMusic() | done | stale |
| **Video** | | |
| video.generate() | done | stale |
| video.from_image() / fromImage() | done | stale |
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

*Last updated: 2026-10-01 — Python image/audio/video rewritten against the live API (per-feature defaults, asset keys, result polling). TypeScript still uses the old shapes for those domains and for asset/conversation ids.*
