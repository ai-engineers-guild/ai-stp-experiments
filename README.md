# ai-stp experiments

Private cross-platform corpus of hypotheses, fixtures and observation prompts for
testing `ai-stp × setup-system × OS × harness × component`.

```text
experiments/
├── instructions/  ├── skills/    ├── mcps/
├── hooks/         ├── commands/  ├── agents/
├── plugins/       ├── settings/  └── setups/
```

The corpus contains exactly 81 logical experiments: 76 experiments across the
eight component types (25 skills, 16 MCP, 10 hooks and five of each remaining
type), plus five full setup experiments. A setup is a composition category, not
a ninth component type.

Every category contains experiments; every experiment contains `experiment.yaml`
and independent `fixtures/<id>` directories. Each fixture has `fixture.yaml`, a
base passport and a shared source in `payload/common` when the component format
is portable. A `payload/harnesses/<profile>` overlay is present only when that
harness needs a different native format; passport differences go in
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
target receives exactly one generated observer prompt after install and before
rollback. It lists visible objects, performs only the fixture's declared safe
probe, and writes the installed-state YAML. It never changes configuration.
Backup, install, managed-state comparison and rollback belong to the external
controller and are executed only through `ai-stp`.

Generated matrices, state files, results and logs are ignored. The controlling
controller owns execution evidence outside this declarative corpus.
