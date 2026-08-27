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
OBSERVER_PROMPT = ROOT / "prompts" / "observe-state.md"
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
EXPECTED_COUNTS = {
    "instructions": 5,
    "skills": 25,
    "mcps": 16,
    "hooks": 10,
    "commands": 5,
    "agents": 5,
    "plugins": 5,
    "settings": 5,
    "setups": 5,
}


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected mapping")
    return value


def observation_prompt(
    experiment_id: str, harness: str, phase: str, probe: str | None = None
) -> str:
    if phase not in {"baseline", "installed", "restored"}:
        raise ValueError(f"unknown observation phase: {phase}")
    state_file = f"state/{experiment_id}-{harness}-{phase}.yaml"
    return OBSERVER_PROMPT.read_text(encoding="utf-8").format(
        experiment_id=experiment_id,
        harness=harness,
        phase=phase,
        state_file=state_file,
        probe_instruction=(
            f"Perform this exact read-only probe after inventory: {probe}"
            if phase == "installed" and probe
            else "Do not invoke components during this phase."
        ),
    )


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
                        "variants": document.get("variants", []),
                    "observation": document.get("observe", {}),
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
    counts = {
        category: sum(row["category"] == category for row in rows)
        for category in CATEGORIES
    }
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"experiment count mismatch: {counts}")
    profiles = set(load(ROOT / "harnesses.yaml"))
    if not OBSERVER_PROMPT.is_file():
        raise ValueError("observer prompt missing")
    for row in rows:
        root = ROOT / row["path"]
        manifest = load(root / "experiment.yaml")
        if manifest.get("schema_version") != 1 or manifest.get("id") != row["id"]:
            raise ValueError(f"{row['id']}: invalid experiment manifest")
        if manifest.get("component_type") != CATEGORIES[row["category"]]:
            raise ValueError(f"{row['id']}: component type/category mismatch")
        if not row["fixtures"] or len(row["fixtures"]) != len(set(row["fixtures"])):
            raise ValueError(f"{row['id']}: fixtures must be a unique non-empty list")
        if not set(row["variants"]) <= profiles:
            raise ValueError(f"{row['id']}: unknown harness profile")
        if not isinstance(row["observation"], dict) or not row["observation"].get(
            "expect"
        ):
            raise ValueError(f"{row['id']}: expected observation missing")
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
            variants = state.get("variants", {})
            if set(variants) != set(row["variants"]):
                raise ValueError(f"{row['id']}/{fixture_id}: variant mismatch")
            for profile, variant in variants.items():
                payload = fixture / variant.get("payload", "")
                if not payload.is_dir():
                    raise ValueError(
                        f"{row['id']}/{fixture_id}: {profile} payload missing"
                    )
                source_subpath = variant.get("source_subpath")
                authoring_path = variant.get("authoring_path")
                if bool(source_subpath) != bool(authoring_path):
                    raise ValueError(
                        f"{row['id']}/{fixture_id}: source mapping must be paired"
                    )
                if source_subpath and not (payload / source_subpath).exists():
                    raise ValueError(
                        f"{row['id']}/{fixture_id}: source subpath missing"
                    )
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
        {
            **row,
            "harness_profile": harness,
            "os": system,
            "variant_available": harness in row["variants"],
            "expected": "runnable" if harness in row["variants"] else "unsupported",
            "observer_prompts": {
                phase: observation_prompt(
                    row["id"], harness, phase, row["observation"].get("probe")
                )
                for phase in ("baseline", "installed", "restored")
            },
        }
        for row, harness, system in product(selected, harnesses, systems)
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
        print("validated: 81 logical experiments in 9 categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
