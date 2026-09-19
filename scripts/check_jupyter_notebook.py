#!/usr/bin/env python3
"""Check the executed Dirac triality Jupyter notebook."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_CELL_COUNT = 10
EXPECTED_CODE_CELL_COUNT = 5


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notebook",
        type=Path,
        default=Path("notebooks/dirac_triality.executed.ipynb"),
    )
    parser.add_argument("--repeat", type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_notebook(notebook_path: Path, repeat_path: Path | None) -> dict[str, object]:
    repository_root = Path(__file__).resolve().parent.parent
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    cells = notebook.get("cells", [])
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    execution_counts = [cell.get("execution_count") for cell in code_cells]
    final_text = json.dumps(code_cells[-1].get("outputs", [])) if code_cells else ""
    report_path = repository_root / "artifacts" / "notebooks" / "jupyter-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    repeat_compared = repeat_path is not None
    repeat_equal = not repeat_compared or notebook_path.read_bytes() == repeat_path.read_bytes()
    checks = {
        "format": notebook.get("nbformat") == 4 and notebook.get("nbformat_minor") == 5,
        "cellCount": len(cells) == EXPECTED_CELL_COUNT,
        "codeCellCount": len(code_cells) == EXPECTED_CODE_CELL_COUNT,
        "fixedIds": len({cell.get("id") for cell in cells}) == len(cells),
        "executionCounts": execution_counts == list(range(1, EXPECTED_CODE_CELL_COUNT + 1)),
        "noErrors": errors == [],
        "finalChecksVisible": "NOTEBOOK_CHECKS" not in final_text and final_text.count("True") >= 6,
        "reportPresent": report_path.is_file(),
        "reportChecks": len(report.get("checks", {})) == 6
        and all(report.get("checks", {}).values()),
        "inputHashes": report.get("inputSha256")
        == notebook.get("metadata", {}).get("dirac", {}).get("inputSha256"),
        "repeatByteIdentity": repeat_equal,
    }
    return {
        "checks": checks,
        "measurements": {
            "cellCount": len(cells),
            "codeCellCount": len(code_cells),
            "notebookSha256": sha256_file(notebook_path),
            "repeatCompared": repeat_compared,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_notebook(
        arguments.notebook.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
    )
    failures = [name for name, passed in report["checks"].items() if not passed]
    for name, passed in report["checks"].items():
        print(f"check_{name}={str(passed).lower()}")
    for name, value in report["measurements"].items():
        print(f"measurement_{name}={value}")
    print(f"check_count={len(report['checks'])}")
    print(f"failed_check_count={len(failures)}")
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())