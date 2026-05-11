"""Debug script to test what feature types the 1min.ai API actually accepts.

Run this and share the output with 1min.ai support.
"""
import os
import httpx

API_KEY = os.environ.get("ONEMIN_API_KEY")
if not API_KEY:
    print("Set ONEMIN_API_KEY environment variable.")
    exit(1)

BASE_URL = "https://api.1min.ai"
HEADERS = {"API-KEY": API_KEY, "Content-Type": "application/json"}

# Test 1: Simple text chat (CHAT_WITH_AI)
print("=" * 60)
print("Test 1: CHAT_WITH_AI (basic text chat)")
print("=" * 60)
try:
    r = httpx.post(
        f"{BASE_URL}/api/features",
        headers=HEADERS,
        json={
            "type": "CHAT_WITH_AI",
            "model": "gpt-4o",
            "promptObject": {
                "prompt": "Say hello",
                "isMixed": False,
                "webSearch": False,
                "chatList": [],
            },
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: UNIFY_CHAT_WITH_AI (the migration notice said to use this)
print()
print("=" * 60)
print("Test 2: UNIFY_CHAT_WITH_AI (migration notice replacement)")
print("=" * 60)
try:
    r = httpx.post(
        f"{BASE_URL}/api/features",
        headers=HEADERS,
        json={
            "type": "UNIFY_CHAT_WITH_AI",
            "model": "gpt-4o",
            "promptObject": {
                "prompt": "Say hello",
                "isMixed": False,
                "webSearch": False,
                "chatList": [],
            },
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try IMAGE_GENERATOR just to verify the API key works at all
print()
print("=" * 60)
print("Test 3: IMAGE_GENERATOR (verify API key / connection works)")
print("=" * 60)
try:
    r = httpx.post(
        f"{BASE_URL}/api/features",
        headers=HEADERS,
        json={
            "type": "IMAGE_GENERATOR",
            "model": "dall-e-3",
            "promptObject": {
                "prompt": "A red circle",
                "numImages": 1,
            },
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Try the /api/conversations endpoint
print()
print("=" * 60)
print("Test 4: POST /api/conversations (create conversation)")
print("=" * 60)
try:
    r = httpx.post(
        f"{BASE_URL}/api/conversations",
        headers=HEADERS,
        json={
            "title": "Debug Test",
            "type": "CHAT_WITH_AI",
            "model": "gpt-4o",
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Try POSTing to /api/chat (if the unified endpoint lives there)
print()
print("=" * 60)
print("Test 5: POST /api/chat (possible unified endpoint?)")
print("=" * 60)
try:
    r = httpx.post(
        f"{BASE_URL}/api/chat",
        headers=HEADERS,
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Say hello"}],
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("If Test 3 (IMAGE_GENERATOR) works but Tests 1/2/4 fail,")
print("the chat endpoints are broken on 1min.ai's side.")
print("Share this output with support@1min.ai or their API team.")
