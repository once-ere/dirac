#!/usr/bin/env python3
"""Independently verify the exact-real Cl(4,4) JSON fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PRIME = 1_000_003
EXPECTED_CHECK_COUNT = 24
Matrix = list[list[int]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=Path("wolfram/Cl44.wl"),
    )
    return parser.parse_args()


def identity_matrix(dimension: int) -> Matrix:
    return [
        [int(row == column) for column in range(dimension)]
        for row in range(dimension)
    ]


def zero_matrix(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def matrix_subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def matrix_scale(scale: int, matrix: Matrix) -> Matrix:
    return [[scale * value for value in row] for row in matrix]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    columns = list(zip(*right, strict=True))
    return [
        [sum(a * b for a, b in zip(row, column, strict=True)) for column in columns]
        for row in left
    ]


def flatten(matrix: Matrix) -> list[int]:
    return [value for row in matrix for value in row]


def restrict_matrix(matrix: Matrix, indices: list[int]) -> Matrix:
    return [[matrix[row][column] for column in indices] for row in indices]


def rank_modulo(rows: list[list[int]], prime: int = PRIME) -> int:
    matrix = [[value % prime for value in row] for row in rows]
    row_count = len(matrix)
    column_count = len(matrix[0]) if matrix else 0
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, prime)
        matrix[rank][column:] = [
            value * inverse % prime for value in matrix[rank][column:]
        ]
        pivot_row = matrix[rank]
        for row in range(rank + 1, row_count):
            factor = matrix[row][column]
            if factor:
                matrix[row][column:] = [
                    (value - factor * pivot_value) % prime
                    for value, pivot_value in zip(
                        matrix[row][column:],
                        pivot_row[column:],
                        strict=True,
                    )
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def ordered_monomials(generators: list[Matrix]) -> list[tuple[int, Matrix]]:
    dimension = len(generators[0])
    result: list[tuple[int, Matrix]] = []
    for mask in range(1 << len(generators)):
        matrix = identity_matrix(dimension)
        for index, generator in enumerate(generators):
            if mask & (1 << index):
                matrix = matrix_multiply(matrix, generator)
        result.append((mask, matrix))
    return result


def bivector(generators: list[Matrix], left: int, right: int) -> Matrix:
    if left == right:
        return zero_matrix(len(generators[0]), len(generators[0]))
    return matrix_multiply(generators[left], generators[right])


def intertwiner_equations(left: list[Matrix], right: list[Matrix]) -> list[list[int]]:
    dimension = len(left[0])
    equations: list[list[int]] = []
    for left_generator, right_generator in zip(left, right, strict=True):
        for row in range(dimension):
            for column in range(dimension):
                equation = [0] * (dimension * dimension)
                for inner in range(dimension):
                    equation[inner * dimension + column] += left_generator[row][inner]
                    equation[row * dimension + inner] -= right_generator[inner][column]
                equations.append(equation)
    return equations


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_fixture(fixture_path: Path, package_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    generators: list[Matrix] = fixture["generators"]
    metric: Matrix = fixture["metric"]
    dimension = 16
    identity = identity_matrix(dimension)
    zero = zero_matrix(dimension, dimension)
    plus_indices: list[int] = fixture["halfSpinIndicesZeroBased"]["Plus"]
    minus_indices: list[int] = fixture["halfSpinIndicesZeroBased"]["Minus"]

    monomials = ordered_monomials(generators)
    even_monomials = [
        matrix for mask, matrix in monomials if mask.bit_count() % 2 == 0
    ]
    volume = identity
    for generator in generators:
        volume = matrix_multiply(volume, generator)

    expected_plus = [
        [(identity[row][column] + volume[row][column]) // 2 for column in range(dimension)]
        for row in range(dimension)
    ]
    expected_minus = [
        [(identity[row][column] - volume[row][column]) // 2 for column in range(dimension)]
        for row in range(dimension)
    ]

    spin_pairs = [
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
    ]
    spin_matrices = [bivector(generators, *pair) for pair in spin_pairs]
    plus_spin = [restrict_matrix(matrix, plus_indices) for matrix in spin_matrices]
    minus_spin = [restrict_matrix(matrix, minus_indices) for matrix in spin_matrices]
    plus_even = [restrict_matrix(matrix, plus_indices) for matrix in even_monomials]
    minus_even = [restrict_matrix(matrix, minus_indices) for matrix in even_monomials]

    clifford_relations = all(
        matrix_add(
            matrix_multiply(generators[left], generators[right]),
            matrix_multiply(generators[right], generators[left]),
        )
        == matrix_scale(2 * metric[left][right], identity)
        for left in range(8)
        for right in range(8)
    )
    spin_vector_relations = all(
        matrix_subtract(
            matrix_multiply(bivector(generators, left, right), generators[index]),
            matrix_multiply(generators[index], bivector(generators, left, right)),
        )
        == matrix_scale(
            2,
            matrix_subtract(
                matrix_scale(metric[right][index], generators[left]),
                matrix_scale(metric[left][index], generators[right]),
            ),
        )
        for left, right in spin_pairs
        for index in range(8)
    )
    spin_lie_relations = all(
        matrix_subtract(
            matrix_multiply(bivector(generators, left, right), bivector(generators, first, second)),
            matrix_multiply(bivector(generators, first, second), bivector(generators, left, right)),
        )
        == matrix_scale(
            2,
            matrix_add(
                matrix_subtract(
                    matrix_scale(metric[right][first], bivector(generators, left, second)),
                    matrix_scale(metric[left][first], bivector(generators, right, second)),
                ),
                matrix_subtract(
                    matrix_scale(metric[left][second], bivector(generators, right, first)),
                    matrix_scale(metric[right][second], bivector(generators, left, first)),
                ),
            ),
        )
        for left, right in spin_pairs
        for first, second in spin_pairs
    )

    full_rank = rank_modulo([flatten(matrix) for _, matrix in monomials])
    even_rank = rank_modulo([flatten(matrix) for matrix in even_monomials])
    plus_even_rank = rank_modulo([flatten(matrix) for matrix in plus_even])
    minus_even_rank = rank_modulo([flatten(matrix) for matrix in minus_even])
    plus_commutant = 64 - rank_modulo(intertwiner_equations(plus_spin, plus_spin))
    minus_commutant = 64 - rank_modulo(intertwiner_equations(minus_spin, minus_spin))
    cross_intertwiner = 64 - rank_modulo(intertwiner_equations(plus_spin, minus_spin))

    checks = {
        "schemaVersion": fixture.get("schemaVersion") == 1,
        "packageHash": fixture.get("packageSha256") == sha256_file(package_path),
        "signature": fixture.get("signature") == [4, 4],
        "generatorCount": len(generators) == 8,
        "generatorDimensions": all(
            len(matrix) == dimension and all(len(row) == dimension for row in matrix)
            for matrix in generators
        ),
        "integerEntries": all(
            isinstance(value, int) for matrix in generators for row in matrix for value in row
        ),
        "metric": metric == [
            [int(row == column) * (1 if row < 4 else -1) for column in range(8)]
            for row in range(8)
        ],
        "cliffordRelations": clifford_relations,
        "volumeElement": volume == fixture["volumeElement"],
        "volumeSquare": matrix_multiply(volume, volume) == identity,
        "volumeOddAnticommutation": all(
            matrix_add(matrix_multiply(volume, generator), matrix_multiply(generator, volume)) == zero
            for generator in generators
        ),
        "projectorMatrices": fixture["projectors"]["Plus"] == expected_plus
        and fixture["projectors"]["Minus"] == expected_minus,
        "projectorIdentities": matrix_multiply(expected_plus, expected_plus) == expected_plus
        and matrix_multiply(expected_minus, expected_minus) == expected_minus
        and matrix_multiply(expected_plus, expected_minus) == zero,
        "halfSpinIndices": plus_indices == [index for index in range(dimension) if volume[index][index] == 1]
        and minus_indices == [index for index in range(dimension) if volume[index][index] == -1],
        "oddExchangesHalfSpin": all(
            restrict_matrix(generator, plus_indices) == zero_matrix(8, 8)
            and restrict_matrix(generator, minus_indices) == zero_matrix(8, 8)
            for generator in generators
        ),
        "spinPreservesHalfSpin": all(
            all(matrix[row][column] == 0 for row in plus_indices for column in minus_indices)
            and all(matrix[row][column] == 0 for row in minus_indices for column in plus_indices)
            for matrix in spin_matrices
        ),
        "spinVectorRelations": spin_vector_relations,
        "spinLieRelations": spin_lie_relations,
        "fullAlgebraRank": full_rank == 256,
        "evenAlgebraRank": even_rank == 128,
        "halfSpinActionRanks": plus_even_rank == 64 and minus_even_rank == 64,
        "plusSpinCommutant": plus_commutant == 1,
        "minusSpinCommutant": minus_commutant == 1,
        "halfSpinInequivalence": cross_intertwiner == 0,
    }
    return {
        "checks": checks,
        "measurements": {
            "fullAlgebraRankModuloPrime": full_rank,
            "evenAlgebraRankModuloPrime": even_rank,
            "plusEvenActionRankModuloPrime": plus_even_rank,
            "minusEvenActionRankModuloPrime": minus_even_rank,
            "plusSpinCommutantDimensionModuloPrime": plus_commutant,
            "minusSpinCommutantDimensionModuloPrime": minus_commutant,
            "halfSpinIntertwinerDimensionModuloPrime": cross_intertwiner,
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