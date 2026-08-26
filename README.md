# ai-stp experiments

Private cross-platform corpus for testing `ai-stp CLI × provider × OS × harness × component`.

```text
experiments/
├── instructions/  ├── skills/    ├── mcps/
├── hooks/         ├── commands/  ├── agents/
├── plugins/       ├── settings/  └── setups/
```

Every category contains experiments; every experiment contains `experiment.yaml`
and independent `fixtures/<id>` directories. Each fixture has `fixture.yaml`, a
base passport and `payload/common`. Harness-native files are optional overlays in
`payload/harnesses/<profile>`; passport differences go in
`passport-overrides/<profile>.json`. See [the fixture contract](specs/fixture-contract.md).

```bash
python -m pip install .
python matrix.py validate
python matrix.py generate --category hooks --id H01 --harness antigravity --os windows
python materialize.py experiments/hooks/H01/fixtures/main --harness antigravity --output _generated/H01
python doctor.py --profile antigravity
python run_experiment.py path/to/task.yaml --run-root runs/H01
```

`run_experiment.py` uses an isolated HOME by default, records target snapshots,
runs cleanup/rollback in `finally`, and fails if the restored target differs from
the baseline. A real target requires both `--live-target` and the exact resolved
`--confirm-target`; target writes still belong only to ai-stp and its provider.

Machine-specific executable, delegate and provider paths belong in ignored
`harnesses.local.yaml`. Generated matrices, runs, results and logs are ignored.
