Do not edit the harness configuration and do not install, remove, enable or
disable any component.

Inspect the current {harness} state for experiment {experiment_id} during the
{phase} phase. Report what is visible now, not what should be present. List names
only for every category below. Use an empty list when none are visible and add a
short note when a category cannot be inspected.

{probe_instruction}

Write this YAML to `{state_file}`:

```yaml
schema_version: 1
experiment_id: {experiment_id}
harness: {harness}
phase: {phase}
visible:
  instructions: []
  skills: []
  mcps: []
  hooks: []
  commands: []
  agents: []
  plugins: []
  settings: []
probe:
  attempted: false
  status: not_run
  markers: []
  notes: []
notes: []
```

Set `probe.attempted` and `probe.status` from what actually happened. Record only
markers returned by the component or hook, never expected markers copied from
this prompt.
