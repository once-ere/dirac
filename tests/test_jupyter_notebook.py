from __future__ import annotations

import unittest
from pathlib import Path

import nbformat

from scripts import check_jupyter_notebook
from scripts import run_jupyter_notebook


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

    def test_adjacent_stream_outputs_are_coalesced(self) -> None:
        notebook = nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_code_cell(
                    outputs=[
                        nbformat.v4.new_output(
                            "stream", name="stdout", text="first\n"
                        ),
                        nbformat.v4.new_output(
                            "stream", name="stdout", text="second\n"
                        ),
                        nbformat.v4.new_output(
                            "stream", name="stderr", text="warning\n"
                        ),
                    ]
                )
            ]
        )

        run_jupyter_notebook.coalesce_stream_outputs(notebook)

        self.assertEqual(len(notebook.cells[0].outputs), 2)
        self.assertEqual(
            notebook.cells[0].outputs[0].text,
            "first\nsecond\n",
        )
        self.assertEqual(notebook.cells[0].outputs[1].text, "warning\n")


if __name__ == "__main__":
    unittest.main()