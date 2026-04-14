// Run: npx tsx audio-example.ts
// audio-example.ts -- demonstrates speak() (TTS) and transcribe() (STT)
import { OneMinClient, Models } from 'onemin';

const apiKey = process.env.ONEMIN_API_KEY;
if (!apiKey) {
  console.error('Set ONEMIN_API_KEY environment variable to run this example.');
  console.error('  export ONEMIN_API_KEY=your-key-here');
  process.exit(1);
}

const client = new OneMinClient({ apiKey });

// --- Demo 1: Text-to-speech with TTS-1 HD ---
const result1 = await client.audio.speak(
  'Welcome to the 1min.ai SDK. This is a text-to-speech demo.',
  { model: Models.Audio.TTS_1_HD },
);
console.log('=== Text-to-Speech ===');
console.log(`Audio URL: ${result1.url}`);
console.log();

// --- Demo 2: Text-to-speech with ElevenLabs ---
const result2 = await client.audio.speak(
  'Hello from ElevenLabs voice synthesis.',
  { model: Models.Audio.ELEVENLABS_TTS, voice: 'Rachel' },
);
console.log(`=== Text-to-Speech (${Models.Audio.ELEVENLABS_TTS}) ===`);
console.log(`Audio URL: ${result2.url}`);
console.log();

// --- Demo 3: Transcribe audio from a URL ---
// Replace with a real audio URL to test transcription
const sampleAudioUrl = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3';
const result3 = await client.audio.transcribe(sampleAudioUrl, { model: Models.Audio.WHISPER_1 });
console.log('=== Speech-to-Text (Whisper) ===');
console.log(`Transcript: ${result3.content}`);
console.log();
