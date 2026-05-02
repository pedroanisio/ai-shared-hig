#!/usr/bin/env python3
"""
Repair common UTF-8 mojibake caused by decoding UTF-8 bytes as CP1252/Latin-1.

This script scans text and converts byte-sequences that look like UTF-8 into
their intended Unicode characters while leaving valid Unicode intact.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Tuple


DEFAULT_PATH = "data/master_data/final_corpus_compact.jsonl"


def _to_cp1252_byte(ch: str) -> int | None:
    try:
        return ch.encode("cp1252")[0]
    except UnicodeEncodeError:
        code = ord(ch)
        if 0x80 <= code <= 0xFF:
            return code
        return None


def _fix_mojibake(text: str) -> str:
    out = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        byte = _to_cp1252_byte(ch)
        if byte is None:
            out.append(ch)
            i += 1
            continue

        if 0xC2 <= byte <= 0xDF:
            need = 2
        elif 0xE0 <= byte <= 0xEF:
            need = 3
        elif 0xF0 <= byte <= 0xF4:
            need = 4
        else:
            out.append(ch)
            i += 1
            continue

        if i + need - 1 >= length:
            out.append(ch)
            i += 1
            continue

        bytes_seq = bytearray([byte])
        ok = True
        for j in range(1, need):
            bval = _to_cp1252_byte(text[i + j])
            if bval is None or bval < 0x80 or bval > 0xBF:
                ok = False
                break
            bytes_seq.append(bval)

        if ok:
            try:
                decoded = bytes(bytes_seq).decode("utf-8")
            except UnicodeDecodeError:
                ok = False

        if ok:
            out.append(decoded)
            i += need
        else:
            out.append(ch)
            i += 1

    return "".join(out)


def repair_text(text: str) -> Tuple[str, int]:
    lines = text.splitlines(keepends=True)
    changed_lines = 0
    fixed_lines = []
    for line in lines:
        fixed = _fix_mojibake(line)
        if fixed != line:
            changed_lines += 1
        fixed_lines.append(fixed)
    return "".join(fixed_lines), changed_lines


def _iter_paths(paths: Iterable[str]) -> Iterable[Path]:
    for path in paths:
        yield Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair common UTF-8 mojibake in text files."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[DEFAULT_PATH],
        help=f"File paths to repair (default: {DEFAULT_PATH}).",
    )
    parser.add_argument(
        "--output",
        help="Write output to this file (only valid with a single input path).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files.",
    )
    args = parser.parse_args()

    if args.output and len(args.paths) != 1:
        parser.error("--output requires exactly one input path.")

    for path in _iter_paths(args.paths):
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        text = path.read_text(encoding="utf-8")
        fixed, changed_lines = repair_text(text)

        if args.dry_run:
            print(f"{path}: {changed_lines} line(s) would change")
            continue

        if args.output:
            out_path = Path(args.output)
            out_path.write_text(fixed, encoding="utf-8")
            print(f"{path} -> {out_path} ({changed_lines} line(s) changed)")
        else:
            if fixed != text:
                path.write_text(fixed, encoding="utf-8")
            print(f"{path}: {changed_lines} line(s) changed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
