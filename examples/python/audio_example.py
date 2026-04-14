"""Audio domain example -- demonstrates speak() (TTS) and transcribe() (STT)."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Text-to-speech with TTS-1 HD ---
result = client.audio.speak(
    "Welcome to the 1min.ai SDK. This is a text-to-speech demo.",
    model=Models.Audio.TTS_1_HD,
)
print("=== Text-to-Speech ===")
print(f"Audio URL: {result.url}")
print()

# --- Demo 2: Text-to-speech with ElevenLabs ---
result = client.audio.speak(
    "Hello from ElevenLabs voice synthesis.",
    model=Models.Audio.ELEVENLABS_TTS,
    voice="Rachel",
)
print(f"=== Text-to-Speech ({Models.Audio.ELEVENLABS_TTS}) ===")
print(f"Audio URL: {result.url}")
print()

# --- Demo 3: Transcribe audio from a URL ---
# Replace with a real audio URL to test transcription
sample_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
result = client.audio.transcribe(sample_audio_url, model=Models.Audio.WHISPER_1)
print("=== Speech-to-Text (Whisper) ===")
print(f"Transcript: {result.content}")
print()
