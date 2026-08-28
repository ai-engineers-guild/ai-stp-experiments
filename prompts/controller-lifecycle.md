# Controller lifecycle

You are the controller harness for target harness `{harness}`.

Read this repository's manifests, generated matrix row and installed observer
prompt. This repository is declarative: do not add or run lifecycle code here.

For every runnable experiment:

1. Create a separate disposable target.
2. Use the installed `ai-stp` skill and CLI to build and preserve the immutable
   plan and `plan_digest`.
3. Use `ai-stp` to create a backup and preserve its exact `operation_id`,
   provider state and `backup_ref`.
4. Use `ai-stp` to install/apply only the selected fixture or setup.
5. Start one fresh target-harness context through that harness's delegate skill
   and run the matrix row's `observer_prompt` exactly once. Allow at most 120
   seconds, never start a second observer while one is active, and terminate the
   entire delegate process tree on timeout.
6. Verify that the observer reports only the expected logical objects and that
   every declared safe probe actually succeeds.
7. In a `finally` path, use `ai-stp` to rollback the exact `backup_ref` and
   require provider state `verified`, including after observer timeout or crash.
8. Compare restored managed state mechanically with the backup. Do not call the
   delegate again.

Never invoke a provider directly, edit target configuration, copy credentials,
reuse a target-harness session, or treat file existence as runtime proof. For an
unsupported matrix row, preserve the machine reason and perform no install or
rollback.

Keep results outside this repository's source tree. Save all plan digests,
operation IDs, backup refs, provider responses, observer YAML and the final
report.

Report lifecycle and observation independently. An observer timeout is
`observer_timeout`, not an install failure; continue only after rollback,
restored-state comparison and process-tree cleanup have all completed.
