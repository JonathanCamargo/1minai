"""Video domain example -- demonstrates generate() (text-to-video) with model constants."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Generate a video with Luma AI ---
# Note: video generation auto-polls until completion (may take 1-3 minutes)
print("Generating video with Luma AI (this may take a few minutes)...")
result = client.video.generate(
    "A serene time-lapse of clouds drifting over mountain peaks at golden hour",
    model=Models.Video.LUMA_AI,
    aspect_ratio="16:9",
)
print("=== Generated video (Luma AI) ===")
print(f"URL: {result.url}")
print()

# --- Demo 2: Generate a video with Kling ---
print("Generating video with Kling...")
result = client.video.generate(
    "A butterfly landing on a flower in slow motion",
    model=Models.Video.KLING,
)
print(f"=== Generated video ({Models.Video.KLING}) ===")
print(f"URL: {result.url}")
print()
