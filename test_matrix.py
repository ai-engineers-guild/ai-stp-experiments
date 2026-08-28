import json
import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import materialize
import matrix


class MatrixTests(unittest.TestCase):
    def test_all_nine_categories_have_manifested_experiments(self) -> None:
        rows = matrix.validate()
        self.assertEqual({row["category"] for row in rows}, set(matrix.CATEGORIES))
        self.assertEqual(len(rows), 81)
        self.assertEqual(
            {
                category: sum(row["category"] == category for row in rows)
                for category in matrix.CATEGORIES
            },
            matrix.EXPECTED_COUNTS,
        )

    def test_each_setup_has_two_requested_logical_objects(self) -> None:
        for row in matrix.cases(["setups"]):
            root = matrix.ROOT / row["path"]
            manifest = matrix.load(root / "experiment.yaml")
            counts = {}
            for fixture_id in row["fixtures"]:
                fixture = matrix.load(root / "fixtures" / fixture_id / "fixture.yaml")
                passport = json.loads(
                    (root / "fixtures" / fixture_id / "passport-patch.json").read_text(
                        encoding="utf-8"
                    )
                )
                kind = passport["component_type"]
                counts[kind] = counts.get(kind, 0) + len(fixture["objects"])
            self.assertTrue(
                all(
                    counts[kind] >= minimum
                    for kind, minimum in manifest["minimum_objects"].items()
                )
            )

    def test_generate_retains_unsupported_harnesses_as_evidence(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.yaml"
            argv = [
                "matrix.py",
                "generate",
                "--category",
                "hooks",
                "--id",
                "H05",
                "--harness",
                "antigravity",
                "--harness",
                "pi-omp",
                "--os",
                "windows",
                "--os",
                "linux",
                "--output",
                str(output),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(matrix.main(), 0)
            text = output.read_text(encoding="utf-8")
            self.assertEqual(text.count("harness_profile:"), 4)
            self.assertIn("harness_profile: pi-omp", text)
            self.assertEqual(text.count("expected: unsupported"), 2)
            self.assertIn("AI_STP_H05_PREINVOCATION", text)

    def test_materialize_applies_overlay_and_passport_override(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture"
            (fixture / "payload/common").mkdir(parents=True)
            (fixture / "payload/common/value.txt").write_text(
                "common", encoding="utf-8"
            )
            (fixture / "payload/harnesses/pi").mkdir(parents=True)
            (fixture / "payload/harnesses/pi/value.txt").write_text(
                "pi", encoding="utf-8"
            )
            (fixture / "passport-overrides").mkdir()
            (fixture / "passport-patch.json").write_text(
                '{"harness_id":"base"}', encoding="utf-8"
            )
            (fixture / "passport-overrides/pi.json").write_text(
                '{"harness_id":"pi"}', encoding="utf-8"
            )
            output = root / "out"
            materialize.materialize(fixture, "pi", output)
            self.assertEqual((output / "value.txt").read_text(encoding="utf-8"), "pi")
            self.assertIn(
                '"pi"', (output / "passport-patch.json").read_text(encoding="utf-8")
            )

    def test_all_experiments_have_materializable_pi_variants(self) -> None:
        with TemporaryDirectory() as directory:
            count = 0
            for row in matrix.cases():
                self.assertIn("pi", row["variants"], row["id"])
                for fixture_id in row["fixtures"]:
                    output = Path(directory) / row["id"] / fixture_id
                    fixture = matrix.ROOT / row["path"] / "fixtures" / fixture_id
                    materialize.materialize(fixture, "pi", output)
                    passport = json.loads(
                        (output / "passport-patch.json").read_text(encoding="utf-8")
                    )
                    self.assertEqual(passport["harness_id"], "pi")
                    count += 1
            self.assertGreaterEqual(count, 81)

    def test_pi_matrix_has_no_unsupported_experiments(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.yaml"
            argv = [
                "matrix.py", "generate", "--harness", "pi", "--os", "windows",
                "--output", str(output),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(matrix.main(), 0)
            generated = matrix.load(output)["experiments"]
            self.assertEqual(len(generated), 81)
            self.assertTrue(all(row["expected"] == "runnable" for row in generated))

    def test_codex_matrix_has_no_unsupported_experiments(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.yaml"
            argv = [
                "matrix.py", "generate", "--harness", "codex", "--os", "windows",
                "--output", str(output),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(matrix.main(), 0)
            generated = matrix.load(output)["experiments"]
            self.assertEqual(len(generated), 81)
            self.assertTrue(all(row["expected"] == "runnable" for row in generated))

    def test_codex_native_payloads_parse(self) -> None:
        root = matrix.EXPERIMENTS
        configs = list(root.rglob("payload/harnesses/codex/config.toml"))
        self.assertGreater(len(configs), 0)
        for path in configs:
            tomllib.loads(path.read_text(encoding="utf-8"))
        for path in root.rglob("payload/harnesses/codex/hooks.json"):
            hooks = json.loads(path.read_text(encoding="utf-8"))["hooks"]
            self.assertTrue(set(hooks) <= {
                "PreToolUse", "PermissionRequest", "PostToolUse", "PreCompact",
                "PostCompact", "SessionStart", "SessionEnd", "SubagentStart",
                "SubagentStop", "UserPromptSubmit", "Stop",
            })

    def test_antigravity_skill_materializes_as_authoring_source(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "out"
            materialize.materialize(
                matrix.ROOT / "experiments/skills/SK01/fixtures/main",
                "antigravity",
                output,
            )
            self.assertTrue(
                (output / "skills/experiment-sk01/SKILL.md").is_file()
            )
            self.assertFalse((output / "config").exists())

    def test_all_skills_materialize_as_discoverable_sources(self) -> None:
        with TemporaryDirectory() as directory:
            for row in matrix.cases(["skills"]):
                output = Path(directory) / row["id"]
                materialize.materialize(
                    matrix.ROOT / row["path"] / "fixtures/main",
                    "antigravity",
                    output,
                )
                passport = json.loads(
                    (output / "passport-patch.json").read_text(encoding="utf-8")
                )
                self.assertTrue(
                    (output / "skills" / passport["name"] / "SKILL.md").is_file()
                )
                self.assertEqual(passport["entry_points"], ["SKILL.md"])

    def test_setup_skills_materialize_as_discoverable_sources(self) -> None:
        with TemporaryDirectory() as directory:
            root = matrix.EXPERIMENTS / "setups/M01/fixtures"
            for fixture in ("M01-skill-a", "M01-skill-b"):
                output = Path(directory) / fixture
                materialize.materialize(root / fixture, "antigravity", output)
                self.assertTrue((output / "skills" / fixture / "SKILL.md").is_file())

    def test_native_overlays_exclude_portable_siblings(self) -> None:
        cases = (
            ("commands/C01/fixtures/main", "antigravity", "commands", ".agents/skills/experiment-c01/SKILL.md"),
            ("commands/C01/fixtures/main", "pi", "commands", ".pi/prompts/experiment-c01.md"),
            ("hooks/H01/fixtures/main", "pi", "config", "extensions/experiment-h01.ts"),
            ("plugins/P01/fixtures/main", "antigravity", "plugins", ".agents/plugins/ai-stp-p01-plugin/plugin.json"),
            ("plugins/P01/fixtures/main", "pi", "plugins", "extensions/ai-stp-p01-plugin.ts"),
            ("setups/M01/fixtures/mcp", "pi", ".mcp.json", ".pi/extensions/m01-mcps/index.ts"),
        )
        with TemporaryDirectory() as directory:
            for fixture, harness, excluded, expected in cases:
                output = Path(directory) / harness / fixture
                materialize.materialize(matrix.EXPERIMENTS / fixture, harness, output)
                self.assertFalse((output / excluded).exists(), (fixture, harness, excluded))
                self.assertTrue((output / expected).is_file(), (fixture, harness, expected))

    def test_all_grok_variants_materialize(self) -> None:
        with TemporaryDirectory() as directory:
            count = 0
            for row in matrix.cases():
                if "grok-build" not in row["variants"]:
                    continue
                for fixture_id in row["fixtures"]:
                    output = Path(directory) / row["id"] / fixture_id
                    materialize.materialize(
                        matrix.ROOT / row["path"] / "fixtures" / fixture_id,
                        "grok-build",
                        output,
                    )
                    passport = json.loads(
                        (output / "passport-patch.json").read_text(encoding="utf-8")
                    )
                    self.assertEqual(passport["harness_id"], "grok-build")
                    if row["component_type"] == "mcp":
                        self.assertTrue((output / "config.toml").is_file())
                        self.assertFalse((output / ".mcp.json").exists())
                    count += 1
            self.assertGreater(count, 0)

    def test_all_primary_harness_variants_materialize(self) -> None:
        with TemporaryDirectory() as directory:
            for harness in ("codex", "grok-build", "antigravity", "pi"):
                count = 0
                for row in matrix.cases():
                    if harness not in row["variants"]:
                        continue
                    for fixture_id in row["fixtures"]:
                        output = Path(directory) / harness / row["id"] / fixture_id
                        fixture = matrix.ROOT / row["path"] / "fixtures" / fixture_id
                        materialize.materialize(fixture, harness, output)
                        passport = json.loads(
                            (output / "passport-patch.json").read_text(encoding="utf-8")
                        )
                        self.assertEqual(passport["harness_id"], harness)
                        count += 1
                self.assertGreater(count, 0, harness)

    def test_observer_prompt_has_stable_state_contract(self) -> None:
        prompt = matrix.observation_prompt("SK01", "antigravity", "installed")
        self.assertIn("controller saves it as", prompt)
        self.assertIn("Do not write files", prompt)
        self.assertIn("Report facts observed in this new context", prompt)
        self.assertIn("expected_logical_objects:", prompt)
        self.assertIn("logical_objects:", prompt)
        self.assertIn("managed_paths:", prompt)
        self.assertNotIn("visible:", prompt)
        self.assertNotIn("notes:", prompt)
        self.assertIn("Do not invoke components during this phase", prompt)

    def test_installed_observer_runs_the_declared_probe(self) -> None:
        prompt = matrix.observation_prompt(
            "SK01", "antigravity", "installed", "Use experiment-sk01."
        )
        self.assertIn("Perform this exact read-only probe", prompt)
        self.assertIn("Use experiment-sk01.", prompt)

    def test_matrix_generates_exactly_one_installed_observer(self) -> None:
        with self.assertRaises(ValueError):
            matrix.observation_prompt("SK01", "pi", "baseline")
        with self.assertRaises(ValueError):
            matrix.observation_prompt("SK01", "pi", "restored")

    def test_pi_native_probes_are_declared(self) -> None:
        experiments = matrix.EXPERIMENTS
        command = matrix.load(experiments / "commands/C01/experiment.yaml")
        hook = matrix.load(experiments / "hooks/H01/experiment.yaml")
        setting = matrix.load(experiments / "settings/S01/experiment.yaml")
        setup = matrix.load(experiments / "setups/M01/experiment.yaml")

        self.assertEqual(command["observe"]["pi_probe"]["input"], "/experiment-c01")
        self.assertEqual(hook["observe"]["pi_probe"]["tools"], ["powershell"])
        self.assertFalse(
            setting["observe"]["pi_probe"]["values"]["enableInstallTelemetry"]
        )
        self.assertEqual(setup["observe"]["pi_probe"]["tools"], ["powershell"])

        extension = (
            experiments
            / "hooks/H01/fixtures/main/payload/harnesses/pi/extensions/experiment-h01.ts"
        ).read_text(encoding="utf-8")
        self.assertIn('"powershell"', extension)
        hook_override = json.loads(
            (
                experiments
                / "hooks/H01/fixtures/main/passport-overrides/pi.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(hook_override["native_ids"], ["tool_call"])

    def test_pi_runtime_probes_are_observable(self) -> None:
        root = matrix.EXPERIMENTS
        h01 = (root / "hooks/H01/fixtures/main/payload/harnesses/pi/extensions/experiment-h01.ts").read_text(encoding="utf-8")
        m01 = (root / "setups/M01/fixtures/hooks/payload/harnesses/pi/extensions/m01-hooks.ts").read_text(encoding="utf-8")
        s01 = matrix.load(root / "settings/S01/experiment.yaml")
        c01 = matrix.load(root / "commands/C01/experiment.yaml")
        self.assertNotIn("terminate: true", h01 + m01)
        self.assertIn("AI_STP_H02_ALLOW", m01)
        self.assertIn('event.toolName === "powershell"', m01)
        self.assertEqual(s01["observe"]["expect"]["key"], "enableInstallTelemetry")
        self.assertIn("/experiment-c01", c01["observe"]["probe"])


if __name__ == "__main__":
    unittest.main()
