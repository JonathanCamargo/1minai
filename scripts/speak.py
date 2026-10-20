#!/usr/bin/env python3
"""Convert text to speech using 1min.ai TTS models."""
import argparse
import os

from pathlib import Path
from fileman.envars import load_env
from onemin import OneMinClient, Models


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env(project_env=Path(__file__).parent / ".." / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(description="Text-to-speech using 1min.ai.")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument(
        "-f", "--file", help="Path to a text file to read aloud"
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("ONEMIN_API_KEY"),
        help="1min.ai API key (falls back to ONEMIN_API_KEY env var)",
    )
    parser.add_argument(
        "-m", "--model",
        default=Models.Audio.TTS_1,
        help=f"TTS model (default: {Models.Audio.TTS_1})",
    )
    parser.add_argument(
        "-v", "--voice", default=None, help="Voice name (e.g., 'Rachel')"
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.error("No text provided. Pass text or use -f/--file.")

    client = OneMinClient(api_key=args.api_key)
    result = client.audio.speak(text, model=args.model, voice=args.voice)
    print(result.url)


if __name__ == "__main__":
    main()
