#!/usr/bin/env python3
"""Build the deterministic Dirac triality Jupyter notebook."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notebooks/dirac_triality.ipynb"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_cell(identifier: str, source: str) -> dict[str, Any]:
    return {
        "cell_type": "markdown",
        "id": identifier,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code_cell(identifier: str, source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": identifier,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path(__file__).resolve().parent.parent
    output_path = arguments.output.resolve()
    inputs = {
        "cl44": repository_root / "artifacts" / "exact" / "cl44-seed.json",
        "split": repository_root / "artifacts" / "exact" / "split-octonion.json",
        "triality": repository_root / "artifacts" / "exact" / "triality44.json",
        "transport": repository_root
        / "artifacts"
        / "triality-transport"
        / "summary.json",
        "cosmology": repository_root
        / "artifacts"
        / "spinor-cosmology"
        / "summary.json",
    }
    input_hashes = {name: sha256_file(path) for name, path in inputs.items()}

    cells = [
        markdown_cell(
            "title",
            "# Real $Cl(4,4)$, split octonions, and triality\n\n"
            "This generated SolveIt-style notebook checks the exact real algebra and "
            "both pure-Rust CVODE studies. It treats historical notebook output as "
            "evidence only and uses the repository's independent checkers.",
        ),
        code_cell(
            "setup",
            "from pathlib import Path\n"
            "import csv\n"
            "import hashlib\n"
            "import json\n"
            "import subprocess\n"
            "import sys\n\n"
            "ROOT = Path.cwd().resolve()\n"
            "assert (ROOT / 'Cargo.toml').is_file()\n"
            "def sha256(path):\n"
            "    return hashlib.sha256(path.read_bytes()).hexdigest()\n"
            "def run_check(script, *arguments):\n"
            "    process = subprocess.run(\n"
            "        [sys.executable, str(ROOT / script), *arguments],\n"
            "        cwd=ROOT, text=True, capture_output=True, check=False\n"
            "    )\n"
            "    print(process.stdout.strip())\n"
            "    assert process.returncode == 0, process.stderr\n"
            "    return process.stdout\n"
            f"EXPECTED_HASHES = {input_hashes!r}\n",
        ),
        markdown_cell(
            "exact-heading",
            "## Independent exact-algebra checks\n\n"
            "The checks below use standard-library integer and rational arithmetic; "
            "they do not trust stored Wolfram results.",
        ),
        code_cell(
            "exact-checks",
            "run_check('scripts/check_cl44_fixture.py')\n"
            "run_check('scripts/check_split_octonion_fixture.py')\n"
            "run_check('scripts/check_triality44_fixture.py')\n",
        ),
        markdown_cell(
            "numerical-heading",
            "## CVODE studies\n\n"
            "The transport study evolves 24 real states. The cosmology study evolves "
            "18 real states and is compared against analytic background identities.",
        ),
        code_cell(
            "numerical-checks",
            "run_check('scripts/check_triality_transport.py')\n"
            "run_check('scripts/check_spinor_cosmology.py')\n"
            "transport = json.loads((ROOT / 'artifacts/triality-transport/summary.json').read_text())\n"
            "cosmology = json.loads((ROOT / 'artifacts/spinor-cosmology/summary.json').read_text())\n"
            "print({'transport_samples': transport['sampleCount'], "
            "'cosmology_samples': cosmology['sampleCount']})\n",
        ),
        markdown_cell(
            "data-heading",
            "## Dataset inspection\n\n"
            "The notebook reads the canonical CSV files directly and checks their "
            "endpoint grids and row counts.",
        ),
        code_cell(
            "data-checks",
            "def read_csv(relative_path):\n"
            "    with (ROOT / relative_path).open(newline='', encoding='utf-8') as stream:\n"
            "        return list(csv.DictReader(stream))\n"
            "transport_rows = read_csv('artifacts/triality-transport/trajectory.csv')\n"
            "cosmology_rows = read_csv('artifacts/spinor-cosmology/background.csv')\n"
            "assert len(transport_rows) == 41\n"
            "assert len(cosmology_rows) == 1201\n"
            "assert float(transport_rows[0]['t']) == 0.0\n"
            "assert float(transport_rows[-1]['t']) == 4.0\n"
            "assert float(cosmology_rows[0]['N']) == -4.0\n"
            "assert float(cosmology_rows[-1]['N']) == 1.0\n"
            "{'transport_final': transport_rows[-1], "
            "'cosmology_present': cosmology_rows[960]}\n",
        ),
        markdown_cell(
            "report-heading",
            "## Reproducibility report",
        ),
        code_cell(
            "report",
            "actual_hashes = {\n"
            "    'cl44': sha256(ROOT / 'artifacts/exact/cl44-seed.json'),\n"
            "    'split': sha256(ROOT / 'artifacts/exact/split-octonion.json'),\n"
            "    'triality': sha256(ROOT / 'artifacts/exact/triality44.json'),\n"
            "    'transport': sha256(ROOT / 'artifacts/triality-transport/summary.json'),\n"
            "    'cosmology': sha256(ROOT / 'artifacts/spinor-cosmology/summary.json'),\n"
            "}\n"
            "NOTEBOOK_CHECKS = {\n"
            "    'input_hashes': actual_hashes == EXPECTED_HASHES,\n"
            "    'transport_success': transport['verdict'] == 'SUCCESS',\n"
            "    'transport_dimension': transport['stateDimension'] == 24,\n"
            "    'cosmology_success': cosmology['verdict'] == 'SUCCESS',\n"
            "    'cosmology_dimension': cosmology['stateDimension'] == 18,\n"
            "    'dataset_counts': len(transport_rows) == 41 and len(cosmology_rows) == 1201,\n"
            "}\n"
            "assert all(NOTEBOOK_CHECKS.values()), NOTEBOOK_CHECKS\n"
            "report_path = ROOT / 'artifacts/notebooks/jupyter-report.json'\n"
            "report_path.parent.mkdir(parents=True, exist_ok=True)\n"
            "report = {'schemaVersion': 1, 'checks': NOTEBOOK_CHECKS, "
            "'inputSha256': actual_hashes}\n"
            "report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\\n', encoding='utf-8')\n"
            "NOTEBOOK_CHECKS\n",
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "dirac": {
                "generatedBy": "scripts/build_jupyter_notebook.py",
                "inputSha256": input_hashes,
                "schemaVersion": 1,
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"cell_count={len(cells)}")
    print(f"code_cell_count={sum(cell['cell_type'] == 'code' for cell in cells)}")
    print(f"output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())