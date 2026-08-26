"""Generate the minimal real Pi/OMP experiment corpus."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures" / "pi-omp"
TASKS = ROOT / "pi-omp-tasks"
CLI = "${ai_stp}"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def passport(marker: str) -> dict:
    return {
        "name": "pi-omp-instruction",
        "description": "Deterministic Pi/OMP instruction experiment fixture.",
        "tags": ["experiment", "pi", "omp"],
        "harness_id": "pi",
        "component_type": "instruction",
        "projection_kind": "native_files",
        "license": {"spdx_id": "MIT", "redistribution_allowed": True},
        "managed_paths": ["AGENTS.md"],
        "native_ids": [marker],
        "entry_points": ["AGENTS.md"],
        "runtime_requirements": [],
        "provides_capabilities": [],
        "requires_capabilities": [],
        "requires_components": [],
        "requires_authorization": "none",
        "requires_credentials": False,
        "permissions": {"filesystem": [], "network": [], "process": []},
    }


def generate() -> None:
    marker = "PI_OMP_INSTRUCTION_OK"
    source = FIXTURES / "instruction" / "AGENTS.md"
    patch = FIXTURES / "instruction" / "passport-patch.json"
    write(source, f"# Pi OMP experiment\n\nActive marker: `{marker}`.\n")
    write(patch, json.dumps(passport(marker), indent=2) + "\n")
    provider = "${provider}"
    task = {
        "schema_version": 2,
        "harness_profile": "pi-omp",
        "id": "PI01",
        "fixtures": [
            {
                "source": "${experiments}/fixtures/pi-omp/instruction/AGENTS.md",
                "destination": "AGENTS.md",
            }
        ],
        "cleanup_requires": ["backup_ref"],
        "phases": {
            "prepare": [
                {
                    "id": "discover",
                    "argv": [
                        CLI,
                        "component",
                        "discover",
                        "--root",
                        "${user_home}",
                        "--json",
                    ],
                },
                {
                    "id": "adopt",
                    "argv": [
                        CLI,
                        "component",
                        "adopt",
                        "--path",
                        "${user_home}\\AGENTS.md",
                        "--root",
                        "${user_home}",
                        "--json",
                    ],
                    "capture": {
                        "component_id": "data.stable_id",
                        "component_revision": "data.revision_id",
                    },
                },
                {
                    "id": "developer",
                    "argv": [CLI, "passport", "developer", "init", "--json"],
                },
                {
                    "id": "device",
                    "argv": [CLI, "passport", "device", "refresh", "--json"],
                },
                {
                    "id": "project",
                    "argv": [
                        CLI,
                        "project",
                        "passport",
                        "--root",
                        "${project}",
                        "--json",
                    ],
                },
                {
                    "id": "update",
                    "argv": [
                        CLI,
                        "component",
                        "passport",
                        "update",
                        "--id",
                        "${component_id}",
                        "--expected-revision",
                        "${component_revision}",
                        "--from",
                        "${experiments}/fixtures/pi-omp/instruction/passport-patch.json",
                        "--confirm",
                        "--json",
                    ],
                },
                {
                    "id": "release",
                    "argv": [
                        CLI,
                        "component",
                        "version",
                        "release",
                        "--id",
                        "${component_id}",
                        "--json",
                    ],
                },
                {
                    "id": "propose",
                    "argv": [
                        CLI,
                        "select",
                        "propose",
                        "--harness",
                        "${harness_id}",
                        "--project",
                        "${project}",
                        "--member",
                        "${component_id}@1.0",
                        "--json",
                    ],
                    "capture": {"proposal_id": "data.proposals.0.proposal_id"},
                },
                {
                    "id": "confirm",
                    "argv": [
                        CLI,
                        "select",
                        "confirm",
                        "--proposal",
                        "${proposal_id}",
                        "--confirm",
                        "--json",
                    ],
                    "capture": {"setup_id": "data.stable_id"},
                },
            ],
            "install": [
                {
                    "id": "plan",
                    "argv": [
                        CLI,
                        "install",
                        "plan",
                        "--setup",
                        "${setup_id}@1.0",
                        "--project",
                        "${project}",
                        "--harness",
                        "${harness_id}",
                        "--provider",
                        provider,
                        "--unverified-provider",
                        "--protocol-version",
                        "3",
                        "--target",
                        "${target}",
                        "--json",
                    ],
                    "capture": {
                        "operation_id": "data.operation_id",
                        "plan_digest": "data.plan_digest",
                    },
                },
                {
                    "id": "approve",
                    "argv": [
                        CLI,
                        "install",
                        "approve",
                        "--operation",
                        "${operation_id}",
                        "--plan-digest",
                        "${plan_digest}",
                        "--json",
                    ],
                },
                {
                    "id": "apply",
                    "argv": [
                        CLI,
                        "install",
                        "apply",
                        "--operation",
                        "${operation_id}",
                        "--provider",
                        provider,
                        "--json",
                    ],
                    "capture": {"backup_ref": "data.backup_ref"},
                    "expect_json": {"ok": True, "data.state": "verified"},
                },
            ],
            "verify": [
                {
                    "id": "observer",
                    "argv": [
                        "${python}",
                        "${delegate}",
                        "--harness",
                        "${harness_id}",
                        "--backend",
                        "${delegate_backend}",
                        "--runtime",
                        "${runtime}",
                        "--target",
                        "${target}",
                        "--cwd",
                        "${project}",
                        "--timeout",
                        "3m",
                        "--no-tools",
                        "--output-dir",
                        "${run_root}\\observer",
                        "--task",
                        f"Reply with exactly {marker} if your active instructions contain {marker}; otherwise reply MISSING.",
                    ],
                    "expect_json_contains": {"response": marker},
                },
            ],
            "cleanup": [
                {
                    "id": "rollback-plan",
                    "argv": [
                        CLI,
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
                        provider,
                        "--unverified-provider",
                        "--protocol-version",
                        "3",
                        "--target",
                        "${target}",
                        "--json",
                    ],
                    "capture": {
                        "rollback_operation": "data.operation_id",
                        "rollback_digest": "data.plan_digest",
                    },
                },
                {
                    "id": "rollback-approve",
                    "argv": [
                        CLI,
                        "install",
                        "approve",
                        "--operation",
                        "${rollback_operation}",
                        "--plan-digest",
                        "${rollback_digest}",
                        "--json",
                    ],
                },
                {
                    "id": "rollback-apply",
                    "argv": [
                        CLI,
                        "install",
                        "apply",
                        "--operation",
                        "${rollback_operation}",
                        "--provider",
                        provider,
                        "--json",
                    ],
                    "expect_json": {"ok": True, "data.state": "verified"},
                },
            ],
        },
    }
    TASKS.mkdir(parents=True, exist_ok=True)
    (TASKS / "PI01.yaml").write_text(
        yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


if __name__ == "__main__":
    generate()
