#!/usr/bin/env python3
"""Summarize text from a file, stdin, or a string argument."""
import argparse
import os
import sys
from pathlib import Path

from fileman.envars import load_env
from onemin import OneMinClient, Models


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env()


def _read_input(args: argparse.Namespace) -> str:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if args.stdin:
        return sys.stdin.read()
    return args.text


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize text using 1min.ai.")
    parser.add_argument("text", nargs="?", help="Text to summarize")
    parser.add_argument("-f", "--file", help="Path to a text file to summarize")
    parser.add_argument(
        "--stdin", action="store_true", help="Read text from stdin"
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("ONEMIN_API_KEY"),
        help="1min.ai API key (falls back to ONEMIN_API_KEY env var)",
    )
    parser.add_argument(
        "-m", "--model",
        default=Models.Text.GPT_4O,
        help=f"Model to use (default: {Models.Text.GPT_4O})",
    )
    parser.add_argument(
        "-w", "--words",
        type=int,
        default=None,
        help="Target summary length in words",
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")

    input_text = _read_input(args)
    if not input_text or not input_text.strip():
        parser.error("No text provided. Pass text, --file, or --stdin.")

    client = OneMinClient(api_key=args.api_key)
    result = client.writing.summarize(input_text, model=args.model, maxLength=args.words)
    print(result.content)


if __name__ == "__main__":
    main()
