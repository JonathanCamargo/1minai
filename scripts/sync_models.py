"""Generate Python and TypeScript model-constant modules from data/models.json.

Single source of truth: ``data/models.json``. This script regenerates two files:

* ``python/src/onemin/_models_data.py`` -- importable as ``from onemin._models_data import Models``.
* ``typescript/src/models-data.ts``     -- importable as ``import { Models } from './models-data.js'``.

Both files are marked DO NOT EDIT and are checked into source control. Running
the script on an unchanged ``models.json`` is a no-op (byte-identical output);
that property is what the GitHub Actions ``models-sync`` workflow checks.

Usage::

    python scripts/sync_models.py             # writes generated files
    python scripts/sync_models.py --check     # exits non-zero if the working
                                              # copy is stale (use in CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "models.json"
PY_OUT_PATH = REPO_ROOT / "python" / "src" / "onemin" / "_models_data.py"
TS_OUT_PATH = REPO_ROOT / "typescript" / "src" / "models-data.ts"

DOMAIN_ORDER = ("text", "image", "audio", "video")
DOMAIN_TO_CLASS = {"text": "Text", "image": "Image", "audio": "Audio", "video": "Video"}


def _load() -> dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "domains" not in data:
        raise ValueError(f"{DATA_PATH} missing top-level 'domains' object")
    return data


def _validate(data: dict[str, Any]) -> None:
    """Check structural invariants the codegen relies on.

    Catches drift early -- a bad models.json fails the script, not the build.
    """
    seen_constants_per_domain: dict[str, set[str]] = {}
    seen_ids_per_domain: dict[str, set[str]] = {}
    for domain in DOMAIN_ORDER:
        info = data["domains"].get(domain)
        if info is None:
            raise ValueError(f"missing domain '{domain}' in models.json")
        if "models" not in info:
            raise ValueError(f"domain '{domain}' missing 'models' list")
        seen_constants_per_domain[domain] = set()
        seen_ids_per_domain[domain] = set()
        for entry in info["models"]:
            for required in ("constant", "id", "provider", "label"):
                if required not in entry:
                    raise ValueError(
                        f"domain '{domain}' entry missing '{required}': {entry!r}"
                    )
            if entry["constant"] in seen_constants_per_domain[domain]:
                raise ValueError(
                    f"duplicate constant {entry['constant']!r} in domain '{domain}'"
                )
            if entry["id"] in seen_ids_per_domain[domain]:
                raise ValueError(
                    f"duplicate id {entry['id']!r} in domain '{domain}' "
                    f"(constants: {entry['constant']!r} clashes with another entry)"
                )
            seen_constants_per_domain[domain].add(entry["constant"])
            seen_ids_per_domain[domain].add(entry["id"])


def _python_source(data: dict[str, Any]) -> str:
    """Render the Python module."""
    out: list[str] = []
    out.append('"""Generated model constants for the 1min.ai Python SDK.')
    out.append("")
    out.append("DO NOT EDIT. Regenerate with ``python scripts/sync_models.py``.")
    out.append("Source of truth: ``data/models.json``.")
    out.append('"""')
    out.append("")
    out.append("from __future__ import annotations")
    out.append("")
    out.append("")
    out.append("class Models:")
    out.append('    """Model identifiers grouped by capability domain."""')
    for domain in DOMAIN_ORDER:
        info = data["domains"][domain]
        cls = DOMAIN_TO_CLASS[domain]
        out.append("")
        out.append(f"    class {cls}:")
        out.append(f'        """{cls} models -- {info["feature_type"]} via {info["endpoint"]}."""')
        out.append("")
        for entry in info["models"]:
            out.append(f'        {entry["constant"]} = "{entry["id"]}"')
    out.append("")
    out.append("")
    out.append("MODEL_CATALOGUE: dict[str, list[dict[str, str]]] = {")
    for domain in DOMAIN_ORDER:
        out.append(f'    "{domain}": [')
        for entry in data["domains"][domain]["models"]:
            tags = entry.get("tags", [])
            tags_repr = ", ".join(f'"{t}"' for t in tags)
            out.append("        {")
            out.append(f'            "constant": "{entry["constant"]}",')
            out.append(f'            "id": "{entry["id"]}",')
            out.append(f'            "provider": "{entry["provider"]}",')
            out.append(f'            "label": "{entry["label"]}",')
            if tags:
                out.append(f'            "tags": [{tags_repr}],')
            out.append("        },")
        out.append("    ],")
    out.append("}")
    out.append("")
    out.append("")
    out.append("def all_ids(domain: str | None = None) -> list[str]:")
    out.append('    """Return every known model id, optionally filtered by domain."""')
    out.append("    if domain is None:")
    out.append("        return [m['id'] for entries in MODEL_CATALOGUE.values() for m in entries]")
    out.append("    return [m['id'] for m in MODEL_CATALOGUE.get(domain, [])]")
    out.append("")
    return "\n".join(out)


