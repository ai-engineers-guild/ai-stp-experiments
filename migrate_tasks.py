"""One-shot migration of the legacy Antigravity task corpus to schema v2."""

from pathlib import Path

import yaml

ROOT = Path(__file__).parent
AI_STP = "${ai_stp}"
PROVIDER = "${provider}"
DELEGATE = "${delegate}"
FIXTURE = ROOT / "fixtures" / "skill-smoke"
COMPONENT_FIXTURES = {
    "E32": (
        "mcp-local",
        r"config\mcp_config.json",
        r".gemini\config\mcp_config.json",
        "mcp",
        "native_files",
        r"config\mcp_config.json",
        "playwright",
    ),
    "E46": (
        "hook-local",
        r"config\hooks.json",
        r".gemini\config\hooks.json",
        "hook",
        "native_files",
        r"config\hooks.json",
        "AI_STP_HOOK_MARKER",
    ),
    "E47": (
        "setting-local",
        r"antigravity-cli\settings.json",
        r".gemini\antigravity-cli\settings.json",
        "setting",
        "native_files",
        r"antigravity-cli\settings.json",
        "telemetry",
    ),
    "E48": (
        "plugin-local",
        r"antigravity-cli\plugins\experiment-plugin",
        r".gemini\antigravity-cli\plugins\experiment-plugin",
        "plugin",
        "plugin",
        r"antigravity-cli\plugins\experiment-plugin\AI_STP_PLUGIN_MARKER.txt",
        "AI_STP_PLUGIN_MARKER",
    ),
    "E49": (
        "agent-local",
        r"config\agents\experiment-reviewer.md",
        r".gemini\config\agents\experiment-reviewer.md",
        "agent",
        "native_files",
        r"config\agents\experiment-reviewer.md",
        "experiment-reviewer",
    ),
}
IDS = ["E00", "E01", "E02", "E03", *[f"E{i:02d}" for i in range(10, 63)]]
BLOCKER_REASONS = {
    "E00": "baseline capture requires the explicitly retained live snapshot",
    "E01": "bare-home transition is covered by each disposable component run",
    "E02": "canonical ai-stp skill lifecycle is separate from setup components",
    "E03": "canonical ai-stp skill removal requires a preceding canonical install",
    "E30": "the named private skill fixture is unavailable",
    "E31": "the named private skill fixture is unavailable",
    "E50": "Antigravity provider does not declare the command component kind",
    "E51": "Antigravity provider does not declare the instruction component kind",
    "E52": "the original skills need distinct released component fixtures",
    "E53": "the original twenty skills need distinct released component fixtures",
    "E54": "the fourteen named MCP servers require network or credential policy",
    "E55": "Antigravity 1.1.21 headless does not load the documented hook fixture",
    "E56": "ai-stp has no explicit empty-setup authoring command",
    "E57": "the retained live snapshot contains credentials and is unsafe to inspect",
    "E58": "missing-provider refusal is an expected negative experiment",
    "E59": "target status requires a preceding installation in the same run",
    "E60": "rollback requires a BackupRef produced in the same installation run",
    "E61": "external source resolution requires an exact network-resolved commit",
    "E62": "live restore is disabled until a credential-free baseline exists",
}


def portable_prompt(legacy: dict) -> str:
    return (
        str(legacy.get("prompt", ""))
        .strip()
        .replace(r"C:\Users\User\a_projects", "${workspace_root}")
    )


def old_task(experiment_id: str) -> dict:
    paths = sorted(ROOT.glob(f"20260825T160000_antigravity_{experiment_id}/task.yaml"))
    if paths:
        return yaml.safe_load(paths[0].read_text(encoding="utf-8"))
    # E01 had an accidental combined directory in the legacy corpus.
    combined = ROOT / "20260825T160000_antigravity_E01,E19" / "task.yaml"
    data = yaml.safe_load(combined.read_text(encoding="utf-8"))
    return data


def observer(
    prompt: str,
    expect_success: bool,
    expected_response: str | None = "AI_STP_EXPERIMENT_SMOKE",
    *,
    always_approve: bool = False,
) -> dict:
    step = {
        "id": "observer",
        "argv": [
            "${python}",
            DELEGATE,
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
            "${run_root}\\observer",
            "--task",
            prompt,
        ],
        "expect_exit": 0 if expect_success else 65,
    }
    if always_approve:
        step["argv"].insert(-2, "--always-approve")
    if expect_success:
        step["expect_json"] = {"exit_code": 0, "raw.status": "SUCCESS"}
        if expected_response:
            step["expect_json_contains"] = {"response": expected_response}
    return step


