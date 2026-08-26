"""Execute one schema-v2 experiment without a shell and retain complete evidence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml


PROFILES = Path(__file__).with_name("harnesses.yaml")
LOCAL_PROFILES = PROFILES.with_name("harnesses.local.yaml")


def expand(value: str, variables: dict[str, str]) -> str:
    for name, replacement in variables.items():
        value = value.replace("${" + name + "}", replacement)
    if "${" in value:
        raise ValueError(f"unresolved variable: {value}")
    return value


def select(payload: object, dotted_path: str) -> object:
    value = payload
    for part in dotted_path.split("."):
        if isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
            continue
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_path)
        value = value[part]
    return value


def run_step(
    step: dict, variables: dict[str, str], logs: Path, env: dict[str, str]
) -> dict:
    argv = [expand(str(item), variables) for item in step["argv"]]
    started = datetime.now(UTC).isoformat()
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
    )
    prefix = f"{int(datetime.now(UTC).timestamp() * 1000)}_{step['id']}"
    stdout_path, stderr_path = logs / f"{prefix}.stdout", logs / f"{prefix}.stderr"
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    record = {
        "id": step["id"],
        "argv": argv,
        "ran_at": started,
        "exit": completed.returncode,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "verdict": step.get("verdict", "pass"),
    }
    payload = None
    try:
        payload = json.loads(completed.stdout)
        record["json"] = payload
    except json.JSONDecodeError:
        record["json"] = None
    expected_exit = int(step.get("expect_exit", 0))
    if completed.returncode != expected_exit:
        raise RuntimeError(
            f"{step['id']} exited {completed.returncode}, expected {expected_exit}"
        )
    for dotted_path, expected in (step.get("expect_json") or {}).items():
        actual = select(payload, dotted_path)
        if actual != expected:
            raise RuntimeError(
                f"{step['id']} {dotted_path} is {actual!r}, expected {expected!r}"
            )
    for dotted_path, expected in (step.get("expect_json_contains") or {}).items():
        actual = select(payload, dotted_path)
        if (
            not isinstance(actual, str)
            or expand(str(expected), variables) not in actual
        ):
            raise RuntimeError(f"{step['id']} {dotted_path} lacks {expected!r}")
    for name, dotted_path in (step.get("capture") or {}).items():
        captured = select(payload, dotted_path)
        if not isinstance(captured, (str, int, float, bool)):
            raise TypeError(f"capture {name} must be scalar")
        variables[name] = str(captured)
    return record


def check_path(expectation: dict, variables: dict[str, str]) -> dict:
    path = Path(expand(str(expectation["path"]), variables))
    exists = path.is_file()
    expected = expectation.get("exists", True)
    record = {
        "path": str(path),
        "exists": exists,
        "expected": expected,
        "verdict": "pass",
    }
    if exists is not expected:
        record["verdict"] = "fail"
        return record
    if exists and "contains" in expectation:
        marker = expand(str(expectation["contains"]), variables)
        record["contains"] = marker
        if marker not in path.read_text(encoding="utf-8"):
            record["verdict"] = "fail"
    return record


def load_profile(
    task: dict, variables: dict[str, str], override: str | None = None
) -> tuple[str, dict]:
    name = override or str(task.get("harness_profile", "antigravity"))
    profiles = yaml.safe_load(PROFILES.read_text(encoding="utf-8"))
    if LOCAL_PROFILES.is_file():
        for key, value in yaml.safe_load(
            LOCAL_PROFILES.read_text(encoding="utf-8")
        ).items():
            profiles.setdefault(key, {}).update(value)
    if name not in profiles or not isinstance(profiles[name], dict):
        raise ValueError(f"unknown harness profile: {name}")
    profile = profiles[name]
    for key, value in profile.items():
        if isinstance(value, (str, int, float, bool)):
            variables[key] = expand(str(value), variables)
    return name, profile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--harness-profile")
    args = parser.parse_args()
    task = yaml.safe_load(args.task.read_text(encoding="utf-8"))
    if task.get("schema_version") != 2:
        raise ValueError("task schema_version must be 2")
    run_root = args.run_root.resolve()
    project, user_home, logs = (run_root / name for name in ("project", "home", "logs"))
    variables = {
        "project": str(project),
        "user_home": str(user_home),
        "run_root": str(run_root),
        "experiments": str(PROFILES.parent),
        "workspace_root": str(PROFILES.parent.parent),
        "skills_root": os.environ.get(
            "AI_STP_SKILLS_ROOT", str(PROFILES.parent.parent / "my_skills")
        ),
        "python": sys.executable,
        "ai_stp": os.environ.get("AI_STP_BIN") or shutil.which("ai-stp") or "ai-stp",
    }
    profile_name, profile = load_profile(task, variables, args.harness_profile)
    target = Path(variables["target"])
    for path in (project, target, logs):
        path.mkdir(parents=True, exist_ok=True)
    variables["target"] = str(target)
    env = os.environ.copy()
    env["AI_STP_FORCE_FILE_CREDENTIAL_STORE"] = "1"
    if profile.get("isolate_home", True):
        env.update({"HOME": str(user_home), "USERPROFILE": str(user_home)})
    for name, value in (profile.get("environment") or {}).items():
        env[str(name)] = expand(str(value), variables)
    for fixture in task.get("fixtures", []):
        source = Path(expand(str(fixture["source"]), variables)).resolve()
        destination = user_home / expand(str(fixture["destination"]), variables)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    result = {
        "schema_version": 2,
        "id": task["id"],
        "harness_profile": profile_name,
        "ran_at": datetime.now(UTC).isoformat(),
        "project": str(project),
        "user_home": str(user_home),
        "target": str(target),
        "phases": {},
        "assertions": [],
        "verdict": "inconclusive",
    }
    phase = "prepare"
    try:
        for phase, steps in task["phases"].items():
            if phase == "cleanup":
                continue
            result["phases"][phase] = []
            for step in steps:
                result["phases"][phase].append(run_step(step, variables, logs, env))
        result["assertions"] = [
            check_path(item, variables) for item in task.get("expect_paths", [])
        ]
        step_verdicts = [
            step["verdict"] for steps in result["phases"].values() for step in steps
        ]
        assertion_verdicts = [item["verdict"] for item in result["assertions"]]
        result["verdict"] = (
            "fail"
            if "fail" in step_verdicts + assertion_verdicts
            else task.get("expected_verdict", "pass")
        )
    except Exception as exc:
        result["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        if phase == "verify" and task.get("observer_failure_verdict") == "blocked":
            result["verdict"] = "blocked"
    finally:
        cleanup = task["phases"].get("cleanup", [])
        required = task.get("cleanup_requires", [])
        if cleanup and all(name in variables for name in required):
            result["phases"]["cleanup"] = []
            try:
                for step in cleanup:
                    result["phases"]["cleanup"].append(
                        run_step(step, variables, logs, env)
                    )
            except Exception as exc:
                result["cleanup_failure"] = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
                result["verdict"] = "fail"
    (run_root / "results.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return 1 if result["verdict"] in {"fail", "inconclusive"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
