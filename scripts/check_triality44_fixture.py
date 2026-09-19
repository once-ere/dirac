#!/usr/bin/env python3
"""Independently verify the exact split-real triality JSON fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from check_cl44_fixture import (
    PRIME,
    flatten,
    identity_matrix,
    intertwiner_equations,
    matrix_add,
    matrix_multiply,
    matrix_scale,
    matrix_subtract,
    restrict_matrix,
    zero_matrix,
)
from check_split_octonion_fixture import product


EXPECTED_CHECK_COUNT = 24
RationalMatrix = list[list[Fraction]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/exact/triality44.json"),
    )
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    parser.add_argument(
        "--split-fixture",
        type=Path,
        default=Path("artifacts/exact/split-octonion.json"),
    )
    parser.add_argument("--clifford-package", type=Path, default=Path("wolfram/Cl44.wl"))
    parser.add_argument(
        "--split-package",
        type=Path,
        default=Path("wolfram/SplitOctonion.wl"),
    )
    parser.add_argument(
        "--triality-package",
        type=Path,
        default=Path("wolfram/Triality44.wl"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def decode_rationals(value: Any) -> Any:
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    ):
        return Fraction(value[0], value[1])
    if isinstance(value, list):
        return [decode_rationals(item) for item in value]
    raise TypeError(f"Unexpected rational encoding: {value!r}")


def modulo(value: int | Fraction, prime: int = PRIME) -> int:
    fraction = Fraction(value)
    return fraction.numerator * pow(fraction.denominator, -1, prime) % prime


def rank_rational_modulo(rows: list[list[int | Fraction]]) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for source_row in rows:
        row = {
            column: reduced
            for column, value in enumerate(source_row)
            if (reduced := modulo(value))
        }
        while row:
            pivot = min(row)
            pivot_row = pivots.get(pivot)
            if pivot_row is None:
                inverse = pow(row[pivot], -1, PRIME)
                pivots[pivot] = {
                    column: value * inverse % PRIME
                    for column, value in row.items()
                }
                break
            factor = row[pivot]
            for column, pivot_value in pivot_row.items():
                reduced = (row.get(column, 0) - factor * pivot_value) % PRIME
                if reduced:
                    row[column] = reduced
                else:
                    row.pop(column, None)
    return len(pivots)


def transpose(matrix: RationalMatrix) -> RationalMatrix:
    return [list(column) for column in zip(*matrix, strict=True)]


def linear_combination(coefficients: list[Fraction], matrices: list[RationalMatrix]) -> RationalMatrix:
    dimension = len(matrices[0])
    result = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for coefficient, matrix in zip(coefficients, matrices, strict=True):
        if coefficient:
            result = matrix_add(result, matrix_scale(coefficient, matrix))
    return result


def vector_generators(metric: RationalMatrix, pairs: list[list[int]]) -> list[RationalMatrix]:
    result: list[RationalMatrix] = []
    for left, right in pairs:
        matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for column in range(8):
                matrix[row][column] = (
                    int(row == left) * metric[right][column]
                    - int(row == right) * metric[left][column]
                )
        result.append(matrix)
    return result


def representation_generator(
    representation: list[RationalMatrix],
    pair_index: dict[tuple[int, int], int],
    left: int,
    right: int,
) -> RationalMatrix:
    if left == right:
        return [[Fraction(0) for _ in range(8)] for _ in range(8)]
    if left < right:
        return representation[pair_index[(left, right)]]
    return matrix_scale(-1, representation[pair_index[(right, left)]])


def representation_lie_relations(
    representation: list[RationalMatrix],
    metric: RationalMatrix,
    pairs: list[list[int]],
) -> bool:
    pair_index = {tuple(pair): index for index, pair in enumerate(pairs)}
    for left, right in pairs:
        for first, second in pairs:
            actual = matrix_subtract(
                matrix_multiply(
                    representation_generator(representation, pair_index, left, right),
                    representation_generator(representation, pair_index, first, second),
                ),
                matrix_multiply(
                    representation_generator(representation, pair_index, first, second),
                    representation_generator(representation, pair_index, left, right),
                ),
            )
            expected = matrix_add(
                matrix_subtract(
                    matrix_scale(
                        metric[right][first],
                        representation_generator(representation, pair_index, left, second),
                    ),
                    matrix_scale(
                        metric[left][first],
                        representation_generator(representation, pair_index, right, second),
                    ),
                ),
                matrix_subtract(
                    matrix_scale(
                        metric[left][second],
                        representation_generator(representation, pair_index, right, first),
                    ),
                    matrix_scale(
                        metric[right][second],
                        representation_generator(representation, pair_index, left, first),
                    ),
                ),
            )
            if actual != expected:
                return False
    return True


def matrix_power(matrix: RationalMatrix, exponent: int) -> RationalMatrix:
    result: RationalMatrix = [
        [Fraction(value) for value in row] for row in identity_matrix(len(matrix))
    ]
    for _ in range(exponent):
        result = matrix_multiply(result, matrix)
    return result


def precompose(
    representation: list[RationalMatrix],
    automorphism: RationalMatrix,
) -> list[RationalMatrix]:
    return [
        linear_combination(
            [automorphism[row][column] for row in range(28)],
            representation,
        )
        for column in range(28)
    ]


def conjugate_representation(representation: list[RationalMatrix]) -> list[RationalMatrix]:
    conjugation = [
        [Fraction(int(row == column) * (1 if row == 0 else -1)) for column in range(8)]
        for row in range(8)
    ]
    return [
        matrix_multiply(conjugation, matrix_multiply(matrix, conjugation))
        for matrix in representation
    ]


def product_vector_basis(tensor: list[list[list[int]]], vector: list[Fraction], basis_index: int) -> list[Fraction]:
    return [
        sum(vector[first] * tensor[first][basis_index][output] for first in range(8))
        for output in range(8)
    ]


def product_basis_vector(tensor: list[list[list[int]]], basis_index: int, vector: list[Fraction]) -> list[Fraction]:
    return [
        sum(vector[second] * tensor[basis_index][second][output] for second in range(8))
        for output in range(8)
    ]


def intertwiner_dimension(
    left: list[RationalMatrix],
    right: list[RationalMatrix],
) -> int:
    dimension = len(left[0])
    return dimension * dimension - rank_rational_modulo(
        intertwiner_equations(left, right)
    )


def matrix_tuple(matrix: RationalMatrix) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(row) for row in matrix)


def verify_fixture(
    fixture_path: Path,
    clifford_fixture_path: Path,
    split_fixture_path: Path,
    package_paths: dict[str, Path],
) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    clifford_fixture = json.loads(clifford_fixture_path.read_text(encoding="utf-8"))
    split_fixture = json.loads(split_fixture_path.read_text(encoding="utf-8"))
    coefficients: list[list[Fraction]] = decode_rationals(
        fixture["coefficientBasisRationals"]
    )
    representations: list[list[RationalMatrix]] = decode_rationals(
        fixture["representationsRationals"]
    )
    cyclic: RationalMatrix = decode_rationals(
        fixture["cyclicAutomorphismRationals"]
    )
    reflection: RationalMatrix = decode_rationals(
        fixture["reflectionAutomorphismRationals"]
    )
    metric: RationalMatrix = [
        [Fraction(value) for value in row] for row in split_fixture["metric"]
    ]
    para_tensor = split_fixture["paraMultiplicationTensor"]
    pairs: list[list[int]] = fixture["liePairsZeroBased"]
    so_basis = vector_generators(metric, pairs)
    reconstructed_representations = [
        [
            linear_combination(row[block * 28 : (block + 1) * 28], so_basis)
            for row in coefficients
        ]
        for block in range(3)
    ]
    basis = identity_matrix(8)

    defining_relation = all(
        matrix_multiply(
            representations[0][triple],
            [[value] for value in para_tensor[left][right]],
        )
        == matrix_add(
            [[value] for value in product_vector_basis(
                para_tensor,
                [representations[1][triple][row][left] for row in range(8)],
                right,
            )],
            [[value] for value in product_basis_vector(
                para_tensor,
                left,
                [representations[2][triple][row][right] for row in range(8)],
            )],
        )
        for triple in range(28)
        for left in range(8)
        for right in range(8)
    )
    metric_skew = all(
        matrix_add(
            matrix_multiply(transpose(matrix), metric),
            matrix_multiply(metric, matrix),
        )
        == zero_matrix(8, 8)
        for representation in representations
        for matrix in representation
    )
    invariant_trilinear = all(
        sum(
            product_vector_basis(
                para_tensor,
                [representations[1][triple][row][left] for row in range(8)],
                right,
            )[output]
            * metric[output][third]
            for output in range(8)
        )
        + sum(
            product_basis_vector(
                para_tensor,
                left,
                [representations[2][triple][row][right] for row in range(8)],
            )[output]
            * metric[output][third]
            for output in range(8)
        )
        + sum(
            para_tensor[left][right][output]
            * metric[output][row]
            * representations[0][triple][row][third]
            for output in range(8)
            for row in range(8)
        )
        == 0
        for triple in range(28)
        for left in range(8)
        for right in range(8)
        for third in range(8)
    )

    identity28: RationalMatrix = [
        [Fraction(value) for value in row] for row in identity_matrix(28)
    ]
    s3_elements = {
        matrix_tuple(identity28),
        matrix_tuple(cyclic),
        matrix_tuple(matrix_power(cyclic, 2)),
        matrix_tuple(reflection),
        matrix_tuple(matrix_multiply(reflection, cyclic)),
        matrix_tuple(matrix_multiply(reflection, matrix_power(cyclic, 2))),
    }
    commutants = [intertwiner_dimension(rep, rep) for rep in representations]
    cross_intertwiners = [
        intertwiner_dimension(representations[0], representations[1]),
        intertwiner_dimension(representations[0], representations[2]),
        intertwiner_dimension(representations[1], representations[2]),
    ]

    octonion_generators = fixture["octonionCliffordGenerators"]
    canonical_generators = clifford_fixture["generators"]
    clifford_intertwiner = fixture["canonicalCliffordIntertwiner"]
    clifford_relations = all(
        matrix_add(
            matrix_multiply(octonion_generators[left], octonion_generators[right]),
            matrix_multiply(octonion_generators[right], octonion_generators[left]),
        )
        == matrix_scale(2 * int(metric[left][right]), identity_matrix(16))
        for left in range(8)
        for right in range(8)
    )
    clifford_intertwiner_ok = rank_rational_modulo(clifford_intertwiner) == 16 and all(
        matrix_multiply(canonical, clifford_intertwiner)
        == matrix_multiply(clifford_intertwiner, octonion)
        for canonical, octonion in zip(
            canonical_generators,
            octonion_generators,
            strict=True,
        )
    )
    canonical_spin = [
        matrix_scale(
            Fraction(1, 2),
            matrix_multiply(canonical_generators[left], canonical_generators[right]),
        )
        for left, right in pairs
    ]
    plus_indices = clifford_fixture["halfSpinIndicesZeroBased"]["Plus"]
    minus_indices = clifford_fixture["halfSpinIndicesZeroBased"]["Minus"]
    canonical_plus = [restrict_matrix(matrix, plus_indices) for matrix in canonical_spin]
    canonical_minus = [restrict_matrix(matrix, minus_indices) for matrix in canonical_spin]
    half_matching = [
        [
            intertwiner_dimension(representations[1], canonical_plus),
            intertwiner_dimension(representations[1], canonical_minus),
        ],
        [
            intertwiner_dimension(representations[2], canonical_plus),
            intertwiner_dimension(representations[2], canonical_minus),
        ],
    ]

    package_hashes = fixture["packageSha256"]
    checks = {
        "schemaVersion": fixture.get("schemaVersion") == 1,
        "packageHashes": all(
            package_hashes[name] == sha256_file(path)
            for name, path in package_paths.items()
        ),
        "signature": fixture.get("signature") == [4, 4],
        "pairLabels": pairs
        == [[left, right] for left in range(8) for right in range(left + 1, 8)],
        "coefficientShape": len(coefficients) == 28
        and all(len(row) == 84 for row in coefficients),
        "canonicalVectorProjection": [row[:28] for row in coefficients]
        == [[Fraction(value) for value in row] for row in identity_matrix(28)],
        "representationReconstruction": representations == reconstructed_representations,
        "projectionRanks": [
            rank_rational_modulo([row[block * 28 : (block + 1) * 28] for row in coefficients])
            for block in range(3)
        ]
        == [28, 28, 28],
        "metricSkew": metric_skew,
        "definingRelation": defining_relation,
        "lieRelations": all(
            representation_lie_relations(rep, metric, pairs) for rep in representations
        ),
        "invariantTrilinear": invariant_trilinear,
        "representationCommutants": commutants == [1, 1, 1],
        "representationInequivalence": cross_intertwiners == [0, 0, 0],
        "cyclicOrderThree": matrix_power(cyclic, 3) == identity28,
        "reflectionOrderTwo": matrix_power(reflection, 2) == identity28,
        "s3BraidRelation": matrix_multiply(
            reflection,
            matrix_multiply(cyclic, reflection),
        )
        == matrix_power(cyclic, 2),
        "s3ElementCount": len(s3_elements) == 6,
        "cyclicPermutesRepresentations": precompose(representations[0], cyclic)
        == representations[1]
        and precompose(representations[1], cyclic) == representations[2]
        and precompose(representations[2], cyclic) == representations[0],
        "reflectionConjugateSwap": precompose(representations[0], reflection)
        == conjugate_representation(representations[0])
        and precompose(representations[1], reflection)
        == conjugate_representation(representations[2])
        and precompose(representations[2], reflection)
        == conjugate_representation(representations[1]),
        "octonionCliffordRelations": clifford_relations,
        "cliffordIntertwiner": clifford_intertwiner_ok,
        "canonicalHalfSpinMatching": half_matching == [[1, 0], [0, 1]],
        "wolframChecks": len(fixture["checks"]) == 25
        and all(fixture["checks"].values()),
    }
    return {
        "checks": checks,
        "measurements": {
            "projectionRanksModuloPrime": [
                rank_rational_modulo(
                    [row[block * 28 : (block + 1) * 28] for row in coefficients]
                )
                for block in range(3)
            ],
            "representationCommutantDimensionsModuloPrime": commutants,
            "representationIntertwinerDimensionsModuloPrime": cross_intertwiners,
            "s3ElementCount": len(s3_elements),
            "cliffordIntertwinerRankModuloPrime": rank_rational_modulo(
                clifford_intertwiner
            ),
            "canonicalHalfSpinMatchingDimensionsModuloPrime": half_matching,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    package_paths = {
        "cl44": arguments.clifford_package.resolve(),
        "splitOctonion": arguments.split_package.resolve(),
        "triality44": arguments.triality_package.resolve(),
    }
    report = verify_fixture(
        arguments.fixture.resolve(),
        arguments.clifford_fixture.resolve(),
        arguments.split_fixture.resolve(),
        package_paths,
    )
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