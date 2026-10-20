#!/usr/bin/env python3
"""Analyze scientific papers (PDF, text file, or URL) with a 1min.ai model.

Usage:
    python paper.py paper.pdf                         # structured summary
    python paper.py paper.pdf -t critique             # referee-style review
    python paper.py paper.pdf -q "What was the sample size?"
    python paper.py https://arxiv.org/abs/1706.03762 -t methods
    python paper.py a.pdf b.pdf --compare -o notes.md
    python paper.py -f "And how was that measured?"   # follow up on the last paper
"""
import argparse
import os
import re
import sys
from io import BytesIO
from pathlib import Path

import httpx
from fileman.envars import load_env
from onemin import OneMinClient, Models, OneMinError


# Load env vars: system env → ~/.env → <project_root>/.env (system wins)
load_env(project_env=Path(__file__).parent / ".." / ".env")

RULES = (
    "You are a careful scientific reader. Base every statement only on the "
    "paper text provided below. Cite the page for each specific claim or "
    "number as [p. N] using the page markers in the text. If something is "
    "not stated in the paper, write 'not reported' instead of guessing. "
    "Distinguish what the authors claim from what their data actually show."
)

TASKS = {
    "summary": (
        "Summarize this paper in Markdown with these sections: "
        "**Citation** (title, authors, year, venue if given), "
        "**Research question**, **Methods** (design, data/sample, analysis), "
        "**Key findings** (with effect sizes, statistics, and uncertainty), "
        "**Limitations** (those the authors state and those they do not), "
        "**Takeaway** (2 sentences)."
    ),
    "critique": (
        "Write a referee-style critique in Markdown: main claim, whether the "
        "design and statistics support it, threats to internal and external "
        "validity, confounders, missing controls or analyses, reproducibility "
        "(data/code availability), and questions you would put to the authors. "
        "End with an overall assessment of how strong the evidence is."
    ),
    "methods": (
        "Describe the methodology in enough detail to replicate it: study "
        "design, materials/datasets, sample and inclusion criteria, procedures, "
        "instruments, parameters, statistical tests, and software. List any "
        "detail needed for replication that is missing."
    ),
    "extract": (
        "Extract the paper into a single JSON object and output only the JSON. "
        "Keys: title, authors, year, venue, doi, study_type, research_question, "
        "sample (description, n), methods, main_findings (list of "
        "{finding, value, page}), limitations, funding, "
        "data_code_availability. Use null for anything not reported."
    ),
}

# Each analysis runs in a 1min.ai conversation; the id of the last one is kept
# here so -f/--follow-up can continue it without re-sending the paper.
STATE = Path.home() / ".onemin_paper_conversation"

COMPARE = (
    "Compare the papers below in Markdown. Start with a table (one row per "
    "paper: question, design, sample, main finding). Then discuss where they "
    "agree, where they conflict and why (methods, samples, definitions), and "
    "what remains unresolved. Refer to papers by the name in their header."
)


def _fetch(source: str) -> tuple[str, bytes]:
    """Return (name, raw bytes) for a local path or URL."""
    if not re.match(r"https?://", source):
        path = Path(source)
        return path.name, path.read_bytes()
    # arXiv abstract pages -> the PDF itself
    url = re.sub(r"arxiv\.org/abs/", "arxiv.org/pdf/", source)
    response = httpx.get(url, follow_redirects=True, timeout=60)
    response.raise_for_status()
    return url.rstrip("/").rsplit("/", 1)[-1] or "paper", response.content


