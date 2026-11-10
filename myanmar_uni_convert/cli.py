"""Command-line interface for myanmar-uni-convert."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .api import convert, convert_with_stats


def _read(path: str | None) -> str:
    if not path or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _write(path: str | None, text: str) -> None:
    if not path or path == "-":
        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="myanmar-uni-convert",
        description="Convert legacy Myanmar encodings / Zawgyi text to Unicode.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input file (default: stdin)")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    p.add_argument("--font", default="", help="Font name hint, e.g. WinInnwa")
    p.add_argument("--kind", default="", help="Kind hint: win, academy, ce, zawgyi, …")
    p.add_argument("--no-auto", action="store_true", help="Disable Zawgyi auto-detect")
    p.add_argument("--no-cleanup", action="store_true", help="Skip light post cleanup")
    p.add_argument("--stats", action="store_true", help="Print JSON stats to stderr")
    p.add_argument(
        "--zawgyi-min",
        type=float,
        default=0.5,
        help="Zawgyi detector threshold (default: 0.5)",
    )
    args = p.parse_args(argv)

    text = _read(args.input)
    result = convert_with_stats(
        text,
        font=args.font or None,
        kind=args.kind or None,
        auto=not args.no_auto,
        zawgyi_min=args.zawgyi_min,
        cleanup=not args.no_cleanup,
    )
    _write(args.output, result.text)
    if args.stats:
        payload = {
            "kind": result.kind,
            "branch": result.branch,
            "zawgyi_score": result.zawgyi_score,
            "stats": result.stats,
        }
        sys.stderr.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return 0


# Keep convert import used for type checkers / re-exports
_ = convert

if __name__ == "__main__":
    raise SystemExit(main())
