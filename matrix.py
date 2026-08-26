"""Validate manifests and generate OS × harness experiment matrices."""

from __future__ import annotations

import argparse
import json
import platform
from itertools import product
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
EXPERIMENTS = ROOT / "experiments"
CATEGORIES = {
    "instructions": "instruction",
    "skills": "skill",
    "mcps": "mcp",
    "hooks": "hook",
    "commands": "command",
    "agents": "agent",
    "plugins": "plugin",
    "settings": "setting",
    "setups": "setup",
}
OPERATING_SYSTEMS = ("windows", "macos", "linux")


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected mapping")
    return value


def cases(
    categories: list[str] | None = None, ids: set[str] | None = None
) -> list[dict]:
    rows = []
    for category in categories or list(CATEGORIES):
        root = EXPERIMENTS / category
        if not root.is_dir():
            continue
        for directory in sorted(root.iterdir()):
            manifest = directory / "experiment.yaml"
            if (
                directory.is_dir()
                and manifest.is_file()
                and (not ids or directory.name in ids)
            ):
                document = load(manifest)
                rows.append(
                    {
                        "id": directory.name,
                        "category": category,
                        "component_type": document.get("component_type"),
                        "path": directory.relative_to(ROOT).as_posix(),
                        "fixtures": document.get("fixtures", []),
                        "harnesses": document.get("harnesses", []),
                    }
                )
    return rows


def _portable(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {
            ".json",
            ".md",
            ".yaml",
            ".yml",
            ".py",
        }:
            text = path.read_text(encoding="utf-8")
            if "C:\\Users" in text or "C:/Users" in text:
                raise ValueError(f"{path}: machine-specific path")


def validate() -> list[dict]:
    rows = cases()
    present = {row["category"] for row in rows}
    if present != set(CATEGORIES):
        raise ValueError(
            f"category mismatch: missing={sorted(set(CATEGORIES) - present)}"
        )
    profiles = set(load(ROOT / "harnesses.yaml"))
    for row in rows:
        root = ROOT / row["path"]
        manifest = load(root / "experiment.yaml")
        if manifest.get("schema_version") != 1 or manifest.get("id") != row["id"]:
            raise ValueError(f"{row['id']}: invalid experiment manifest")
        if manifest.get("component_type") != CATEGORIES[row["category"]]:
            raise ValueError(f"{row['id']}: component type/category mismatch")
        if not row["fixtures"] or len(row["fixtures"]) != len(set(row["fixtures"])):
            raise ValueError(f"{row['id']}: fixtures must be a unique non-empty list")
        if not set(row["harnesses"]) <= profiles:
            raise ValueError(f"{row['id']}: unknown harness profile")
        object_counts: dict[str, int] = {}
        for fixture_id in row["fixtures"]:
            fixture = root / "fixtures" / fixture_id
            state = load(fixture / "fixture.yaml")
            patch = json.loads(
                (fixture / "passport-patch.json").read_text(encoding="utf-8")
            )
            states = state.get("states", {})
            if state.get("schema_version") != 1 or set(states) != {
                "baseline",
                "installed",
                "restored",
            }:
                raise ValueError(f"{row['id']}/{fixture_id}: invalid states")
            if states["restored"] != {"same_as": "baseline"}:
                raise ValueError(
                    f"{row['id']}/{fixture_id}: restored must equal baseline"
                )
            if not (fixture / "payload" / "common").is_dir():
                raise ValueError(f"{row['id']}/{fixture_id}: common payload missing")
            component_type = patch.get("component_type")
            object_counts[component_type] = object_counts.get(component_type, 0) + len(
                state.get("objects", [])
            )
        if row["category"] == "setups":
            for component_type, minimum in manifest.get("minimum_objects", {}).items():
                if object_counts.get(component_type, 0) < minimum:
                    raise ValueError(
                        f"{row['id']}: fewer than {minimum} {component_type} objects"
                    )
        _portable(root)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("validate", "generate"), nargs="?", default="validate"
    )
    parser.add_argument("--category", action="append", choices=tuple(CATEGORIES))
    parser.add_argument("--id", action="append", dest="ids")
    parser.add_argument("--harness", action="append")
    parser.add_argument(
        "--os", action="append", choices=OPERATING_SYSTEMS, dest="operating_systems"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "_generated/matrix.yaml")
    args = parser.parse_args()
    rows = validate()
    selected = [
        row
        for row in rows
        if (not args.category or row["category"] in args.category)
        and (not args.ids or row["id"] in set(args.ids))
    ]
    harnesses = args.harness or list(load(ROOT / "harnesses.yaml"))
    systems = args.operating_systems or [
        platform.system().lower().replace("darwin", "macos")
    ]
    matrix = [
        {**row, "harness_profile": harness, "os": system}
        for row, harness, system in product(selected, harnesses, systems)
        if harness in row["harnesses"]
    ]
    if args.command == "generate":
        if not matrix:
            raise SystemExit("no compatible experiments selected")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            yaml.safe_dump(
                {"schema_version": 1, "experiments": matrix}, sort_keys=False
            ),
            encoding="utf-8",
        )
        print(args.output)
    else:
        print(f"validated: {len(rows)} experiments in 9 categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
