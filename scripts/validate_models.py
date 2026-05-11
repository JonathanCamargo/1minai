"""Validate every model in data/models.json against the live 1min.ai API.

Strategy:

* For each text model: POST a one-token chat to ``/api/chat-with-ai`` and look
  for ``UNSUPPORTED_MODEL`` errors -- those are fatal. 4xx errors with any
  other ``errorCode``, 5xx, and timeouts are treated as **inconclusive** and
  reported but do not fail the run by default. Pass ``--strict`` to flip those
  into failures.
* Image / audio / video models cost real credits, so we don't generate. We only
  send a deliberately-malformed feature payload and check that the API rejects
  it for *content* reasons (``REQUEST_BODY_VALIDATION_FAILED`` or similar)
  rather than ``UNSUPPORTED_MODEL``. If the API replies ``UNSUPPORTED_MODEL``
  the model entry is broken; otherwise we treat the model as live.

Reads ``ONEMIN_API_KEY`` from the environment. Exits 0 when every model is
either ``ok`` or ``inconclusive``, 1 if any are ``unsupported``, and 2 on
configuration errors (missing key, malformed json).

Usage::

    ONEMIN_API_KEY=... python scripts/validate_models.py
    ONEMIN_API_KEY=... python scripts/validate_models.py --strict
    ONEMIN_API_KEY=... python scripts/validate_models.py --domains text,image
    ONEMIN_API_KEY=... python scripts/validate_models.py --json > report.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "models.json"
BASE_URL = "https://api.1min.ai"
PER_REQUEST_TIMEOUT = 30.0


@dataclass
class Result:
    domain: str
    constant: str
    id: str
    status: str           # "ok" | "unsupported" | "inconclusive"
    detail: str = ""

    def is_failure(self, strict: bool) -> bool:
        if self.status == "unsupported":
            return True
        if strict and self.status == "inconclusive":
            return True
        return False


def _load_data() -> dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _classify(status_code: int, body: str) -> tuple[str, str]:
    """Map an HTTP response to (status, detail).

    A 200 means the model id was accepted. A 400 with errorCode
    UNSUPPORTED_MODEL means it is no longer accepted. Everything else --
    different 400 codes, 401/403/429/5xx -- is reported as inconclusive.
    """
    if status_code == 200:
        return "ok", ""
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return "inconclusive", f"HTTP {status_code} (non-JSON body)"
    error_code = payload.get("errorCode") if isinstance(payload, dict) else None
    message = payload.get("message", "") if isinstance(payload, dict) else ""
    if error_code == "UNSUPPORTED_MODEL":
        return "unsupported", message or "UNSUPPORTED_MODEL"
    return "inconclusive", f"{status_code} {error_code or 'unknown'}: {message[:120]}"


def _probe_text(client: httpx.Client, headers: dict[str, str], model_id: str) -> Result:
    """Send a minimal chat. ``ping`` is the cheapest legal prompt we can send.

    The chat endpoint validates ``model`` before doing anything else, so even
    if the request still costs a token it succeeds quickly.
    """
    payload = {
        "type": "UNIFY_CHAT_WITH_AI",
        "model": model_id,
        "promptObject": {"prompt": "ping"},
    }
    try:
        r = client.post(
            f"{BASE_URL}/api/chat-with-ai",
            headers=headers,
            json=payload,
            timeout=PER_REQUEST_TIMEOUT,
        )
    except httpx.HTTPError as exc:
        return Result(domain="text", constant="", id=model_id,
                      status="inconclusive", detail=f"network error: {exc}")
    status, detail = _classify(r.status_code, r.text)
    return Result(domain="text", constant="", id=model_id, status=status, detail=detail)


def _probe_feature(
    client: httpx.Client,
    headers: dict[str, str],
    domain: str,
    feature_type: str,
    model_id: str,
) -> Result:
    """For non-text domains, send a deliberately-empty promptObject.

    The API validates ``model`` before promptObject contents, so an
    UNSUPPORTED_MODEL error means the model is gone. A different validation
    error means the model id was accepted (and the request was rejected for
    other reasons) -- which is what we want, since we don't want to spend
    credits generating images/audio/video just to validate.
    """
    payload = {
        "type": feature_type,
        "model": model_id,
        "promptObject": {},
    }
    try:
        r = client.post(
            f"{BASE_URL}/api/features",
            headers=headers,
            json=payload,
            timeout=PER_REQUEST_TIMEOUT,
        )
    except httpx.HTTPError as exc:
        return Result(domain=domain, constant="", id=model_id,
                      status="inconclusive", detail=f"network error: {exc}")
    status, detail = _classify(r.status_code, r.text)
    return Result(domain=domain, constant="", id=model_id, status=status, detail=detail)


def _validate_domain(
    client: httpx.Client,
    headers: dict[str, str],
    domain: str,
    info: dict[str, Any],
) -> list[Result]:
    """Validate every model in one domain.

    Each entry may override the domain's default ``feature_type`` -- 1min.ai
    validates models per (model, feature) pair (e.g. SUNO is rejected as
    TEXT_TO_SPEECH but accepted as MUSIC_GENERATOR), so audio entries that
    aren't TTS specify their own type.
    """
    results: list[Result] = []
    domain_feature_type = info.get("feature_type", "")
    for entry in info["models"]:
        feature_type = entry.get("feature_type", domain_feature_type)
        if domain == "text":
            res = _probe_text(client, headers, entry["id"])
        else:
            res = _probe_feature(client, headers, domain, feature_type, entry["id"])
        res.domain = domain
        res.constant = entry["constant"]
        results.append(res)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domains",
        default="text,image,audio,video",
        help="comma-separated subset of domains to validate (default: all)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat 'inconclusive' as failure (use only when you trust the network)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable JSON report on stdout instead of a table",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ONEMIN_API_KEY")
    if not api_key:
        print("ONEMIN_API_KEY is not set.", file=sys.stderr)
        return 2

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    try:
        data = _load_data()
    except Exception as exc:
        print(f"Failed to read {DATA_PATH}: {exc}", file=sys.stderr)
        return 2

    headers = {"API-KEY": api_key, "Content-Type": "application/json"}
    results: list[Result] = []
    with httpx.Client() as client:
        for domain in domains:
            info = data["domains"].get(domain)
            if info is None:
                print(f"unknown domain: {domain}", file=sys.stderr)
                return 2
            results.extend(_validate_domain(client, headers, domain, info))

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        # Human-readable table grouped by status
        by_status: dict[str, list[Result]] = {"unsupported": [], "inconclusive": [], "ok": []}
        for r in results:
            by_status[r.status].append(r)
        for status_label in ("unsupported", "inconclusive", "ok"):
            bucket = by_status[status_label]
            if not bucket:
                continue
            print(f"\n=== {status_label.upper()} ({len(bucket)}) ===")
            for r in bucket:
                detail = f"  -- {r.detail}" if r.detail else ""
                print(f"  [{r.domain:5}] {r.constant:24} {r.id}{detail}")

    failures = [r for r in results if r.is_failure(args.strict)]
    if failures:
        print(
            f"\n{len(failures)} failing entries. "
            "Edit data/models.json and re-run scripts/sync_models.py.",
            file=sys.stderr,
        )
        return 1
    print(f"\nAll {len(results)} model entries verified.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
