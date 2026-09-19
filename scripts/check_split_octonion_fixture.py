#!/usr/bin/env python3
"""Independently verify the exact split-octonion JSON fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from check_cl44_fixture import (
    Matrix,
    flatten,
    identity_matrix,
    matrix_add,
    matrix_multiply,
    matrix_scale,
    matrix_subtract,
    rank_modulo,
    zero_matrix,
)


EXPECTED_CHECK_COUNT = 17
Vector = list[int]
Tensor = list[list[Vector]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/exact/split-octonion.json"),
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=Path("wolfram/SplitOctonion.wl"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def vector_add(left: Vector, right: Vector) -> Vector:
    return [a + b for a, b in zip(left, right, strict=True)]


def vector_subtract(left: Vector, right: Vector) -> Vector:
    return [a - b for a, b in zip(left, right, strict=True)]


def vector_scale(scale: int, vector: Vector) -> Vector:
    return [scale * value for value in vector]


def dot3(left: Vector, right: Vector) -> int:
    return sum(a * b for a, b in zip(left, right, strict=True))


def cross3(left: Vector, right: Vector) -> Vector:
    return [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]


def to_zorn(vector: Vector) -> tuple[int, Vector, Vector, int]:
    positive = vector[1:4]
    negative = vector[5:8]
    return (
        vector[0] + vector[4],
        vector_add(positive, negative),
        vector_subtract(negative, positive),
        vector[0] - vector[4],
    )


def from_zorn(value: tuple[int, Vector, Vector, int]) -> Vector:
    upper_left, upper_right, lower_left, lower_right = value
    numerators = [
        upper_left + lower_right,
        *vector_subtract(upper_right, lower_left),
        upper_left - lower_right,
        *vector_add(upper_right, lower_left),
    ]
    if any(numerator % 2 for numerator in numerators):
        raise ValueError("Zorn basis conversion produced a nonintegral coordinate")
    return [numerator // 2 for numerator in numerators]


def zorn_product(left: Vector, right: Vector) -> Vector:
    a, upper, lower, b = to_zorn(left)
    c, other_upper, other_lower, d = to_zorn(right)
    return from_zorn(
        (
            a * c + dot3(upper, other_lower),
            vector_subtract(
                vector_add(vector_scale(a, other_upper), vector_scale(d, upper)),
                cross3(lower, other_lower),
            ),
            vector_add(
                vector_add(vector_scale(c, lower), vector_scale(b, other_lower)),
                cross3(upper, other_upper),
            ),
            dot3(lower, other_upper) + b * d,
        )
    )


def conjugate(vector: Vector) -> Vector:
    return [vector[0], *[-value for value in vector[1:]]]


def product(tensor: Tensor, left: Vector, right: Vector) -> Vector:
    return [
        sum(
            left[first] * right[second] * tensor[first][second][output]
            for first in range(8)
            for second in range(8)
        )
        for output in range(8)
    ]


def associator(tensor: Tensor, left: Vector, middle: Vector, right: Vector) -> Vector:
    return vector_subtract(
        product(tensor, product(tensor, left, middle), right),
        product(tensor, left, product(tensor, middle, right)),
    )


def multiplication_matrices(tensor: Tensor) -> tuple[list[Matrix], list[Matrix]]:
    basis = identity_matrix(8)
    left = [
        [
            [product(tensor, basis[index], basis[column])[row] for column in range(8)]
            for row in range(8)
        ]
        for index in range(8)
    ]
    right = [
        [
            [product(tensor, basis[column], basis[index])[row] for column in range(8)]
            for row in range(8)
        ]
        for index in range(8)
    ]
    return left, right


def tensor_mode_ranks(tensor: Tensor) -> list[int]:
    first = [flatten(tensor[index]) for index in range(8)]
    second = [
        [tensor[left][index][output] for left in range(8) for output in range(8)]
        for index in range(8)
    ]
    third = [
        [tensor[left][right][index] for left in range(8) for right in range(8)]
        for index in range(8)
    ]
    return [rank_modulo(first), rank_modulo(second), rank_modulo(third)]


def verify_fixture(fixture_path: Path, package_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    tensor: Tensor = fixture["multiplicationTensor"]
    para_tensor: Tensor = fixture["paraMultiplicationTensor"]
    metric: Matrix = fixture["metric"]
    basis = identity_matrix(8)
    unit = basis[0]
    zero_vector = [0] * 8
    expected_metric = [
        [int(row == column) * (1 if row < 4 else -1) for column in range(8)]
        for row in range(8)
    ]
    expected_tensor = [
        [zorn_product(basis[left], basis[right]) for right in range(8)]
        for left in range(8)
    ]
    expected_para_tensor = [
        [zorn_product(conjugate(basis[left]), conjugate(basis[right])) for right in range(8)]
        for left in range(8)
    ]
    left_matrices, right_matrices = multiplication_matrices(tensor)

    left_polarization = all(
        matrix_add(
            matrix_multiply(
                [list(column) for column in zip(*left_matrices[left], strict=True)],
                matrix_multiply(metric, left_matrices[right]),
            ),
            matrix_multiply(
                [list(column) for column in zip(*left_matrices[right], strict=True)],
                matrix_multiply(metric, left_matrices[left]),
            ),
        )
        == matrix_scale(2 * metric[left][right], metric)
        for left in range(8)
        for right in range(8)
    )
    right_polarization = all(
        matrix_add(
            matrix_multiply(
                [list(column) for column in zip(*right_matrices[left], strict=True)],
                matrix_multiply(metric, right_matrices[right]),
            ),
            matrix_multiply(
                [list(column) for column in zip(*right_matrices[right], strict=True)],
                matrix_multiply(metric, right_matrices[left]),
            ),
        )
        == matrix_scale(2 * metric[left][right], metric)
        for left in range(8)
        for right in range(8)
    )
    alternativity = all(
        vector_add(
            associator(tensor, basis[first], basis[second], basis[third]),
            associator(tensor, basis[second], basis[first], basis[third]),
        )
        == zero_vector
        and vector_add(
            associator(tensor, basis[first], basis[second], basis[third]),
            associator(tensor, basis[first], basis[third], basis[second]),
        )
        == zero_vector
        for first in range(8)
        for second in range(8)
        for third in range(8)
    )
    para_cyclic = all(
        sum(
            product(para_tensor, basis[first], basis[second])[index]
            * metric[index][third]
            for index in range(8)
        )
        == sum(
            product(para_tensor, basis[second], basis[third])[index]
            * metric[index][first]
            for index in range(8)
        )
        for first in range(8)
        for second in range(8)
        for third in range(8)
    )

    checks = {
        "schemaVersion": fixture.get("schemaVersion") == 1,
        "packageHash": fixture.get("packageSha256") == sha256_file(package_path),
        "signature": fixture.get("signature") == [4, 4],
        "tensorDimensions": len(tensor) == 8
        and all(len(row) == 8 for row in tensor)
        and all(len(vector) == 8 for row in tensor for vector in row),
        "integerStructureConstants": all(
            isinstance(value, int) for row in tensor for vector in row for value in vector
        ),
        "metric": metric == expected_metric,
        "zornReconstruction": tensor == expected_tensor,
        "unit": all(
            product(tensor, unit, vector) == vector
            and product(tensor, vector, unit) == vector
            for vector in basis
        ),
        "conjugationReversal": all(
            conjugate(product(tensor, left, right))
            == product(tensor, conjugate(right), conjugate(left))
            for left in basis
            for right in basis
        ),
        "quadraticPolarization": all(
            vector_add(
                product(tensor, left, conjugate(right)),
                product(tensor, right, conjugate(left)),
            )
            == vector_scale(2 * metric[index][other], unit)
            for index, left in enumerate(basis)
            for other, right in enumerate(basis)
        ),
        "leftCompositionPolarization": left_polarization,
        "rightCompositionPolarization": right_polarization,
        "alternativity": alternativity,
        "paraTensor": para_tensor == expected_para_tensor,
        "paraTrilinearCyclic": para_cyclic,
        "ordinaryTensorModeRanks": tensor_mode_ranks(tensor) == [8, 8, 8],
        "paraTensorModeRanks": tensor_mode_ranks(para_tensor) == [8, 8, 8],
    }
    return {
        "checks": checks,
        "measurements": {
            "nonzeroOrdinaryStructureConstants": sum(
                value != 0 for row in tensor for vector in row for value in vector
            ),
            "nonzeroParaStructureConstants": sum(
                value != 0 for row in para_tensor for vector in row for value in vector
            ),
            "ordinaryTensorModeRanks": tensor_mode_ranks(tensor),
            "paraTensorModeRanks": tensor_mode_ranks(para_tensor),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_fixture(arguments.fixture.resolve(), arguments.package.resolve())
    checks = report["checks"]
    failures = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"check_{name}={str(passed).lower()}")
    for name, value in report["measurements"].items():
        print(f"measurement_{name}={value}")
    print(f"check_count={len(checks)}")
    print(f"failed_check_count={len(failures)}")
    if len(checks) != EXPECTED_CHECK_COUNT:
        print(f"ERROR: expected {EXPECTED_CHECK_COUNT} checks")
        return 1
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())