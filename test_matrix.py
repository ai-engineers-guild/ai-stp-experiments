import json
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
                "H01",
                "--harness",
                "antigravity",
                "--harness",
                "pi",
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
            self.assertIn("harness_profile: pi", text)
            self.assertEqual(text.count("expected: unsupported"), 2)
            self.assertIn("AI_STP_H01_PRETOOLUSE", text)

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

    def test_real_pi_skill_variant_materializes_and_hook_refuses(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "skill"
            materialize.materialize(
                matrix.EXPERIMENTS / "skills/SK01/fixtures/main", "pi", output
            )
            self.assertTrue((output / "skills/experiment-sk01/SKILL.md").is_file())
            with self.assertRaisesRegex(ValueError, "no pi variant"):
                materialize.materialize(
                    matrix.EXPERIMENTS / "hooks/H01/fixtures/main",
                    "pi",
                    Path(directory) / "hook",
                )

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

    def test_observer_prompt_only_records_visible_state(self) -> None:
        prompt = matrix.observation_prompt("SK01", "antigravity", "installed")
        self.assertIn("state/SK01-antigravity-installed.yaml", prompt)
        self.assertIn("Report what is visible now", prompt)
        self.assertIn("Do not invoke components during this phase", prompt)

    def test_installed_observer_runs_the_declared_probe(self) -> None:
        prompt = matrix.observation_prompt(
            "SK01", "antigravity", "installed", "Use experiment-sk01."
        )
        self.assertIn("Perform this exact read-only probe", prompt)
        self.assertIn("Use experiment-sk01.", prompt)


if __name__ == "__main__":
    unittest.main()
