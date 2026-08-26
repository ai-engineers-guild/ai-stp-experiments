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
        self.assertEqual(len(rows), 30)

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

    def test_generate_filters_unsupported_harnesses(self) -> None:
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
            self.assertEqual(text.count("harness_profile:"), 2)
            self.assertNotIn("harness_profile: pi", text)

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


if __name__ == "__main__":
    unittest.main()
