"""Check whether this machine can run experiment profiles."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path

import yaml

import run_experiment


def available(value: str) -> bool:
    path = Path(value).expanduser()
    return (
        path.is_file() if path.parent != Path(".") else shutil.which(value) is not None
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", action="append")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    names = list(yaml.safe_load(run_experiment.PROFILES.read_text(encoding="utf-8")))
    names = args.profile or names
    root = Path.cwd().resolve()
    base = {
        "project": str(root),
        "user_home": str(Path.home()),
        "run_root": str(root / "_doctor"),
        "experiments": str(run_experiment.PROFILES.parent),
        "workspace_root": str(run_experiment.PROFILES.parent.parent),
        "skills_root": os.environ.get(
            "AI_STP_SKILLS_ROOT",
            str(run_experiment.PROFILES.parent.parent / "my_skills"),
        ),
        "python": sys.executable,
        "ai_stp": os.environ.get("AI_STP_BIN") or shutil.which("ai-stp") or "ai-stp",
    }
    rows = []
    for name in names:
        variables = dict(base)
        try:
            _, profile = run_experiment.load_profile({}, variables, name)
            checks = {
                "ai_stp": available(variables["ai_stp"]),
                "harness_cli": available(variables["cli"]),
                "delegate": available(variables["delegate"]),
                "delegate_backend": available(variables["delegate_backend"]),
                "provider": available(variables["provider"]),
            }
            rows.append(
                {"profile": name, "ready": all(checks.values()), "checks": checks}
            )
        except (KeyError, TypeError, ValueError) as exc:
            rows.append({"profile": name, "ready": False, "error": str(exc)})
    report = {
        "schema_version": 1,
        "os": platform.system().lower(),
        "python": platform.python_version(),
        "profiles": rows,
    }
    print(
        json.dumps(report, indent=2)
        if args.json
        else yaml.safe_dump(report, sort_keys=False)
    )
    return int(any(not row["ready"] for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
