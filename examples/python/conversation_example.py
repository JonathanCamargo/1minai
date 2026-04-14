"""Conversation domain example -- demonstrates create() and send() for multi-turn chat."""
import os
import sys
from onemin import OneMinClient, Models

api_key = os.environ.get("ONEMIN_API_KEY")
if not api_key:
    print("Set ONEMIN_API_KEY environment variable to run this example.")
    print("  export ONEMIN_API_KEY=your-key-here")
    sys.exit(1)

client = OneMinClient(api_key=api_key)

# --- Demo 1: Create a conversation ---
conv = client.conversation.create(
    title="SDK Demo Conversation",
    model=Models.Text.GPT_4O,
)
print("=== Conversation Created ===")
print(f"Conversation ID: {conv.conversation_id}")
print()

# --- Demo 2: Send messages in the conversation ---
reply = client.conversation.send(
    conv.conversation_id,
    "Hi! My name is Alice. Can you remember that?",
    model=Models.Text.GPT_4O,
)
print("=== First message ===")
print(f"Response: {reply.content}")
print()

reply = client.conversation.send(
    conv.conversation_id,
    "What is my name?",
    model=Models.Text.GPT_4O,
)
print("=== Follow-up message ===")
print(f"Response: {reply.content}")
print()
