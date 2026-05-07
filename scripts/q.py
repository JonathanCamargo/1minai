#!/usr/bin/env python3
"""Quick CLI script to ask a 1min.ai model a text question.

Usage:
    python q.py "what is the tallest building in the world?"
"""
import argparse
import os
from pathlib import Path
from fileman.envars import load_env
from onemin import OneMinClient, Models


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env(project_env=Path(__file__).parent / ".." / ".env")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask a 1min.ai model a text question.",
    )
    parser.add_argument("question", help="The question to ask the model")
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

    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")

    client = OneMinClient(api_key=args.api_key)
    result = client.text.chat(args.question, model=args.model)
    print(result.content)


if __name__ == "__main__":
    main()
