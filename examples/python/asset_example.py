"""Asset domain example -- demonstrates upload() and list() for file management."""
import os
import sys
from onemin import OneMinClient

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Upload a file (create a small test PNG in memory) ---
# Minimal 1x1 transparent PNG (67 bytes)
TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

result = client.asset.upload(("test.png", TINY_PNG))
print("=== Asset Uploaded ===")
print(f"Asset ID:     {result.asset_id}")
print(f"URL:          {result.url}")
print(f"Content-type: {result.content_type}")
print()

# --- Demo 2: List assets ---
assets = client.asset.list()
print("=== Asset List ===")
if assets:
    for asset in assets[:5]:  # show first 5
        print(f"  - {asset.get('id')} | {asset.get('contentType')} | {asset.get('location', '')}")
else:
    print("  (no assets found)")
print()

# --- Demo 3: Get a specific asset by ID ---
if result.asset_id:
    fetched = client.asset.get(result.asset_id)
    print("=== Asset Retrieved ===")
    print(f"URL: {fetched.url}")
    print()
