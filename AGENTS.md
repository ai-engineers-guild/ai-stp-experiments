# ai-stp-experiments

This repository contains only declarative experiments: manifests, fixtures,
passport patches and observer prompts. It must not contain lifecycle runners,
provider wrappers or harness-specific installation scripts.

The domain has eight component types: `instruction`, `skill`, `mcp`, `hook`,
`command`, `agent`, `plugin` and `setting`. `setup` is the ninth experiment
category and composes components; it is not a ninth component type.

Use `payload/common` by default. Add `payload/harnesses/<profile>` only when the
common source cannot represent that harness's native authoring format. Put only
passport differences in `passport-overrides/<profile>.json`.

Lifecycle execution belongs to the external controller. It uses the installed
`ai-stp` skill and CLI for plan, backup, install and rollback, and invokes the
target harness delegate once after install for read-only observation. Never call
a provider directly and never store run evidence in the corpus.

Generated matrices, run history, state, logs and reports stay ignored. Validate
changes with `python matrix.py validate` and `python -m unittest test_matrix.py`.
