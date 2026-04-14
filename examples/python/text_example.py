"""Text domain example -- demonstrates chat() with default and named model constants."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Basic chat with default model (gpt-4o) ---
result = client.text.chat("What is the speed of light in a vacuum?")
print("=== Basic chat (gpt-4o) ===")
print(result.content)
print()

# --- Demo 2: Chat with a specific model via Models constant ---
result = client.text.chat(
    "Explain recursion in one sentence.",
    model=Models.Text.CLAUDE_3_5_SONNET,
)
print(f"=== Chat with {Models.Text.CLAUDE_3_5_SONNET} ===")
print(result.content)
print()

# --- Demo 3: Streaming chat ---
print("=== Streaming chat (gpt-4o) ===")
for token in client.text.chat("Count from 1 to 5.", stream=True):
    print(token, end="", flush=True)
print()
