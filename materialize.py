"""Materialize one portable fixture plus an optional harness-native overlay."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        result[key] = (
            merge(result[key], value)
            if isinstance(value, dict) and isinstance(result.get(key), dict)
            else value
        )
    return result


def materialize(fixture: Path, harness: str, output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    common = fixture / "payload" / "common"
    shutil.copytree(common, output)
    overlay = fixture / "payload" / "harnesses" / harness
    if overlay.is_dir():
        shutil.copytree(overlay, output, dirs_exist_ok=True)
    passport = json.loads((fixture / "passport-patch.json").read_text(encoding="utf-8"))
    override = fixture / "passport-overrides" / f"{harness}.json"
    if override.is_file():
        passport = merge(passport, json.loads(override.read_text(encoding="utf-8")))
    (output / "passport-patch.json").write_text(
        json.dumps(passport, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--harness", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    materialize(args.fixture, args.harness, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
