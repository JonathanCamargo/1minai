import os, json, httpx
r = httpx.post(
    "https://api.1min.ai/api/chat-with-ai",
    headers={"API-KEY": os.environ["ONEMIN_API_KEY"], "Content-Type": "application/json"},
    json={
        "type": "UNIFY_CHAT_WITH_AI",
        "model": "gpt-4o",
        "promptObject": {"prompt": "What is 2+2?"},
    },
    timeout=30,
)
print("status:", r.status_code)
print("body:", r.text[:2000])