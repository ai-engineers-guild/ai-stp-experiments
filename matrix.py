"""Validate fixtures and generate a selectable experiment matrix."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
EXPERIMENTS = ROOT / "experiments"
KINDS = ("hooks", "settings", "plugins", "setups")
EXPECTED = {"hooks": 10, "settings": 5, "plugins": 5, "setups": 5}
HOOK_EVENTS = {
    "PreToolUse": 2,
    "PostToolUse": 2,
    "PreInvocation": 2,
    "PostInvocation": 2,
    "Stop": 2,
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cases(kinds: list[str] | None = None, ids: set[str] | None = None) -> list[dict]:
    rows = []
    for kind in kinds or list(KINDS):
        for directory in sorted((EXPERIMENTS / kind).iterdir()):
            if directory.is_dir() and (not ids or directory.name in ids):
                rows.append(
                    {
                        "id": directory.name,
                        "kind": kind,
                        "fixture": directory.relative_to(ROOT).as_posix(),
                    }
                )
    return rows


def validate() -> list[dict]:
    rows = cases()
    counts = Counter(row["kind"] for row in rows)
    if counts != Counter(EXPECTED):
        raise ValueError(f"case count mismatch: {dict(counts)}")

    events: Counter[str] = Counter()
    for row in rows:
        root = ROOT / row["fixture"]
        case_id, kind = row["id"], row["kind"]
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".md", ".yaml", ".yml"}:
                text = path.read_text(encoding="utf-8")
                if "C:\\Users" in text or "C:/Users" in text:
                    raise ValueError(f"{case_id}: machine-specific path in {path.name}")
        if not list(root.rglob("passport-patch.json")):
            raise ValueError(f"{case_id}: passport patch missing")
        if kind == "hooks":
            expected = read_json(root / "expect.json")
            hooks = read_json(root / "config/hooks.json")["hooks"]
            if len(hooks) != 1 or expected["event"] not in hooks:
                raise ValueError(f"{case_id}: malformed hook fixture")
            entries = hooks[expected["event"]]
            handler = entries[0]["hooks"][0] if "hooks" in entries[0] else entries[0]
            if not handler["command"].startswith("python config/hooks/"):
                raise ValueError(f"{case_id}: hook command is not portable")
            script = root / handler["command"].removeprefix("python ")
            if not script.is_file():
                raise ValueError(f"{case_id}: hook script missing")
            events[expected["event"]] += 1
        elif kind == "settings":
            expected = read_json(root / "expect.json")
            settings = read_json(root / "antigravity-cli/settings.json")
            if settings != {expected["key"]: expected["value"]}:
                raise ValueError(f"{case_id}: setting expectation mismatch")
        elif kind == "plugins":
            expected = read_json(root / "expect.json")
            plugin = root / "antigravity-cli/plugins" / expected["plugin"]
            if not (plugin / "plugin.json").is_file() or not list(
                (plugin / "skills").glob("*/SKILL.md")
            ):
                raise ValueError(f"{case_id}: incomplete plugin")
        else:
            manifest = read_json(root / "manifest.json")
            for component in ("skills", "hooks", "mcps", "settings", "subagents"):
                if len(manifest["members"][component]) < 2:
                    raise ValueError(f"{case_id}: fewer than two {component}")
            if len(read_json(root / "mcp/config/mcp_config.json")["mcpServers"]) < 2:
                raise ValueError(f"{case_id}: fewer than two MCP servers")
            hook_config = read_json(root / "hooks/config/hooks.json")["hooks"]
            handlers = sum(len(entries) for entries in hook_config.values())
            if handlers < 2:
                raise ValueError(f"{case_id}: fewer than two hook handlers")
            for entries in hook_config.values():
                for entry in entries:
                    handler = entry["hooks"][0] if "hooks" in entry else entry
                    script = root / "hooks" / handler["command"].removeprefix("python ")
                    if not script.is_file():
                        raise ValueError(f"{case_id}: setup hook script missing")
            if len(read_json(root / "settings/antigravity-cli/settings.json")) < 2:
                raise ValueError(f"{case_id}: fewer than two settings")
            if len(list((root / "skills").glob("*/SKILL.md"))) < 2:
                raise ValueError(f"{case_id}: fewer than two skill fixtures")
            if len(list((root / "subagents").glob("*/config/agents/*.md"))) < 2:
                raise ValueError(f"{case_id}: fewer than two subagent fixtures")
    if dict(events) != HOOK_EVENTS:
        raise ValueError(f"hook coverage mismatch: {dict(events)}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("validate", "generate"), nargs="?", default="validate"
    )
    parser.add_argument("--kind", action="append", choices=KINDS)
    parser.add_argument("--id", action="append", dest="ids")
    parser.add_argument("--harness", default="antigravity")
    parser.add_argument("--output", type=Path, default=ROOT / "_generated/matrix.yaml")
    args = parser.parse_args()
    all_rows = validate()
    selected = [
        {**row, "harness_profile": args.harness}
        for row in all_rows
        if (not args.kind or row["kind"] in args.kind)
        and (not args.ids or row["id"] in set(args.ids))
    ]
    if not selected:
        raise SystemExit("no experiments selected")
    if args.command == "generate":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            yaml.safe_dump(
                {"schema_version": 1, "experiments": selected}, sort_keys=False
            ),
            encoding="utf-8",
        )
        print(args.output)
    else:
        print("validated: 10 hooks, 5 settings, 5 plugins, 5 full setups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
