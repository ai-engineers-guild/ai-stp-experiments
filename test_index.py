import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import generate_index


class IndexTests(unittest.TestCase):
    def test_lists_direct_run_children_in_stable_order(self) -> None:
        with TemporaryDirectory() as directory:
            runs = Path(directory) / "runs"
            (runs / "zeta").mkdir(parents=True)
            (runs / "zeta" / "report.md").write_text("# Zeta", encoding="utf-8")
            (runs / "alpha").mkdir()
            (runs / "notes.txt").write_text("notes", encoding="utf-8")

            index = generate_index.build_index(runs)

            self.assertIn("Archive entries: 3.", index)
            self.assertLess(index.index("`alpha`"), index.index("`zeta`"))
            self.assertLess(index.index("`zeta`"), index.index("`notes.txt`"))
            self.assertIn("[runs/alpha](<runs/alpha>)", index)
            self.assertIn("[runs/notes.txt](<runs/notes.txt>)", index)


if __name__ == "__main__":
    unittest.main()
