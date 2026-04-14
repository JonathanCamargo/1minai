"""Image domain example -- demonstrates generate(), remove_background(), and model constants."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Generate an image with DALL-E 3 ---
result = client.image.generate(
    "A photorealistic golden retriever playing in autumn leaves",
    model=Models.Image.DALL_E_3,
    width=1024,
    height=1024,
)
print("=== Generated image (DALL-E 3) ===")
print(f"URL: {result.url}")
print()

# --- Demo 2: Generate with Flux Schnell (faster model) ---
result = client.image.generate(
    "A minimalist logo of a mountain peak at sunrise",
    model=Models.Image.FLUX_SCHNELL,
)
print(f"=== Generated image ({Models.Image.FLUX_SCHNELL}) ===")
print(f"URL: {result.url}")
print()

# --- Demo 3: Remove background from an online image ---
sample_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg"
result = client.image.remove_background(sample_image_url)
print("=== Background removed ===")
print(f"URL: {result.url}")
print()
