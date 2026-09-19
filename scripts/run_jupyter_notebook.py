#!/usr/bin/env python3
"""Execute and normalize the generated Jupyter notebook."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import warnings

import nbformat
from nbclient import NotebookClient


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path(__file__).resolve().parent.parent
    notebook_path = arguments.notebook.resolve()
    output_path = (arguments.output or notebook_path).resolve()
    warnings.filterwarnings(
        "ignore",
        message="Proactor event loop does not implement add_reader.*",
        category=RuntimeWarning,
        module="zmq._future",
    )
    notebook = nbformat.read(notebook_path, as_version=4)
    os.environ["PYTHONHASHSEED"] = "0"
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(repository_root)}},
        allow_errors=False,
    )
    client.execute()
    for cell in notebook.cells:
        cell.metadata.pop("execution", None)
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata["language_info"] = {"name": "python", "version": "3"}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"cell_count={len(notebook.cells)}")
    print(
        "executed_code_cell_count="
        f"{sum(cell.cell_type == 'code' and cell.execution_count is not None for cell in notebook.cells)}"
    )
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())