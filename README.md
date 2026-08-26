# ai-stp experiments

Private cross-platform fixture corpus for testing ai-stp setup providers and
coding-agent harnesses on Windows, macOS, and Linux.

## Fixture layout

```text
experiments/
├── hooks/H01..H10
├── settings/S01..S05
├── plugins/P01..P05
└── setups/M01..M05
```

Every case owns its payload, passport patch and machine-readable expectation or
manifest. There are no timestamp-based source directories. Timestamps belong
only to ignored run output.

Coverage:

- 10 hooks: two cases for each `PreToolUse`, `PostToolUse`, `PreInvocation`,
  `PostInvocation`, and `Stop` event;
- 5 settings: one explicit setting per case;
- 5 plugins: unique plugin and nested skill per case;
- 5 full setups: at least two skills, hooks, MCP servers, settings and
  subagents in every setup.

## Validate and select

```bash
python -m pip install .
python matrix.py validate
python matrix.py generate --harness antigravity
python matrix.py generate --kind hooks --id H01 --id H02 --harness codex
```

Generated selections are written to `_generated/matrix.yaml`. Local execution
evidence belongs under `runs/` or `results/`; all three locations are ignored.

Machine-specific CLI, delegate and provider paths are placed in the ignored
`harnesses.local.yaml`, using `harnesses.local.example.yaml` as the template.
Use `python doctor.py --profile <name>` before a live ai-stp run.

The repository does not install CLIs, authenticate accounts, or publish run
evidence. A green fixture validation proves corpus structure and portability;
live installation/observer/rollback evidence must be produced on the target OS
with its configured provider and delegate.
