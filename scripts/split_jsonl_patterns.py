#!/usr/bin/env python3
"""
Split a JSONL file into one JSON file per pattern.

Defaults to the compact corpus JSONL and writes to data/master_data/patterns_json.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict


DEFAULT_INPUT = "data/master_data/final_corpus_compact.jsonl"
DEFAULT_OUTPUT_DIR = "data/master_data/patterns_json"
DEFAULT_ID_FIELD = "id"


def _sanitize_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return cleaned or "pattern"


def _build_output_path(
    output_dir: Path, pattern_id: str | None, index: int, overwrite: bool
) -> Path:
    base = _sanitize_filename(pattern_id) if pattern_id else f"pattern_{index}"
    candidate = output_dir / f"{base}.json"
    if overwrite or not candidate.exists():
        return candidate
    return output_dir / f"{base}_{index}.json"


def _parse_json_line(line: str, line_number: int) -> Dict[str, Any]:
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split a JSONL file into one JSON file per pattern."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_INPUT,
        help=f"Input JSONL file (default: {DEFAULT_INPUT}).",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--id-field",
        default=DEFAULT_ID_FIELD,
        help=f"JSON field to use for filenames (default: {DEFAULT_ID_FIELD}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing files.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for output JSON (default: 2).",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for index, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        data = _parse_json_line(line, index)
        pattern_id = data.get(args.id_field)
        output_path = _build_output_path(output_dir, pattern_id, index, args.overwrite)
        output_path.write_text(
            json.dumps(data, indent=args.indent, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written += 1

    print(f"Wrote {written} pattern file(s) to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
