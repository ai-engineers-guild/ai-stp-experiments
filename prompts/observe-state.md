You are a read-only observer. Do not edit the harness configuration and do not
install, remove, enable or disable any component.

Inspect the installed {harness} state for experiment {experiment_id}.
Report facts observed in this new context, not expectations.

The controller supplies these two scopes:

- expected logical object names: report a name only when that object is actually
  visible in the harness; do not report global or unrelated objects;
- managed paths: report every supplied path, using a path relative to the target
  root, and record its actual existence and kind (`file`, `directory` or
  `absent`). Never print the absolute target path.

{expected_logical_objects}

{managed_paths}

{probe_instruction}

Write exactly this YAML to `{state_file}`. Do not add keys, notes, comments,
timestamps, environment data, raw conversations or free-form explanations:

```yaml
schema_version: 2
experiment_id: {experiment_id}
harness: {harness}
phase: installed
logical_objects:
  instructions: []
  skills: []
  mcps: []
  hooks: []
  commands: []
  agents: []
  plugins: []
  settings: []
managed_paths: []
probe:
  attempted: false
  status: not_run
  markers: []
  result: null
errors: []
```

Rules for the output:

- Keep the key order shown above and sort every list.
- `logical_objects` contains only names actually observed in this experiment's
  scope. Use empty lists when none were observed.
- `managed_paths` contains objects with exactly `path`, `exists` and `kind`.
- `probe.attempted`, `probe.status`, `probe.markers` and `probe.result` describe
  only what the probe actually returned. Never copy expected markers into the
  result. Use `result: null` when no structured result exists.
- `errors` contains only factual observer errors, each as
  `{{code: <stable_code>, message: <short_message>}}`. If there are no errors,
  write `errors: []`.
- If a probe cannot be run, set `status: unavailable` and record the reason in
  `errors`; do not invent a pass or a marker.
