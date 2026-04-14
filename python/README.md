# onemin

Python SDK for the 1min.ai API — one key, 25+ AI capabilities.

## Installation

```bash
pip install onemin
```

## Quick Start

```python
from onemin import OneMinClient

client = OneMinClient(api_key="your-key")  # or set ONEMIN_API_KEY env var
result = client.text.chat("What is 2+2?")
print(result.content)
```

## Domain Method Table

| Domain | Methods | Description |
|--------|---------|-------------|
| text | `chat` | Text generation and chat with any LLM; supports streaming |
| image | `generate`, `upscale`, `remove_background`, `replace_background`, `remove_text`, `remove_object`, `search_and_replace`, `inpaint`, `variation`, `extend`, `to_prompt`, `edit_text`, `swap_face`, `generate_3d` | Image generation (14 methods) and editing |
| audio | `speak`, `transcribe`, `translate`, `generate_music` | Text-to-speech, speech-to-text, and music generation |
| video | `generate`, `from_image` | Text-to-video and image-to-video (auto-polls for completion) |
| writing | `summarize`, `translate`, `rewrite`, `expand`, `shorten`, `paraphrase`, `check_grammar`, `blog_article`, `keyword_research`, `summarize_youtube` | 10 writing assistance methods |
| conversation | `create`, `send` | Persistent multi-turn conversations |
| asset | `upload`, `list`, `get` | File upload and asset management |

All methods have async counterparts prefixed with `a` (e.g., `achat`, `agenerate`).

## Models

Discover model names via the `Models` constants — no need to memorise IDs:

```python
from onemin import OneMinClient, Models

client = OneMinClient()

# Text models
result = client.text.chat("Hello", model=Models.Text.GPT_4O)
result = client.text.chat("Hello", model=Models.Text.CLAUDE_3_5_SONNET)
result = client.text.chat("Hello", model=Models.Text.GEMINI_1_5_PRO)

# Image models
result = client.image.generate("a cat", model=Models.Image.DALL_E_3)
result = client.image.generate("a cat", model=Models.Image.FLUX_SCHNELL)

# Audio models
result = client.audio.speak("Hello", model=Models.Audio.TTS_1_HD)
result = client.audio.transcribe("audio.mp3", model=Models.Audio.WHISPER_1)

# Video models
result = client.video.generate("sunset", model=Models.Video.LUMA_AI)
```

All `Models.*` values are plain strings accepted directly by the 1min.ai API.

## Examples

Runnable examples for every domain are in [`examples/python/`](../examples/python/):

- `text_example.py` — chat and streaming
- `image_example.py` — generate and edit images
- `audio_example.py` — TTS and STT
- `video_example.py` — text-to-video
- `writing_example.py` — summarize, translate, grammar
- `conversation_example.py` — multi-turn chat
- `asset_example.py` — upload and list files

Run any example after setting your API key:

```bash
export ONEMIN_API_KEY=your-key-here
python examples/python/text_example.py
```