def skill_task(legacy: dict) -> dict:
    prompt = portable_prompt(legacy)
    return {
        "schema_version": 2,
        "id": legacy["id"],
        "title": legacy.get("title", ""),
        "prompt": prompt,
        "expect": str(legacy.get("expect", "")).strip(),
        "fixtures": [
            {
                "source": "${experiments}/fixtures/skill-smoke",
                "destination": ".agents/skills/experiment-smoke",
            }
        ],
        "phases": {
            "prepare": [
                {"id": "doctor", "argv": [AI_STP, "doctor", "--json"]},
                {"id": "discover", "argv": [AI_STP, "component", "discover", "--json"]},
                {
                    "id": "adopt",
                    "argv": [
                        AI_STP,
                        "component",
                        "adopt",
                        "--path",
                        "${user_home}/.agents/skills/experiment-smoke",
                        "--json",
                    ],
                    "capture": {
                        "component_id": "data.stable_id",
                        "component_revision": "data.revision_id",
                    },
                },
                {
                    "id": "developer",
                    "argv": [AI_STP, "passport", "developer", "init", "--json"],
                },
                {
                    "id": "device",
                    "argv": [AI_STP, "passport", "device", "refresh", "--json"],
                },
                {
                    "id": "project",
                    "argv": [
                        AI_STP,
                        "project",
                        "passport",
                        "--root",
                        "${project}",
                        "--json",
                    ],
                },
                {
                    "id": "suggest",
                    "argv": [
                        AI_STP,
                        "component",
                        "passport",
                        "suggest",
                        "--id",
                        "${component_id}",
                        "--json",
                    ],
                },
                {
                    "id": "update",
                    "argv": [
                        AI_STP,
                        "component",
                        "passport",
                        "update",
                        "--id",
                        "${component_id}",
                        "--expected-revision",
                        "${component_revision}",
                        "--from",
                        "${experiments}/fixtures/skill-smoke/passport-patch.json",
                        "--confirm",
                        "--json",
                    ],
                    "capture": {"component_revision": "data.revision_id"},
                },
                {
                    "id": "release",
                    "argv": [
                        AI_STP,
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
                        AI_STP,
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
                        AI_STP,
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
                        AI_STP,
                        "install",
                        "plan",
                        "--setup",
                        "${setup_id}@1.0",
                        "--project",
                        "${project}",
                        "--harness",
                        "${harness_id}",
                        "--provider",
                        PROVIDER,
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
                        AI_STP,
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
                        AI_STP,
                        "install",
                        "apply",
                        "--operation",
                        "${operation_id}",
                        "--provider",
                        PROVIDER,
                        "--json",
                    ],
                    "expect_json": {"ok": True, "data.state": "verified"},
                },
            ],
            "verify": [observer(prompt, True)],
        },
        "expect_paths": [
            {
                "path": "${target}/config/skills/experiment-smoke/SKILL.md",
                "contains": "AI_STP_EXPERIMENT_SMOKE",
            }
        ],
    }


def diagnostic_task(legacy: dict) -> dict:
    prompt = portable_prompt(legacy)
    return {
        "schema_version": 2,
        "id": legacy["id"],
        "title": legacy.get("title", ""),
        "prompt": prompt,
        "expect": str(legacy.get("expect", "")).strip(),
        "expected_verdict": "blocked",
        "diagnostic": {
            "reason": BLOCKER_REASONS.get(
                legacy["id"], "the original named skill fixture is unavailable"
            ),
            "expected_error": "AI_STP_NEEDS_CONFIGURATION",
        },
        "phases": {
            "prepare": [
                {"id": "doctor", "argv": [AI_STP, "doctor", "--json"]},
                {"id": "discover", "argv": [AI_STP, "component", "discover", "--json"]},
            ],
            "install": [],
            "verify": [],
        },
    }


