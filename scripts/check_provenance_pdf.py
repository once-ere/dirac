#!/usr/bin/env python3
"""Check deterministic curved-geometry provenance PDFs."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts import check_dissertation_pdf
except ModuleNotFoundError:
    import check_dissertation_pdf


SPECIFICATIONS = {
    "developer-summary": {
        "path": Path("DEVELOPER_SUMMARY.pdf"),
        "pages": 27,
        "sha256": (
            "f4de8214b1b6f03f4bd91874d1cc56d609fee348df15962a6d99d6c68e2f8836"
        ),
    },
    "curved-spin-bundle": {
        "path": Path("provenance/CURVED_SPIN_BUNDLE.pdf"),
        "pages": 16,
        "sha256": (
            "588a83a2a5d7f66c5c11f0aeb682f3b32f3e314f9ea73cc16876790bb3a257be"
        ),
    },
    "einstein-spinor-44": {
        "path": Path("provenance/EINSTEIN_SPINOR_44.pdf"),
        "pages": 21,
        "sha256": (
            "3bb9fb215135852f4f2f8f444686de69665ee28ea5198705104d2b46c4801251"
        ),
    },
    "weitzenbock-spinor-44": {
        "path": Path("provenance/WEITZENBOCK_SPINOR_44.pdf"),
        "pages": 19,
        "sha256": (
            "7d14521cf34debb25d277e4db75d3b47bce55ad24ddd30b2b56d65bc9dfa7cd6"
        ),
    },
    "einstein-spinor-44-components-x0-x7": {
        "path": Path("provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf"),
        "pages": 8,
        "sha256": (
            "f64e3f8420c18c3886e201c64ee41d8e0564d7222038f5a8b83f45a46b7113f4"
        ),
    },
    "einstein-spinor-44-numerics-x0-x7": {
        "path": Path("provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf"),
        "pages": 8,
        "sha256": (
            "8501d992709282039b5a69d1de045660018505f1048f09fecfedc40795484af9"
        ),
    },
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--edition", choices=sorted(SPECIFICATIONS), required=True
    )
    parser.add_argument("pdf", nargs="?", type=Path)
    parser.add_argument("--repeat", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    specification = SPECIFICATIONS[arguments.edition]
    report = check_dissertation_pdf.verify_pdf(
        (arguments.pdf or specification["path"]).resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        specification["pages"],
        612.0,
        792.0,
        specification["sha256"],
    )
    failures = [
        name for name, passed in report["checks"].items() if not passed
    ]
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
