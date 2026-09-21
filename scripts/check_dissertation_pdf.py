#!/usr/bin/env python3
"""Check the generated dissertation PDF structure and deterministic replay."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


PAGE_PATTERN = re.compile(rb"/Type\s*/Page(?!s)\b")
MEDIA_BOX_PATTERN = re.compile(rb"/MediaBox\s*\[([^]]+)\]")
ORIGINAL_PDF_SHA256 = (
    "8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e"
)
LEARN_PDF_SHA256 = (
    "7c683b51445a3b4964b244ea3e232bc0ba3f745b5427308b59a80d1532e19ff9"
)
EXPECTED_PDF_SHA256 = ORIGINAL_PDF_SHA256
PDF_SPECIFICATIONS = {
    "original": {
        "path": Path("dissertation/dirac-triality.pdf"),
        "pages": 19,
        "sha256": ORIGINAL_PDF_SHA256,
    },
    "learn": {
        "path": Path("dissertation/Learn_dirac-triality.pdf"),
        "pages": 74,
        "sha256": LEARN_PDF_SHA256,
    },
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--edition",
        choices=sorted(PDF_SPECIFICATIONS),
        default="original",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-width", type=float, default=612.0)
    parser.add_argument("--expected-height", type=float, default=792.0)
    return parser.parse_args()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def parse_media_boxes(content: bytes) -> list[tuple[float, ...]]:
    boxes: set[tuple[float, ...]] = set()
    for match in MEDIA_BOX_PATTERN.finditer(content):
        try:
            boxes.add(tuple(float(value) for value in match.group(1).split()))
        except ValueError:
            continue
    return sorted(boxes)


def verify_pdf(
    pdf_path: Path,
    repeat_path: Path | None,
    expected_pages: int,
    expected_width: float,
    expected_height: float,
    expected_sha256: str = ORIGINAL_PDF_SHA256,
) -> dict[str, object]:
    content = pdf_path.read_bytes()
    content_hash = sha256_bytes(content)
    page_count = len(PAGE_PATTERN.findall(content))
    media_boxes = parse_media_boxes(content)
    expected_box = (0.0, 0.0, expected_width, expected_height)
    repeat_compared = repeat_path is not None
    repeat_equal = not repeat_compared or content == repeat_path.read_bytes()
    checks = {
        "header": content.startswith(b"%PDF-"),
        "endMarker": content.rstrip().endswith(b"%%EOF"),
        "pageCount": page_count == expected_pages,
        "mediaBox": media_boxes == [expected_box],
        "canonicalHash": content_hash == expected_sha256,
        "repeatByteIdentity": repeat_equal,
    }
    return {
        "checks": checks,
        "measurements": {
            "byteCount": len(content),
            "pageCount": page_count,
            "mediaBoxes": media_boxes,
            "pdfSha256": content_hash,
            "repeatCompared": repeat_compared,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    specification = PDF_SPECIFICATIONS[arguments.edition]
    pdf_path = arguments.pdf or specification["path"]
    expected_pages = arguments.expected_pages or specification["pages"]
    expected_sha256 = arguments.expected_sha256 or specification["sha256"]
    report = verify_pdf(
        pdf_path.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        expected_pages,
        arguments.expected_width,
        arguments.expected_height,
        expected_sha256,
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
