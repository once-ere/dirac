#!/usr/bin/env python3
"""Check the generated dissertation PDF structure and deterministic replay."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


PAGE_PATTERN = re.compile(rb"/Type\s*/Page(?!s)\b")
MEDIA_BOX_PATTERN = re.compile(rb"/MediaBox\s*\[([^]]+)\]")
EXPECTED_PDF_SHA256 = "a2a6e366817cb17d4b4ba936a98f5e495a8ca9c0bc012540021bc548847073f3"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        default=Path("dissertation/dirac-triality.pdf"),
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--expected-pages", type=int, default=13)
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
        "canonicalHash": content_hash == EXPECTED_PDF_SHA256,
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
    report = verify_pdf(
        arguments.pdf.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        arguments.expected_pages,
        arguments.expected_width,
        arguments.expected_height,
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