import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import delegate
import run_all
import run_experiment


class RunnerTests(unittest.TestCase):
    def test_batch_contains_exactly_the_canonical_corpus(self) -> None:
        rows = run_all.tasks()
        self.assertEqual(len(rows), 57)
        self.assertEqual(len({experiment_id for experiment_id, _ in rows}), 57)

    def test_expand_and_select_fail_closed(self) -> None:
        self.assertEqual(run_experiment.expand("x/${a}", {"a": "b"}), "x/b")
        with self.assertRaises(ValueError):
            run_experiment.expand("${missing}", {})
        self.assertEqual(run_experiment.select({"data": {"id": "x"}}, "data.id"), "x")
        self.assertEqual(
            run_experiment.select({"data": [{"id": "x"}]}, "data.0.id"), "x"
        )
        with self.assertRaises(KeyError):
            run_experiment.select({}, "data.id")

    def test_check_path_proves_content(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "proof.txt"
            path.write_text("marker", encoding="utf-8")
            self.assertEqual(
                run_experiment.check_path(
                    {"path": "${root}/proof.txt", "contains": "marker"},
                    {"root": directory},
                )["verdict"],
                "pass",
            )

    def test_expected_blocker_is_not_a_runner_failure(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            task = root / "task.yaml"
            task.write_text(
                "schema_version: 2\nid: blocked\nexpected_verdict: blocked\n"
                "phases:\n  prepare: []\n  install: []\n  verify: []\n",
                encoding="utf-8",
            )
            with patch(
                "sys.argv",
                ["run_experiment.py", str(task), "--run-root", str(root / "run")],
            ):
                self.assertEqual(run_experiment.main(), 0)
            self.assertEqual(
                run_experiment.check_path(
                    {"path": "${root}/proof.txt", "contains": "missing"},
                    {"root": directory},
                )["verdict"],
                "fail",
            )

    def test_harness_profiles_resolve_targets_and_commands(self) -> None:
        variables = {
            "project": "p",
            "user_home": "/tmp/home",
            "run_root": "r",
            "skills_root": "/skills",
            "experiments": "/experiments",
        }
        name, profile = run_experiment.load_profile(
            {"harness_profile": "pi-omp"}, variables
        )
        self.assertEqual(name, "pi-omp")
        self.assertEqual(variables["harness_id"], "pi")
        self.assertEqual(variables["runtime"], "omp")
        self.assertTrue(profile["isolate_home"])
        self.assertEqual(variables["target"], "/tmp/home/.omp/agent")

    def test_shared_profiles_are_machine_agnostic(self) -> None:
        text = run_experiment.PROFILES.read_text(encoding="utf-8")
        self.assertNotIn("C:\\Users", text)
        for name in (
            "antigravity",
            "codex",
            "claude-code",
            "pi",
            "opencode",
            "grok-build",
        ):
            variables = {
                "project": "/project",
                "user_home": "/home/test",
                "run_root": "/run",
                "skills_root": "/skills",
                "experiments": "/experiments",
            }
            run_experiment.load_profile({}, variables, name)
            self.assertTrue(variables["target"].startswith("/home/test/"))

    def test_delegate_adapter_maps_pi_specific_arguments(self) -> None:
        argv = [
            "delegate.py",
            "--harness",
            "pi",
            "--backend",
            "delegate_pi.py",
            "--cwd",
            "/project",
            "--task",
            "check",
            "--output-dir",
            "/output",
            "--target",
            "/agent",
            "--runtime",
            "pi",
            "--always-approve",
        ]
        with patch("sys.argv", argv), patch("delegate.subprocess.run") as run:
            run.return_value.returncode = 0
            self.assertEqual(delegate.main(), 0)
        command = run.call_args.args[0]
        self.assertIn("--agent-dir", command)
        self.assertIn("--auto-approve", command)


if __name__ == "__main__":
    unittest.main()
