# onemin

TypeScript SDK for the 1min.ai API — one key, 25+ AI capabilities.

## Installation

```bash
npm install onemin
```

## Quick Start

```typescript
import { OneMinClient } from 'onemin';

const client = new OneMinClient({ apiKey: 'your-key' }); // or set ONEMIN_API_KEY env var
const result = await client.text.chat('What is 2+2?');
console.log(result.content);
```

## Domain Method Table

| Domain | Methods | Description |
|--------|---------|-------------|
| text | `chat` | Text generation and chat with any LLM; supports streaming |
| image | `generate`, `upscale`, `removeBackground`, `replaceBackground`, `removeText`, `removeObject`, `searchAndReplace`, `inpaint`, `variation`, `extend`, `toPrompt`, `editText`, `swapFace`, `generate3d` | Image generation (14 methods) and editing |
| audio | `speak`, `transcribe`, `translate`, `generateMusic` | Text-to-speech, speech-to-text, and music generation |
| video | `generate`, `fromImage` | Text-to-video and image-to-video (auto-polls for completion) |
| writing | `summarize`, `translate`, `rewrite`, `expand`, `shorten`, `paraphrase`, `checkGrammar`, `blogArticle`, `keywordResearch`, `summarizeYoutube` | 10 writing assistance methods |
| conversation | `create`, `send` | Persistent multi-turn conversations |
| asset | `upload`, `list`, `get` | File upload and asset management |

All methods return Promises. All method names use camelCase.

## Models

Discover model names via the `Models` constants — no need to memorise IDs:

```typescript
import { OneMinClient, Models } from 'onemin';

const client = new OneMinClient({ apiKey: process.env.ONEMIN_API_KEY! });

// Text models
const r1 = await client.text.chat('Hello', { model: Models.Text.GPT_4O });
const r2 = await client.text.chat('Hello', { model: Models.Text.CLAUDE_3_5_SONNET });
const r3 = await client.text.chat('Hello', { model: Models.Text.GEMINI_1_5_PRO });

// Image models
const img1 = await client.image.generate('a cat', { model: Models.Image.DALL_E_3 });
const img2 = await client.image.generate('a cat', { model: Models.Image.FLUX_SCHNELL });

// Audio models
const tts = await client.audio.speak('Hello', { model: Models.Audio.TTS_1_HD });
const stt = await client.audio.transcribe('audio.mp3', { model: Models.Audio.WHISPER_1 });

// Video models
const vid = await client.video.generate('sunset', { model: Models.Video.LUMA_AI });
```

All `Models.*` values are plain strings accepted directly by the 1min.ai API.

## Examples

Runnable examples for every domain are in [`examples/typescript/`](../examples/typescript/):

- `text-example.ts` — chat and streaming
- `image-example.ts` — generate and edit images
- `audio-example.ts` — TTS and STT
- `video-example.ts` — text-to-video
- `writing-example.ts` — summarize, translate, grammar
- `conversation-example.ts` — multi-turn chat
- `asset-example.ts` — upload and list files

Run any example after setting your API key:

```bash
export ONEMIN_API_KEY=your-key-here
npx tsx examples/typescript/text-example.ts
```
