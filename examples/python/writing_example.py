"""Writing domain example -- demonstrates summarize() and translate() with model constants."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

LONG_TEXT = (
    "Artificial intelligence has undergone rapid advancement over the past decade. "
    "Machine learning models have grown from simple classifiers to large language models "
    "capable of reasoning, writing, and even generating images and video. "
    "These systems are now integrated into products used by billions of people worldwide, "
    "transforming how we work, communicate, and create."
)

# --- Demo 1: Summarize a block of text ---
result = client.writing.summarize(LONG_TEXT, model=Models.Text.GPT_4O)
print("=== Summarize ===")
print(result.content)
print()

# --- Demo 2: Translate text to Spanish ---
result = client.writing.translate(
    "Hello, how are you today?",
    target_language="es",
    model=Models.Text.GPT_4O,
)
print("=== Translate to Spanish ===")
print(result.content)
print()

# --- Demo 3: Check grammar ---
result = client.writing.check_grammar(
    "Their going to the store to buys some groceries.",
    model=Models.Text.GPT_4O,
)
print("=== Grammar Check ===")
print(result.content)
print()
