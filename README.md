# ai-stp experiments

Private cross-platform corpus for testing `ai-stp CLI × provider × OS × harness × component`.

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
python compose.py experiments/skills/SK01 --harness pi-omp --output _generated/SK01-pi-omp.yaml
python doctor.py --profile antigravity
python run_experiment.py _generated/SK01-pi-omp.yaml --run-root runs/SK01-pi-omp
```

`run_experiment.py` uses an isolated HOME by default, records target snapshots,
runs cleanup/rollback in `finally`, and fails if the restored target differs from
the baseline. A real target requires both `--live-target` and the exact resolved
`--confirm-target`; target writes still belong only to ai-stp and its provider.
`compose.py` refuses unavailable variants before touching a target and generates
the complete ai-stp + delegate + rollback lifecycle for both single components
and multi-fixture setups.

Machine-specific executable, delegate and provider paths belong in ignored
`harnesses.local.yaml`. Generated matrices, runs, results and logs are ignored.
