#!/usr/bin/env python3
"""Generate an image from a text prompt."""
import argparse
import os

from fileman.envars import load_env
from onemin import OneMinClient, Models


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an image using 1min.ai.")
    parser.add_argument("prompt", help="Text prompt describing the image")
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("ONEMIN_API_KEY"),
        help="1min.ai API key (falls back to ONEMIN_API_KEY env var)",
    )
    parser.add_argument(
        "-m", "--model",
        default=Models.Image.DALL_E_3,
        help=f"Model to use (default: {Models.Image.DALL_E_3})",
    )
    parser.add_argument(
        "-W", "--width", type=int, default=1024, help="Image width (default: 1024)"
    )
    parser.add_argument(
        "-H", "--height", type=int, default=1024, help="Image height (default: 1024)"
    )
    parser.add_argument(
        "-n", type=int, default=1, dest="count", help="Number of images (default: 1)"
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")

    client = OneMinClient(api_key=args.api_key)
    result = client.image.generate(
        args.prompt,
        model=args.model,
        width=args.width,
        height=args.height,
        n=args.count,
    )

    if result.urls:
        for url in result.urls:
            print(url)
    elif result.url:
        print(result.url)
    else:
        print("No image URL returned.")


if __name__ == "__main__":
    main()