def _to_text(name: str, data: bytes) -> str:
    """Extract text, inserting [p. N] markers so the model can cite pages."""
    if not data.startswith(b"%PDF"):
        return data.decode("utf-8", errors="replace")
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("Reading PDFs locally needs pypdf: pip install pypdf (or use --upload)")
    pages = PdfReader(BytesIO(data)).pages
    text = "\n\n".join(
        f"[p. {i}]\n{page.extract_text() or ''}" for i, page in enumerate(pages, 1)
    )
    if len(re.sub(r"\[p\. \d+\]|\s", "", text)) < 200 * len(pages):
        print(
            f"warning: {name}: very little extractable text (scanned PDF?); "
            "try --upload",
            file=sys.stderr,
        )
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze scientific papers using 1min.ai.",
    )
    parser.add_argument("sources", nargs="*", help="PDF/text file paths or URLs")
    parser.add_argument(
        "-f", "--follow-up", metavar="QUESTION",
        help="Ask a follow-up question in the conversation of the last analysis",
    )
    parser.add_argument(
        "-t", "--task",
        choices=sorted(TASKS),
        default="summary",
        help="Kind of analysis (default: summary)",
    )
    parser.add_argument(
        "-q", "--question",
        help="Ask a specific question about the paper(s) instead of running a task",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Analyze all papers together in one request instead of one by one",
    )
    parser.add_argument(
        "--upload", action="store_true",
        help="Attach the file via the asset API instead of extracting text locally",
    )
    parser.add_argument(
        "--max-chars", type=int, default=400_000,
        help="Truncate each paper's text to this many characters (default: 400000)",
    )
    parser.add_argument("-o", "--output", help="Also write the result to this file")
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("ONEMIN_API_KEY"),
        help="1min.ai API key (falls back to ONEMIN_API_KEY env var)",
    )
    parser.add_argument(
        "-m", "--model",
        default=Models.Text.GEMINI_2_5_FLASH,
        help=f"Model to use (default: {Models.Text.GEMINI_2_5_FLASH})",
    )

    args = parser.parse_args()
    sys.stdout.reconfigure(errors="replace")  # model output may not fit the console codepage

    if not args.api_key:
        parser.error("API key is required. Set ONEMIN_API_KEY or use -k/--api-key.")
    if bool(args.follow_up) == bool(args.sources):
        parser.error("Pass paper sources, or -f/--follow-up QUESTION, but not both.")
    if args.compare and len(args.sources) < 2 and not args.follow_up:
        parser.error("--compare needs at least two papers.")

    instruction = args.question or (COMPARE if args.compare else TASKS[args.task])

    papers: list[tuple[str, str, list]] = []  # (name, text, attachments)
    for source in args.sources:
        name, data = _fetch(source)
        if args.upload:
            papers.append((name, "", [(name, data)]))
            continue
        text = _to_text(name, data)
        if len(text) > args.max_chars:
            print(
                f"warning: {name}: truncated from {len(text)} to "
                f"{args.max_chars} characters (raise --max-chars to send more)",
                file=sys.stderr,
            )
            text = text[: args.max_chars]
        papers.append((name, text, []))

    # Warn before spending credits on a request the model cannot hold.
    try:
        from models import fetch_models
        context = next(
            (m.get("creditMetadata") or {}).get("CONTEXT") or 0
            for m in fetch_models() if m["modelId"] == args.model
        )
        needed = max(len(text) for _, text, _ in papers) // 3  # ~3 chars/token, conservative
        if args.compare:
            needed = sum(len(text) for _, text, _ in papers) // 3
        if context and needed > context:
            print(
                f"warning: ~{needed:,} tokens of paper text but {args.model} "
                f"holds {context:,}; see 'python models.py --min-context {needed}'",
                file=sys.stderr,
            )
    except (StopIteration, httpx.HTTPError, ImportError):
        pass  # unknown model or catalogue unreachable: let the API decide

    # One request for everything with --compare, otherwise one per paper.
    batches = [papers] if args.compare else [[p] for p in papers]

    # Long papers take a while; never retry, a retried request is billed again.
    client = OneMinClient(api_key=args.api_key, timeout=300, max_retries=0)
    mode = "a" if args.follow_up else "w"
    out = open(args.output, mode, encoding="utf-8") if args.output else None

    def emit(chunks) -> None:
        for chunk in chunks:
            sys.stdout.write(chunk)
            sys.stdout.flush()
            if out:
                out.write(chunk)

    try:
        if args.follow_up:
            if not STATE.exists():
                parser.error("No previous analysis to follow up on; analyze a paper first.")
            conversation_id, model, *files = STATE.read_text(encoding="utf-8").split("\n")
            # Same model as the analysis unless -m is given explicitly.
            if "-m" not in sys.argv and "--model" not in sys.argv:
                args.model = model or args.model
            emit([f"**Q: {args.follow_up}**\n\n", *client.text.chat(
                args.follow_up, model=args.model, stream=True,
                # Uploaded files are not reliably kept in the history; attach them again.
                files=files or None, conversationId=conversation_id,
            ), "\n\n"])
            return
        for batch in batches:
            body = "\n\n".join(
                f"===== PAPER: {name} =====\n{text}" for name, text, _ in batch
            )
            files = [
                client.asset.upload(f).asset_id
                for _, _, attached in batch for f in attached
            ]
            prompt = f"{RULES}\n\n{instruction}\n\n{body}"
            header = "" if args.compare or len(papers) == 1 else f"# {batch[0][0]}\n\n"
            title = ", ".join(name for name, _, _ in batch)[:90]
            conversation_id = client.conversation.create(
                title=title, model=args.model,
            ).conversation_id
            emit([header, *client.text.chat(
                prompt, model=args.model, stream=True, files=files or None,
                conversationId=conversation_id,
            ), "\n\n"])
            STATE.write_text(
                "\n".join([conversation_id, args.model, *files]), encoding="utf-8",
            )
    except OneMinError as exc:
        sys.exit(f"error: {exc}\n(run 'python models.py' to list valid model ids)")
    finally:
        if out:
            out.close()


if __name__ == "__main__":
    main()
