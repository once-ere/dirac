from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check_jupyter_notebook


class JupyterNotebookTests(unittest.TestCase):
    def test_executed_notebook_is_self_consistent(self) -> None:
        repository_root = Path(__file__).resolve().parent.parent
        report = check_jupyter_notebook.verify_notebook(
            repository_root / "notebooks" / "dirac_triality.executed.ipynb",
            None,
        )
        self.assertEqual(
            [name for name, passed in report["checks"].items() if not passed],
            [],
        )


if __name__ == "__main__":
    unittest.main()