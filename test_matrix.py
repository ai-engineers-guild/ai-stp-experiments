import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import matrix


class MatrixTests(unittest.TestCase):
    def test_complete_fixture_matrix(self) -> None:
        rows = matrix.validate()
        self.assertEqual(len(rows), 25)
        self.assertEqual(
            {row["id"] for row in rows if row["kind"] == "hooks"},
            {f"H{i:02d}" for i in range(1, 11)},
        )

    def test_each_setup_has_two_of_every_requested_type(self) -> None:
        for row in matrix.cases(["setups"]):
            members = matrix.read_json(matrix.ROOT / row["fixture"] / "manifest.json")[
                "members"
            ]
            self.assertTrue(all(len(value) >= 2 for value in members.values()))

    def test_generate_selects_requested_cases_and_harness(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.yaml"
            with patch(
                "sys.argv",
                [
                    "matrix.py",
                    "generate",
                    "--kind",
                    "hooks",
                    "--id",
                    "H01",
                    "--harness",
                    "codex",
                    "--output",
                    str(output),
                ],
            ):
                self.assertEqual(matrix.main(), 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("H01", text)
            self.assertIn("harness_profile: codex", text)


if __name__ == "__main__":
    unittest.main()