def _ts_source(data: dict[str, Any]) -> str:
    """Render the TypeScript module."""
    out: list[str] = []
    out.append("/**")
    out.append(" * Generated model constants for the 1min.ai TypeScript SDK.")
    out.append(" *")
    out.append(" * DO NOT EDIT. Regenerate with `python scripts/sync_models.py`.")
    out.append(" * Source of truth: `data/models.json`.")
    out.append(" */")
    out.append("")
    out.append("export const Models = {")
    for domain in DOMAIN_ORDER:
        info = data["domains"][domain]
        cls = DOMAIN_TO_CLASS[domain]
        out.append(f"  /** {cls} models -- {info['feature_type']} via {info['endpoint']}. */")
        out.append(f"  {cls}: {{")
        for entry in info["models"]:
            out.append(f"    /** {entry['label']} -- {entry['provider']} */")
            out.append(f'    {entry["constant"]}: "{entry["id"]}",')
        out.append("  },")
    out.append("} as const;")
    out.append("")
    out.append("export type ModelId =")
    parts = [f"  | (typeof Models.{DOMAIN_TO_CLASS[d]})[keyof typeof Models.{DOMAIN_TO_CLASS[d]}]"
             for d in DOMAIN_ORDER]
    out.append("\n".join(parts) + ";")
    out.append("")
    out.append("export interface ModelEntry {")
    out.append("  constant: string;")
    out.append("  id: string;")
    out.append("  provider: string;")
    out.append("  label: string;")
    out.append("  tags?: string[];")
    out.append("}")
    out.append("")
    out.append("export const MODEL_CATALOGUE: Record<string, ModelEntry[]> = {")
    for domain in DOMAIN_ORDER:
        out.append(f"  {domain}: [")
        for entry in data["domains"][domain]["models"]:
            tags = entry.get("tags")
            tags_part = f', tags: {json.dumps(tags)}' if tags else ""
            out.append(
                f'    {{ constant: "{entry["constant"]}", id: "{entry["id"]}", '
                f'provider: "{entry["provider"]}", label: "{entry["label"]}"{tags_part} }},'
            )
        out.append("  ],")
    out.append("};")
    out.append("")
    out.append("export function allIds(domain?: keyof typeof MODEL_CATALOGUE): string[] {")
    out.append("  if (domain === undefined) {")
    out.append("    return Object.values(MODEL_CATALOGUE).flat().map((m) => m.id);")
    out.append("  }")
    out.append("  return (MODEL_CATALOGUE[domain] ?? []).map((m) => m.id);")
    out.append("}")
    out.append("")
    return "\n".join(out)


def _write_if_changed(path: Path, content: str) -> bool:
    """Write content if it differs from the existing file. Returns True if the file was changed."""
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any generated file would change. Use in CI.",
    )
    args = parser.parse_args()

    data = _load()
    _validate(data)
    py_src = _python_source(data)
    ts_src = _ts_source(data)

    if args.check:
        stale = []
        if not PY_OUT_PATH.exists() or PY_OUT_PATH.read_text(encoding="utf-8") != py_src:
            stale.append(str(PY_OUT_PATH.relative_to(REPO_ROOT)))
        if not TS_OUT_PATH.exists() or TS_OUT_PATH.read_text(encoding="utf-8") != ts_src:
            stale.append(str(TS_OUT_PATH.relative_to(REPO_ROOT)))
        if stale:
            print("Generated model constants are stale. Run `python scripts/sync_models.py`.")
            for p in stale:
                print(f"  - {p}")
            return 1
        print("Generated model constants are up to date.")
        return 0

    py_changed = _write_if_changed(PY_OUT_PATH, py_src)
    ts_changed = _write_if_changed(TS_OUT_PATH, ts_src)
    print(f"python: {'wrote' if py_changed else 'unchanged'} {PY_OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"typescript: {'wrote' if ts_changed else 'unchanged'} {TS_OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
