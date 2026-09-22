#!/usr/bin/env python3
"""Verify exact component data used by the Phase 7 refinement."""

from __future__ import annotations

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CLIFFORD_PATH = REPOSITORY_ROOT / "artifacts" / "exact" / "cl44-seed.json"
GEOMETRY_PATH = (
    REPOSITORY_ROOT / "artifacts" / "curved-spin-geometry" / "geometry.json"
)
DIMENSION = 16


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    right_columns = transpose(right)
    return [
        [
            sum(a * b for a, b in zip(row, column, strict=True))
            for column in right_columns
        ]
        for row in left
    ]


def add(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [a + b for a, b in zip(left_row, right_row, strict=True)]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def identity(sign: int = 1) -> list[list[int]]:
    return [
        [sign * int(row == column) for column in range(DIMENSION)]
        for row in range(DIMENSION)
    ]


def nonzero_rows(matrix: list[list[int]]) -> list[list[tuple[int, int]]]:
    return [
        [
            (column + 1, value)
            for column, value in enumerate(row)
            if value != 0
        ]
        for row in matrix
    ]


def main() -> int:
    clifford = json.loads(CLIFFORD_PATH.read_text(encoding="utf-8"))
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    gamma_time: list[list[int]] = clifford["generators"][4]
    charge: list[list[int]] = geometry["spinorBilinear"]["matrix"]

    gamma_rows = nonzero_rows(gamma_time)
    charge_rows = nonzero_rows(charge)
    checks = {
        "gammaRowsSignedPermutation": all(len(row) == 1 for row in gamma_rows),
        "chargeRowsSignedPermutation": all(len(row) == 1 for row in charge_rows),
        "gammaSquareMinusIdentity": multiply(gamma_time, gamma_time)
        == identity(-1),
        "chargeSymmetric": charge == transpose(charge),
        "chargeSquareIdentity": multiply(charge, charge) == identity(),
        "gammaChargeSkewAdjoint": add(
            multiply(transpose(gamma_time), charge),
            multiply(charge, gamma_time),
        )
        == [[0] * DIMENSION for _ in range(DIMENSION)],
    }

    for row, entries in enumerate(gamma_rows, start=1):
        print(f"gamma4_row_{row}={entries}")
    for row, entries in enumerate(charge_rows, start=1):
        print(f"charge_row_{row}={entries}")
    for name, passed in checks.items():
        print(f"check_{name}={str(passed).lower()}")
    failures = [name for name, passed in checks.items() if not passed]
    print(f"check_count={len(checks)}")
    print(f"failed_check_count={len(failures)}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())