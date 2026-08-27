"""Materialize one portable fixture plus an optional harness-native overlay."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml


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
    manifest = fixture / "fixture.yaml"
    state = yaml.safe_load(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    variants = state.get("variants", {})
    if variants and harness not in variants:
        raise ValueError(f"fixture has no {harness} variant")
    variant = variants.get(harness, {"payload": f"payload/harnesses/{harness}"})
    common = fixture / "payload" / "common"
    overlay = fixture / variant["payload"]
    if not common.is_dir() and not overlay.is_dir():
        raise ValueError(f"fixture has no {harness} variant")
    if common.is_dir():
        shutil.copytree(common, output)
    else:
        output.mkdir(parents=True)
    if overlay.is_dir():
        shutil.copytree(overlay, output, dirs_exist_ok=True)
    for relative in variant.get("exclude", []):
        path = output / relative
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    source_subpath = variant.get("source_subpath")
    authoring_path = variant.get("authoring_path")
    base_passport = json.loads(
        (fixture / "passport-patch.json").read_text(encoding="utf-8")
    )
    if not source_subpath and base_passport.get("component_type") == "skill":
        skill_files = list(output.rglob("SKILL.md"))
        if len(skill_files) != 1:
            raise ValueError("skill fixture must contain exactly one SKILL.md")
        source_subpath = skill_files[0].parent.relative_to(output).as_posix()
        authoring_path = f"skills/{base_passport['name']}"
    if source_subpath and authoring_path and source_subpath != authoring_path:
        native_source = output / source_subpath
        authoring_source = output / authoring_path
        authoring_source.parent.mkdir(parents=True, exist_ok=True)
        if native_source == output:
            authoring_source.mkdir()
            for item in tuple(output.iterdir()):
                if item != authoring_source.parent:
                    item.rename(authoring_source / item.name)
        else:
            native_source.rename(authoring_source)
            directory = native_source.parent
            while directory != output:
                directory.rmdir()
                directory = directory.parent
    passport = base_passport
    override = fixture / "passport-overrides" / f"{harness}.json"
    if override.is_file():
        passport = merge(passport, json.loads(override.read_text(encoding="utf-8")))
    if passport.get("component_type") == "skill":
        passport["entry_points"] = ["SKILL.md"]
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
