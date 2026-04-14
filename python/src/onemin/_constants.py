BASE_URL = "https://api.1min.ai"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_BASE_DELAY = 0.5
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
API_KEY_HEADER = "API-KEY"

# Per-domain timeout defaults (seconds) per INFRA-07.
# Resources pass their domain timeout to _request() so that
# image/video/audio operations get longer timeouts than text.
DOMAIN_TIMEOUTS: dict[str, float] = {
    "text": 30.0,
    "image": 90.0,
    "audio": 90.0,
    "video": 300.0,
    "writing": 30.0,
    "conversation": 30.0,
    "asset": 30.0,
}