def component_task(legacy: dict) -> dict:
    fixture_name, source_rel, destination, kind, _projection, expected_path, marker = (
        COMPONENT_FIXTURES[legacy["id"]]
    )
    prompt = portable_prompt(legacy)
    task = {
        "schema_version": 2,
        "id": legacy["id"],
        "title": legacy.get("title", ""),
        "prompt": prompt,
        "expect": str(legacy.get("expect", "")).strip(),
        "observer_failure_verdict": "blocked",
        "fixtures": [
            {
                "source": "${experiments}/fixtures/"
                + fixture_name
                + "/"
                + source_rel.replace("\\", "/"),
                "destination": destination.replace("\\", "/"),
            }
        ],
        "phases": {
            "prepare": [
                {"id": "doctor", "argv": [AI_STP, "doctor", "--json"]},
                {"id": "discover", "argv": [AI_STP, "component", "discover", "--json"]},
                {
                    "id": "adopt",
                    "argv": [
                        AI_STP,
                        "component",
                        "adopt",
                        "--path",
                        "${user_home}/" + destination.replace("\\", "/"),
                        "--json",
                    ],
                    "capture": {
                        "component_id": "data.stable_id",
                        "component_revision": "data.revision_id",
                    },
                },
                {
                    "id": "developer",
                    "argv": [AI_STP, "passport", "developer", "init", "--json"],
                },
                {
                    "id": "device",
                    "argv": [AI_STP, "passport", "device", "refresh", "--json"],
                },
                {
                    "id": "project",
                    "argv": [
                        AI_STP,
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
                        AI_STP,
                        "component",
                        "passport",
                        "update",
                        "--id",
                        "${component_id}",
                        "--expected-revision",
                        "${component_revision}",
                        "--from",
                        "${experiments}/fixtures/"
                        + fixture_name
                        + "/passport-patch.json",
                        "--confirm",
                        "--json",
                    ],
                    "capture": {"component_revision": "data.revision_id"},
                },
                {
                    "id": "release",
                    "argv": [
                        AI_STP,
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
                        AI_STP,
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
                        AI_STP,
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
                        AI_STP,
                        "install",
                        "plan",
                        "--setup",
                        "${setup_id}@1.0",
                        "--project",
                        "${project}",
                        "--harness",
                        "${harness_id}",
                        "--provider",
                        PROVIDER,
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
                        AI_STP,
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
                        AI_STP,
                        "install",
                        "apply",
                        "--operation",
                        "${operation_id}",
                        "--provider",
                        PROVIDER,
                        "--json",
                    ],
                    "expect_json": {"ok": True, "data.state": "verified"},
                },
            ],
            "verify": [
                observer(
                    prompt,
                    True,
                    {
                        "E32": "list_pages",
                        "E46": None,
                        "E47": None,
                        "E48": "experiment-plugin",
                        "E49": "experiment-reviewer",
                    }[legacy["id"]],
                    always_approve=legacy["id"] in {"E32", "E46"},
                )
            ],
        },
        "expect_paths": [
            {
                "path": "${target}/" + expected_path.replace("\\", "/"),
                "contains": marker,
            }
        ],
    }
    if kind == "hook":
        task["expected_verdict"] = "blocked"
        task["diagnostic"] = {
            "reason": BLOCKER_REASONS["E55"],
            "expected_error": "AI_STP_DEPENDENCY_UNAVAILABLE",
        }
    return task


def needs_configuration_task(legacy: dict) -> dict:
    return {
        "schema_version": 2,
        "id": legacy["id"],
        "title": legacy.get("title", ""),
        "prompt": portable_prompt(legacy),
        "expect": str(legacy.get("expect", "")).strip(),
        "expected_verdict": "blocked",
        "diagnostic": {
            "reason": (
                "the named external MCP needs its own public fixture, "
                "network policy, or credentials"
            ),
            "expected_error": "AI_STP_NEEDS_CONFIGURATION",
        },
        "phases": {
            "prepare": [
                {"id": "doctor", "argv": [AI_STP, "doctor", "--json"]},
                {"id": "discover", "argv": [AI_STP, "component", "discover", "--json"]},
            ],
            "install": [],
            "verify": [],
        },
    }


def main() -> None:
    for experiment_id in IDS:
        legacy = old_task(experiment_id)
        # A different named skill cannot be replaced by the smoke fixture without
        # changing the experiment. Missing original fixtures remain explicit blockers.
        number = int(experiment_id[1:])
        if experiment_id in COMPONENT_FIXTURES:
            task = component_task(legacy)
        elif 33 <= number <= 45:
            task = needs_configuration_task(legacy)
        else:
            task = diagnostic_task(legacy)
        directory = ROOT / f"20260825T160000_antigravity_{experiment_id}"
        directory.mkdir(exist_ok=True)
        (directory / "task.yaml").write_text(
            yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
