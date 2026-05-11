# onemin

Dual-language SDK (Python + TypeScript) for the [1min.ai](https://1min.ai) API -- a unified gateway to 25+ AI capabilities. One API key, dozens of models (GPT, Claude, Gemini, Mistral, Llama, DeepSeek, Grok, and more).

Generate images, edit photos, chat with LLMs, transcribe audio, create music, generate video -- all through clean one-liner calls.

## Install

This package is not yet on PyPI / npm. Install directly from GitHub:

**Python** (3.10+):

```bash
pip install git+https://github.com/JonathanCamargo/1minai.git#subdirectory=python
```

**TypeScript** (Node 18+):

```bash
npm install github:JonathanCamargo/1minai#typescript
```

Or, if you have already cloned the repo locally:

**Python** — from the repo root:
```bash
pip install -e ./python
```

**TypeScript** — from the repo root:
```bash
npm install file:./typescript
```

## Quick start

### Python

```python
from onemin import OneMinClient, Models

client = OneMinClient(api_key="your-key")  # or set ONEMIN_API_KEY env var

# Chat
result = client.text.chat("Explain quantum computing in one sentence")
print(result.content)

# Generate an image
image = client.image.generate("A cat astronaut on Mars", model=Models.Image.DALL_E_3)
print(image.url)

# Text to speech
audio = client.audio.speak("Hello from 1min.ai", model=Models.Audio.TTS_1)
print(audio.url)
```

### TypeScript

```typescript
import { OneMinClient, Models } from '@onemin/sdk';

const client = new OneMinClient({ apiKey: 'your-key' }); // or set ONEMIN_API_KEY env var

// Chat
const result = await client.text.chat('Explain quantum computing in one sentence');
console.log(result.content);

// Generate an image
const image = await client.image.generate('A cat astronaut on Mars', { model: Models.Image.DALL_E_3 });
console.log(image.url);

// Text to speech
const audio = await client.audio.speak('Hello from 1min.ai', { model: Models.Audio.TTS_1 });
console.log(audio.url);
```

## What you can do

| Domain | Methods | Description |
|--------|---------|-------------|
| **Text** | `chat` | Chat with any LLM. Supports streaming and web search. |
| **Image** | `generate`, `variation`, `upscale`, `extend`, `remove_background`, `replace_background`, `remove_text`, `remove_object`, `search_and_replace`, `inpaint`, `edit_text`, `swap_face`, `generate_3d`, `to_prompt` | Generate and edit images with 25+ models. |
| **Audio** | `speak`, `transcribe`, `translate`, `generate_music` | TTS, speech-to-text, translation, and music generation. |
| **Video** | `generate`, `from_image` | Text/image to video with auto-polling for completion. |
| **Writing** | `keyword_research`, `blog_article`, `rewrite`, `expand`, `shorten`, `translate`, `paraphrase`, `summarize`, `check_grammar`, `summarize_youtube` | AI writing tools powered by any LLM. |
| **Conversation** | `create`, `send` | Multi-turn conversation management. |
| **Asset** | `upload`, `list`, `get` | File upload and asset management. |

## Streaming

```python
# Python
for token in client.text.chat("Tell me a story", stream=True):
    print(token, end="", flush=True)

# Async
async for token in await client.text.achat("Tell me a story", stream=True):
    print(token, end="", flush=True)
```

```typescript
// TypeScript
const stream = await client.text.chat('Tell me a story', { stream: true });
for await (const token of stream) {
    process.stdout.write(token);
}
```

## File inputs

Methods that accept files (image editing, audio transcription, etc.) handle multiple input types:

```python
# Python: path, bytes, or URL
client.image.remove_background("/path/to/photo.png")
client.image.remove_background(image_bytes)
client.image.remove_background("https://example.com/photo.png")  # URL passthrough
```

```typescript
// TypeScript: Uint8Array, [filename, Uint8Array] tuple, or URL
await client.image.removeBackground(imageBytes);
await client.image.removeBackground(['photo.png', imageBytes]);
await client.image.removeBackground('https://example.com/photo.png');
```

Files are automatically uploaded to the asset API before being sent to the feature endpoint.

## Async support

Python provides both sync and async clients. Every resource method has an async counterpart prefixed with `a`:

```python
from onemin import AsyncOneMinClient

async with AsyncOneMinClient() as client:
    result = await client.text.achat("Hello!")
    image = await client.image.agenerate("A sunset over mountains")
```

TypeScript is async-native -- all methods return promises.

## Model constants

Tab-completable constants for all supported models:

```python
from onemin import Models

Models.Text.GPT_4O
Models.Text.CLAUDE_3_5_SONNET
Models.Text.GEMINI_2_0_FLASH
Models.Text.DEEPSEEK_R1
Models.Image.MIDJOURNEY
Models.Image.DALL_E_3
Models.Image.STABLE_DIFFUSION_XL
Models.Audio.TTS_1_HD
Models.Audio.ELEVENLABS
Models.Video.LUMA_AI
```

```typescript
import { Models } from '@onemin/sdk';

Models.Text.GPT_4O
Models.Text.CLAUDE_3_5_SONNET
// ... same constants available
```

## Error handling

Both SDKs throw typed exceptions:

```python
from onemin import OneMinClient, AuthenticationError, RateLimitError, APIError

try:
    result = client.text.chat("Hello")
except AuthenticationError:
    print("Bad API key")
except RateLimitError:
    print("Slow down")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

```typescript
import { OneMinClient, AuthenticationError, RateLimitError, APIError } from '@onemin/sdk';

try {
    const result = await client.text.chat('Hello');
} catch (e) {
    if (e instanceof AuthenticationError) console.log('Bad API key');
    else if (e instanceof RateLimitError) console.log('Slow down');
    else if (e instanceof APIError) console.log(`API error ${e.statusCode}: ${e.message}`);
}
```

**Exception hierarchy:** `OneMinError` > `APIError`, `AuthenticationError`, `RateLimitError`, `NotFoundError`, `BadRequestError`, `InternalServerError`, `ConnectionError`, `TimeoutError`

## Configuration

```python
client = OneMinClient(
    api_key="your-key",       # or ONEMIN_API_KEY env var
    timeout=60.0,             # seconds (default: 30)
    max_retries=3,            # default: 2
    base_delay=1.0,           # retry base delay in seconds (default: 0.5)
)
```

```typescript
const client = new OneMinClient({
    apiKey: 'your-key',       // or ONEMIN_API_KEY env var
    timeout: 60000,           // milliseconds (default: 30000)
    maxRetries: 3,            // default: 2
    baseDelay: 1000,          // retry base delay in ms (default: 500)
});
```

Retries use exponential backoff with jitter and respect `Retry-After` headers. Domain-specific timeouts apply automatically: text/writing at 30s, image/audio at 90s, video at 300s.

## Examples

See [`examples/`](examples/) for complete working scripts covering every domain in both languages.

## CLI Scripts

The [`scripts/`](scripts/) directory contains ready-to-use CLI wrappers for common tasks. They use [`fileman.envars`](https://github.com/yourusername/fileman) to load `.env` files automatically, so you can keep your API key in a project-local `.env` file without exporting it in your shell.

### Setup

Create a `.env` file in the project root:

```bash
ONEMIN_API_KEY=your-key-here
```

The scripts load configuration in this priority (system env always wins):
1. Already-set OS environment variables
2. `~/.env` (global)
3. `<project_root>/.env` (local)

### Available scripts

| Script | What it does | Example |
|--------|-------------|---------|
| `q.py` | Ask a text question to an LLM | `python scripts/q.py "what is quantum computing?"` |
| `sum.py` | Summarize text from argument, file, or stdin | `python scripts/sum.py "long text..."` <br> `python scripts/sum.py -f article.txt` <br> `cat report.md \| python scripts/sum.py --stdin` |
| `img.py` | Generate an image from a prompt | `python scripts/img.py "a futuristic city"` <br> `python scripts/img.py "sunset" -m dall-e-3 -W 512 -H 512` |
| `speak.py` | Convert text to speech | `python scripts/speak.py "Hello world"` <br> `python scripts/speak.py -f story.txt -v Rachel` |

All scripts support `-k/--api-key` to override the env variable and `-m/--model` to select a specific model.

## License

MIT
