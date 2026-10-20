"""Refresh data/models.json from the live 1min.ai model catalogue.

The public ``GET /models?feature=...`` endpoint lists every model the API
currently accepts, so no API key is needed. For each domain this script:

* keeps entries whose id is still live, untouched (constants stay stable,
  hand-added tags such as ``polled`` survive);
* deletes entries whose id is gone -- the API rejects those with
  ``UNSUPPORTED_MODEL``;
* appends newly listed models with a constant derived from the id.

It then regenerates the Python/TypeScript constants via sync_models.py.

Usage::

    python scripts/update_models.py            # update models.json + codegen
    python scripts/update_models.py --check    # exit 1 if anything would change
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "models.json"
MODELS_URL = "https://api.1min.ai/models"

# domain -> [(feature type queried upstream, tag given to new entries or None)]
# Every model valid for any of a domain's features gets a constant.
DOMAIN_FEATURES: dict[str, list[tuple[str, str | None]]] = {
    "text": [("UNIFY_CHAT_WITH_AI", None)],
    "image": [
        ("IMAGE_GENERATOR", None),
        ("IMAGE_TO_PROMPT", None),
        ("IMAGE_VARIATOR", None),
        ("IMAGE_UPSCALER", None),
        ("IMAGE_EXTENDER", None),
        ("IMAGE_EDITOR", None),
        ("IMAGE_INPAINTER", None),
        ("IMAGE_OBJECT_REMOVER", None),
        ("BACKGROUND_REMOVER", None),
        ("BACKGROUND_REPLACER", None),
        ("TEXT_REMOVER", None),
        ("SEARCH_AND_REPLACE", None),
        ("FACE_SWAPPER", None),
        ("IMAGE_3D_GENERATOR", None),
    ],
    "audio": [
        ("TEXT_TO_SPEECH", "tts"),
        ("SPEECH_TO_TEXT", "stt"),
        ("MUSIC_GENERATOR", "music"),
        ("AUDIO_TRANSLATOR", "translate"),
    ],
    "video": [("TEXT_TO_VIDEO", None), ("IMAGE_TO_VIDEO", None)],
}

# Features that share the chat model list; tracked for defaults only.
WRITING_FEATURES = (
    "SUMMARIZER", "REWRITER", "PARAPHRASER", "CONTENT_EXPANDER",
    "CONTENT_SHORTENER", "CONTENT_TRANSLATOR", "GRAMMAR_CHECKER",
    "KEYWORD_RESEARCH", "CONTENT_GENERATOR_BLOG_ARTICLE", "YOUTUBE_SUMMARIZER",
)

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-", re.IGNORECASE)


def _sanitize(text: str) -> str:
    constant = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").upper()
    return f"M_{constant}" if constant[:1].isdigit() else constant


def _constant_for(model: dict[str, Any], taken: set[str]) -> str:
    """Derive a readable, unique constant name for a new model."""
    model_id = model["modelId"]
    if _UUID_RE.match(model_id):
        # Opaque ids (Leonardo, ...) -- name them after the display name.
        short = model.get("name") or model_id
    else:
        # "us.anthropic.claude-opus-5-5" -> "claude-opus-5-5",
        # "meta/llama-4:abc123" -> "llama-4", "...-v1:0" -> "..."
        short = model_id.rsplit("/", 1)[-1].split(":", 1)[0]
        short = re.sub(r"^us\.anthropic\.", "", short)
        short = re.sub(r"-v\d+$", "", short)
    for candidate in (_sanitize(short), _sanitize(model_id)):
        if candidate and candidate not in taken:
            return candidate
    n = 2
    while f"{_sanitize(model_id)}_{n}" in taken:
        n += 1
    return f"{_sanitize(model_id)}_{n}"


def _fetch(client: httpx.Client, feature: str) -> list[dict[str, Any]]:
    response = client.get(MODELS_URL, params={"feature": feature})
    response.raise_for_status()
    models = response.json()["models"]
    return [
        m for m in models
        if m.get("status") == "ACTIVE" and m["modelId"] != "NOT_APPLICABLE"
    ]


def update(data: dict[str, Any], client: httpx.Client) -> list[str]:
    """Update ``data`` in place. Returns human-readable change lines."""
    changes: list[str] = []
    by_feature: dict[str, list[str]] = {}

    def listing(feature: str) -> list[dict[str, Any]]:
        listed = _fetch(client, feature)
        if not listed:
            # An empty listing means the endpoint misbehaved, not that
            # every model vanished -- refuse to wipe anything.
            raise RuntimeError(f"live catalogue returned no models for {feature}")
        by_feature[feature] = [m["modelId"] for m in listed]
        return listed

    for domain, features in DOMAIN_FEATURES.items():
        live: dict[str, tuple[dict[str, Any], str | None]] = {}
        for feature, tag in features:
            for model in listing(feature):
                live.setdefault(model["modelId"], (model, tag))

        entries = data["domains"][domain]["models"]
        kept = [e for e in entries if e["id"] in live]
        for entry in entries:
            if entry["id"] not in live:
                changes.append(f"- {domain}: {entry['constant']} ({entry['id']})")

        known = {e["id"] for e in kept}
        taken = {e["constant"] for e in kept}
        for model_id, (model, tag) in live.items():
            if model_id in known:
                continue
            constant = _constant_for(model, taken)
            taken.add(constant)
            entry = {
                "constant": constant,
                "id": model_id,
                "provider": model.get("provider") or "unknown",
                "label": (model.get("name") or model_id).replace('"', "'"),
            }
            if tag:
                entry["tags"] = [tag]
            kept.append(entry)
            changes.append(f"+ {domain}: {constant} ({model_id})")
        data["domains"][domain]["models"] = kept

    for feature in WRITING_FEATURES:
        listing(feature)

    # Per-feature valid models and the default each SDK method uses. A default
    # is only replaced when upstream stops accepting it.
    features_data = data.setdefault("features", {})
    for feature, ids in by_feature.items():
        entry = features_data.setdefault(feature, {})
        default = entry.get("default")
        if default not in ids:
            entry["default"] = ids[0]
            changes.append(f"! {feature}: default {default} -> {ids[0]} (review this choice)")
        elif entry.get("models") != ids:
            changes.append(f"~ {feature}: model list changed ({len(ids)} models)")
        entry["models"] = ids
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report differences and exit 1 without writing anything.",
    )
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    with httpx.Client(timeout=30) as client:
        changes = update(data, client)

    if not changes:
        print("data/models.json already matches the live catalogue.")
        return 0
    print("\n".join(changes))
    print(f"\n{len(changes)} change(s): '+' added, '-' removed, '~' list changed, '!' default replaced.")
    if args.check:
        return 1

    DATA_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return subprocess.call([sys.executable, str(REPO_ROOT / "scripts" / "sync_models.py")])


if __name__ == "__main__":
    sys.exit(main())
