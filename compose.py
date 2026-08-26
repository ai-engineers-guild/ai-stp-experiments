"""Compose one manifested experiment into a runnable schema-v2 task."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import materialize
import matrix


def step(step_id: str, *argv: str, **extra: object) -> dict:
    return {"id": step_id, "argv": list(argv), **extra}


def compose(experiment: Path, profile: str, output: Path) -> dict:
    manifest = matrix.load(experiment / "experiment.yaml")
    if profile not in manifest["variants"]:
        raise ValueError(f"{manifest['id']} has no {profile} provider variant")
    generated = output.parent / f"{output.stem}-fixtures"
    if generated.exists() or output.exists():
        raise FileExistsError(output)

    prepare = [step("doctor", "${ai_stp}", "doctor", "--json")]
    component_ids = []
    expected_paths = []
    for index, fixture_id in enumerate(manifest["fixtures"], 1):
        source = experiment / "fixtures" / fixture_id
        target = (generated / fixture_id).resolve()
        materialize.materialize(source, profile, target)
        passport = matrix.load(source / "fixture.yaml")
        variant = passport["variants"][profile]
        managed = variant["managed_paths"]
        component_id = f"component_id_{index}"
        revision = f"component_revision_{index}"
        candidate = f"candidate_path_{index}"
        component_ids.append(component_id)
        prepare += [
            step(
                f"discover-{index}",
                "${ai_stp}",
                "component",
                "discover",
                "--root",
                str(target),
                "--json",
                capture={candidate: "data.components.0.source_path"},
            ),
            step(
                f"adopt-{index}",
                "${ai_stp}",
                "component",
                "adopt",
                "--path",
                "${" + candidate + "}",
                "--root",
                str(target),
                "--json",
                capture={component_id: "data.stable_id", revision: "data.revision_id"},
            ),
            step(
                f"update-{index}",
                "${ai_stp}",
                "component",
                "passport",
                "update",
                "--id",
                "${" + component_id + "}",
                "--expected-revision",
                "${" + revision + "}",
                "--from",
                str(target / "passport-patch.json"),
                "--confirm",
                "--json",
            ),
            step(
                f"release-{index}",
                "${ai_stp}",
                "component",
                "version",
                "release",
                "--id",
                "${" + component_id + "}",
                "--json",
            ),
        ]
        expected_paths += [
            {"path": "${target}/" + path, "exists": True} for path in managed
        ]

    prepare[1:1] = [
        step("developer", "${ai_stp}", "passport", "developer", "init", "--json"),
        step("device", "${ai_stp}", "passport", "device", "refresh", "--json"),
        step(
            "project",
            "${ai_stp}",
            "project",
            "passport",
            "--root",
            "${project}",
            "--json",
        ),
    ]
    propose = [
        "${ai_stp}",
        "select",
        "propose",
        "--harness",
        "${harness_id}",
        "--project",
        "${project}",
    ]
    for component_id in component_ids:
        propose += ["--member", "${" + component_id + "}@1.0"]
    propose += ["--json"]
    prepare += [
        step(
            "propose", *propose, capture={"proposal_id": "data.proposals.0.proposal_id"}
        ),
        step(
            "confirm",
            "${ai_stp}",
            "select",
            "confirm",
            "--proposal",
            "${proposal_id}",
            "--confirm",
            "--json",
            capture={"setup_id": "data.stable_id"},
        ),
    ]
    install = [
        step(
            "plan",
            "${ai_stp}",
            "install",
            "plan",
            "--setup",
            "${setup_id}@1.0",
            "--project",
            "${project}",
            "--harness",
            "${harness_id}",
            "--provider",
            "${provider}",
            "--unverified-provider",
            "--protocol-version",
            "3",
            "--target",
            "${target}",
            "--json",
            capture={
                "operation_id": "data.operation_id",
                "plan_digest": "data.plan_digest",
            },
        ),
        step(
            "approve",
            "${ai_stp}",
            "install",
            "approve",
            "--operation",
            "${operation_id}",
            "--plan-digest",
            "${plan_digest}",
            "--json",
        ),
        step(
            "apply",
            "${ai_stp}",
            "install",
            "apply",
            "--operation",
            "${operation_id}",
            "--provider",
            "${provider}",
            "--json",
            capture={"backup_ref": "data.backup_ref"},
            expect_json={"ok": True, "data.state": "verified"},
        ),
    ]
    marker = manifest.get("observe", {}).get("expect", {}).get("marker", manifest["id"])
    prompt = (
        manifest.get("observe", {}).get("prompt")
        or f"Reply with exactly {marker} if you can observe it; otherwise reply MISSING. Do not edit files."
    )
    verify = [
        step(
            "observer",
            "${python}",
            "${delegate}",
            "--harness",
            "${harness_id}",
            "--backend",
            "${delegate_backend}",
            "--cwd",
            "${project}",
            "--target",
            "${target}",
            "--timeout",
            "3m",
            "--output-dir",
            "${run_root}/observer",
            "--task",
            prompt,
            expect_json_contains={"response": marker},
        )
    ]
    cleanup = [
        step(
            "rollback-plan",
            "${ai_stp}",
            "install",
            "plan",
            "--action",
            "rollback",
            "--backup-ref",
            "${backup_ref}",
            "--project",
            "${project}",
            "--harness",
            "${harness_id}",
            "--provider",
            "${provider}",
            "--unverified-provider",
            "--protocol-version",
            "3",
            "--target",
            "${target}",
            "--json",
            capture={
                "rollback_operation": "data.operation_id",
                "rollback_digest": "data.plan_digest",
            },
        ),
        step(
            "rollback-approve",
            "${ai_stp}",
            "install",
            "approve",
            "--operation",
            "${rollback_operation}",
            "--plan-digest",
            "${rollback_digest}",
            "--json",
        ),
        step(
            "rollback-apply",
            "${ai_stp}",
            "install",
            "apply",
            "--operation",
            "${rollback_operation}",
            "--provider",
            "${provider}",
            "--json",
            expect_json={"ok": True, "data.state": "verified"},
        ),
    ]
    task = {
        "schema_version": 2,
        "id": manifest["id"],
        "harness_profile": profile,
        "cleanup_requires": ["backup_ref"],
        "observer_failure_verdict": "blocked",
        "phases": {
            "prepare": prepare,
            "install": install,
            "verify": verify,
            "cleanup": cleanup,
        },
        "expect_paths": expected_paths,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return task


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--harness", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    compose(args.experiment, args.harness, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
