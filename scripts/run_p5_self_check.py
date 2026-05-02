#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_P5_PATH = Path(__file__).resolve().parents[1] / "data/master_data/patterns_json/P5.json"


def load_self_check(p5_path: Path):
    with p5_path.open("r", encoding="utf-8") as handle:
        p5 = json.load(handle)
    self_check = p5.get("self_check")
    if not self_check:
        raise ValueError("missing self_check in P5.json")
    if self_check.get("lang") != "javascript":
        raise ValueError(f"unsupported self_check lang: {self_check.get('lang')}")
    code = self_check.get("code")
    entry = self_check.get("entry")
    if not code or not entry:
        raise ValueError("self_check must include code and entry")
    return code, entry


def run_js(code: str, entry: str, p5_path: Path) -> int:
    p5_path_js = json.dumps(str(p5_path))
    wrapper = (
        "const fs = require('fs');\n"
        f"const p5 = JSON.parse(fs.readFileSync({p5_path_js}, 'utf8'));\n"
        f"{code}\n"
        f"if (typeof {entry} !== 'function') {{ throw new Error('entry function not found: {entry}'); }}\n"
        f"{entry}(p5);\n"
        "console.log('ok');\n"
    )
    try:
        result = subprocess.run(
            ["node", "-e", wrapper],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("node is not installed or not on PATH", file=sys.stderr)
        return 2

    if result.returncode != 0:
        sys.stderr.write(result.stderr or "self_check failed\n")
        return result.returncode
    print(result.stdout.strip())
    return 0


def main() -> int:
    p5_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_P5_PATH
    code, entry = load_self_check(p5_path)
    return run_js(code, entry, p5_path)


if __name__ == "__main__":
    raise SystemExit(main())
