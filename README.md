# ai-stp experiments

Private cross-platform corpus of hypotheses, fixtures and observation prompts for
testing `ai-stp × setup-system × OS × harness × component`.

```text
experiments/
├── instructions/  ├── skills/    ├── mcps/
├── hooks/         ├── commands/  ├── agents/
├── plugins/       ├── settings/  └── setups/
```

The corpus contains exactly 81 logical experiments: 25 skills, 16 MCP, 10 hooks,
five of every other component type, and five full setups.

Every category contains experiments; every experiment contains `experiment.yaml`
and independent `fixtures/<id>` directories. Each fixture has `fixture.yaml`, a
base passport and one or more provider variants in
`payload/harnesses/<profile>`; passport differences go in
`passport-overrides/<profile>.json`. See [the fixture contract](specs/fixture-contract.md).
One experiment is shared by every harness. The generated matrix retains a row
with `expected: unsupported` when a setup-system has no variant for that
component; unsupported combinations are evidence and are never silently dropped.

```bash
python -m pip install .
python matrix.py validate
python matrix.py generate --category hooks --id H01 --harness antigravity --os windows
python materialize.py experiments/hooks/H01/fixtures/main --harness antigravity --output _generated/H01
```

This repository does not execute `ai-stp`, providers or harnesses. Any controller
harness reads one generated matrix row and uses its installed `ai-stp` skill to
perform backup, setup installation and rollback on any target harness. Controller
and target are independent matrix dimensions and may name the same harness. The
target receives the generated observer prompt at `baseline`, `installed` and
`restored`; it only lists visible objects and writes the requested local state
YAML. It does not invoke components or change configuration. The same matrix row
carries the experiment's expected observation so the controller can compare it
with the three state files without telling the observer what it should find.

Generated matrices, state files, results and logs are ignored. The controlling
controller owns execution evidence outside this declarative corpus.
