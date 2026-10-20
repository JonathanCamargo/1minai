#!/usr/bin/env python3
"""List the chat models 1min.ai currently offers, with context size and price.

Reads the public live catalogue, so it shows models that are not (yet) in
data/models.json. Any id listed here can be passed to -m in the other scripts.

Usage:
    python models.py                      # all chat models, cheapest input first
    python models.py claude               # filter by name / id / provider
    python models.py --min-context 500000 # only long-context models
"""
import argparse

import httpx

MODELS_URL = "https://api.1min.ai/models"


def fetch_models(feature: str = "UNIFY_CHAT_WITH_AI") -> list[dict]:
    """Return the active models supporting ``feature`` from the live catalogue."""
    response = httpx.get(MODELS_URL, params={"feature": feature}, timeout=30)
    response.raise_for_status()
    return [m for m in response.json()["models"] if m.get("status") == "ACTIVE"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List live 1min.ai chat models with context size and price.",
    )
    parser.add_argument("search", nargs="?", default="", help="Filter text")
    parser.add_argument(
        "--min-context", type=int, default=0,
        help="Only show models with at least this many context tokens",
    )
    args = parser.parse_args()

    rows = []
    for model in fetch_models():
        credit = model.get("creditMetadata") or {}
        haystack = f"{model['modelId']} {model.get('name', '')} {model.get('provider', '')}"
        if args.search.lower() not in haystack.lower():
            continue
        if (credit.get("CONTEXT") or 0) < args.min_context:
            continue
        rows.append((
            credit.get("INPUT") or 0,
            model["modelId"],
            credit.get("CONTEXT") or 0,
            credit.get("OUTPUT") or 0,
            "+".join((model.get("modality") or {}).get("INPUT", [])),
        ))

    width = max((len(r[1]) for r in rows), default=8)
    print(f"{'model id':<{width}}  {'context':>9}  {'in':>6}  {'out':>6}  input")
    for price_in, model_id, context, price_out, modality in sorted(rows):
        print(f"{model_id:<{width}}  {context:>9,}  {price_in:>6g}  {price_out:>6g}  {modality}")
    print(f"\n{len(rows)} models. 'in'/'out' are 1min.ai's listed credit rates (lower is cheaper).")


if __name__ == "__main__":
    main()
