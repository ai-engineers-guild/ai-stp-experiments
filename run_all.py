"""Run every canonical Antigravity experiment in a fresh disposable home."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
IDS = ["E00", "E01", "E02", "E03", *[f"E{i:02d}" for i in range(10, 63)]]


def tasks() -> list[tuple[str, Path]]:
    return [
        (
            experiment_id,
            ROOT / f"20260825T160000_antigravity_{experiment_id}" / "task.yaml",
        )
        for experiment_id in IDS
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=ROOT / "runs")
    parser.add_argument("--ids", nargs="*", choices=IDS, default=IDS)
    parser.add_argument("--harness-profile", default="antigravity")
    parser.add_argument("--skip-doctor", action="store_true")
    args = parser.parse_args()
    if not args.skip_doctor:
        ready = subprocess.run(
            [
                sys.executable,
                str(ROOT / "doctor.py"),
                "--profile",
                args.harness_profile,
            ],
            check=False,
        )
        if ready.returncode:
            return ready.returncode
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    summary = {"schema_version": 1, "run_id": stamp, "experiments": []}
    wanted = set(args.ids)
    for experiment_id, task in tasks():
        if experiment_id not in wanted:
            continue
        destination = args.run_root.resolve() / stamp / experiment_id
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_experiment.py"),
                str(task),
                "--run-root",
                str(destination),
                "--harness-profile",
                args.harness_profile,
            ],
            check=False,
        )
        result = yaml.safe_load(
            (destination / "results.yaml").read_text(encoding="utf-8")
        )
        summary["experiments"].append(
            {
                "id": experiment_id,
                "verdict": result["verdict"],
                "exit": completed.returncode,
            }
        )
    summary_path = args.run_root.resolve() / stamp / "summary.yaml"
    summary_path.write_text(yaml.safe_dump(summary, sort_keys=False), encoding="utf-8")
    print(summary_path)
    return int(
        any(
            item["verdict"] in {"fail", "inconclusive"}
            for item in summary["experiments"]
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
