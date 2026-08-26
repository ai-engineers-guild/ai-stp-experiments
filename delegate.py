"""Normalize experiment observer calls onto existing delegate skills."""

from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--timeout", default="45m")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model")
    parser.add_argument("--target")
    parser.add_argument("--runtime")
    parser.add_argument("--profile")
    parser.add_argument("--always-approve", action="store_true")
    parser.add_argument("--no-tools", action="store_true")
    args = parser.parse_args()
    command = [
        sys.executable,
        args.backend,
        "--cwd",
        args.cwd,
        "--task",
        args.task,
        "--timeout",
        args.timeout,
        "--output-dir",
        args.output_dir,
    ]
    if args.model:
        command += ["--model", args.model]
    if args.always_approve:
        command.append("--auto-approve" if args.harness == "pi" else "--always-approve")
    if args.harness == "antigravity" and args.target:
        command += ["--user-home", args.target]
    if args.harness == "pi":
        if args.runtime:
            command += ["--runtime", args.runtime]
        if args.profile:
            command += ["--profile", args.profile]
        if args.target:
            command += ["--agent-dir", args.target]
        if args.no_tools:
            command.append("--no-tools")
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
