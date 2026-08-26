import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import compose
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
            self.assertTrue(
                (output / "skills/experiment-sk01/SKILL.md").is_file()
            )
            with self.assertRaisesRegex(ValueError, "no pi variant"):
                materialize.materialize(
                    matrix.EXPERIMENTS / "hooks/H01/fixtures/main",
                    "pi",
                    Path(directory) / "hook",
                )

    def test_compose_builds_full_setup_lifecycle_and_rejects_missing_variant(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "M01.yaml"
            task = compose.compose(
                matrix.EXPERIMENTS / "setups/M01", "antigravity", output
            )
            self.assertEqual(len(task["phases"]["cleanup"]), 3)
            self.assertEqual(
                len(
                    [
                        step
                        for step in task["phases"]["prepare"]
                        if step["id"].startswith("adopt-")
                    ]
                ),
                7,
            )
            with self.assertRaisesRegex(ValueError, "no pi provider variant"):
                compose.compose(
                    matrix.EXPERIMENTS / "hooks/H01", "pi", Path(directory) / "H01.yaml"
                )


if __name__ == "__main__":
    unittest.main()
