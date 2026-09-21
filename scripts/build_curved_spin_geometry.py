#!/usr/bin/env python3
"""Build the exact curved Spin(4,4) geometry fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


DIMENSION = 8
SPINOR_DIMENSION = 16
TIME_INDEX = 4
TRANSVERSE_INDICES = [0, 1, 2, 3, 5, 6, 7]
Matrix = list[list[Fraction]]
Tensor3 = list[list[list[Fraction]]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/curved-spin-geometry/geometry.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(dimension: int) -> Matrix:
    return [
        [Fraction(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    return [
        [
            sum(
                (a * b for a, b in zip(row, column, strict=True)),
                Fraction(0),
            )
            for column in columns
        ]
        for row in left
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row, strict=True)]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def scale(coefficient: Fraction, matrix: Matrix) -> Matrix:
    return [[coefficient * value for value in row] for row in matrix]


def diagonal(values: list[Fraction]) -> Matrix:
    return [
        [
            value if row == column else Fraction(0)
            for column in range(len(values))
        ]
        for row, value in enumerate(values)
    ]


def zero_tensor3() -> Tensor3:
    return [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]


def connection_data(
    metric_signs: list[int],
    scale_factor: Fraction,
    scale_derivative: Fraction,
) -> tuple[Matrix, Matrix, Tensor3, Tensor3]:
    frame_values = [
        Fraction(1) if index == TIME_INDEX else scale_factor
        for index in range(DIMENSION)
    ]
    frame = diagonal(frame_values)
    inverse_frame = diagonal([Fraction(1) / value for value in frame_values])
    metric = diagonal(
        [
            Fraction(metric_signs[index]) * frame_values[index] ** 2
            for index in range(DIMENSION)
        ]
    )
    inverse_metric = diagonal(
        [Fraction(1) / metric[index][index] for index in range(DIMENSION)]
    )
    metric_derivative = zero_tensor3()
    frame_derivative = zero_tensor3()
    for index in TRANSVERSE_INDICES:
        metric_derivative[TIME_INDEX][index][index] = (
            2 * metric_signs[index] * scale_factor * scale_derivative
        )
        frame_derivative[TIME_INDEX][index][index] = scale_derivative

    christoffel = zero_tensor3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                christoffel[rho][mu][nu] = sum(
                    (
                        inverse_metric[rho][sigma]
                        * (
                            metric_derivative[mu][nu][sigma]
                            + metric_derivative[nu][mu][sigma]
                            - metric_derivative[sigma][mu][nu]
                        )
                        / 2
                        for sigma in range(DIMENSION)
                    ),
                    Fraction(0),
                )

    spin_connection = zero_tensor3()
    for mu in range(DIMENSION):
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                raised = sum(
                    (
                        inverse_frame[tangent_b][nu]
                        * (
                            sum(
                                (
                                    christoffel[rho][mu][nu]
                                    * frame[rho][tangent_a]
                                    for rho in range(DIMENSION)
                                ),
                                Fraction(0),
                            )
                            - frame_derivative[mu][nu][tangent_a]
                        )
                        for nu in range(DIMENSION)
                    ),
                    Fraction(0),
                )
                spin_connection[mu][tangent_a][tangent_b] = (
                    metric_signs[tangent_a] * raised
                )
    return frame, inverse_frame, christoffel, spin_connection


def rank(matrix: Matrix) -> int:
    working = [row[:] for row in matrix]
    result = 0
    for column in range(len(working[0])):
        pivot = next(
            (
                row
                for row in range(result, len(working))
                if working[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        working[result], working[pivot] = working[pivot], working[result]
        divisor = working[result][column]
        working[result] = [value / divisor for value in working[result]]
        for row in range(len(working)):
            if row == result:
                continue
            factor = working[row][column]
            if factor:
                working[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(
                        working[row], working[result], strict=True
                    )
                ]
        result += 1
    return result


def expected_records(
    metric_signs: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    christoffel: list[dict[str, Any]] = []
    spin_connection: list[dict[str, Any]] = []
    for index in TRANSVERSE_INDICES:
        christoffel.extend(
            [
                {
                    "rho": TIME_INDEX,
                    "mu": index,
                    "nu": index,
                    "coefficient": f"{metric_signs[index]} a adot",
                },
                {
                    "rho": index,
                    "mu": TIME_INDEX,
                    "nu": index,
                    "coefficient": "H",
                },
                {
                    "rho": index,
                    "mu": index,
                    "nu": TIME_INDEX,
                    "coefficient": "H",
                },
            ]
        )
        spin_connection.extend(
            [
                {
                    "mu": index,
                    "a": index,
                    "b": TIME_INDEX,
                    "coefficient": f"{metric_signs[index]} adot",
                },
                {
                    "mu": index,
                    "a": TIME_INDEX,
                    "b": index,
                    "coefficient": f"{-metric_signs[index]} adot",
                },
            ]
        )
    return christoffel, spin_connection


def main() -> int:
    arguments = parse_arguments()
    fixture_path = arguments.clifford_fixture.resolve()
    output_path = arguments.output.resolve()
    clifford = json.loads(fixture_path.read_text(encoding="utf-8"))
    metric_signs = [
        row[index] for index, row in enumerate(clifford["metric"])
    ]
    generators = [
        [[Fraction(value) for value in row] for row in matrix]
        for matrix in clifford["generators"]
    ]
    volume = [
        [Fraction(value) for value in row]
        for row in clifford["volumeElement"]
    ]
    charge = identity(SPINOR_DIMENSION)
    for generator in generators[:4]:
        charge = multiply(charge, generator)

    sample_scale = Fraction(3, 2)
    sample_derivative = Fraction(2, 5)
    frame, inverse_frame, christoffel, spin_connection = connection_data(
        metric_signs,
        sample_scale,
        sample_derivative,
    )
    hubble = sample_derivative / sample_scale
    tangent_metric = diagonal([Fraction(value) for value in metric_signs])
    metric_relation = multiply(
        multiply(frame, tangent_metric), transpose(frame)
    )
    expected_metric = diagonal(
        [
            Fraction(metric_signs[index])
            * (Fraction(1) if index == TIME_INDEX else sample_scale**2)
            for index in range(DIMENSION)
        ]
    )

    vielbein_postulate = True
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            for tangent_a in range(DIMENSION):
                derivative = (
                    sample_derivative
                    if mu == TIME_INDEX
                    and nu == tangent_a
                    and nu in TRANSVERSE_INDICES
                    else Fraction(0)
                )
                christoffel_term = sum(
                    (
                        christoffel[rho][mu][nu] * frame[rho][tangent_a]
                        for rho in range(DIMENSION)
                    ),
                    Fraction(0),
                )
                connection_term = sum(
                    (
                        metric_signs[tangent_a]
                        * spin_connection[mu][tangent_a][tangent_b]
                        * frame[nu][tangent_b]
                        for tangent_b in range(DIMENSION)
                    ),
                    Fraction(0),
                )
                vielbein_postulate &= (
                    derivative - christoffel_term + connection_term == 0
                )

    zero_spinor = [
        [Fraction(0) for _ in range(SPINOR_DIMENSION)]
        for _ in range(SPINOR_DIMENSION)
    ]
    spin_matrices = []
    for mu in range(DIMENSION):
        omega_matrix = [row[:] for row in zero_spinor]
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                commutator = add(
                    multiply(generators[tangent_a], generators[tangent_b]),
                    scale(
                        Fraction(-1),
                        multiply(generators[tangent_b], generators[tangent_a]),
                    ),
                )
                omega_matrix = add(
                    omega_matrix,
                    scale(
                        spin_connection[mu][tangent_a][tangent_b] / 8,
                        commutator,
                    ),
                )
        spin_matrices.append(omega_matrix)
    slash_connection = [row[:] for row in zero_spinor]
    for mu in TRANSVERSE_INDICES:
        curved_gamma = scale(inverse_frame[mu][mu], generators[mu])
        slash_connection = add(
            slash_connection,
            multiply(curved_gamma, spin_matrices[mu]),
        )
    expected_slash = scale(Fraction(7, 2) * hubble, generators[TIME_INDEX])

    christoffel_records, spin_connection_records = expected_records(
        metric_signs
    )
    checks = {
        "signature": metric_signs == [1, 1, 1, 1, -1, -1, -1, -1],
        "metricFromFrame": metric_relation == expected_metric,
        "spinConnectionAntisymmetric": all(
            spin_connection[mu][a][b] == -spin_connection[mu][b][a]
            for mu in range(DIMENSION)
            for a in range(DIMENSION)
            for b in range(DIMENSION)
        ),
        "vielbeinPostulate": vielbein_postulate,
        "chargeSymmetric": charge == transpose(charge),
        "chargeInvolution": multiply(charge, charge)
        == identity(SPINOR_DIMENSION),
        "gammaChargeSkew": all(
            multiply(transpose(generator), charge)
            == scale(Fraction(-1), multiply(charge, generator))
            for generator in generators
        ),
        "chargeNondegenerate": rank(charge) == SPINOR_DIMENSION,
        "chargeSignature": sum(charge[index][index] for index in range(16))
        == 0,
        "slashConnection": slash_connection == expected_slash,
        "connectionPreservesChirality": all(
            multiply(matrix, volume) == multiply(volume, matrix)
            for matrix in spin_matrices
        ),
        "halfSpinIndices": clifford["halfSpinIndicesZeroBased"]
        == {
            "Plus": [
                index for index in range(16) if volume[index][index] == 1
            ],
            "Minus": [
                index for index in range(16) if volume[index][index] == -1
            ],
        },
    }
    document = {
        "schemaVersion": 1,
        "cliffordFixtureSha256": sha256_file(fixture_path),
        "baseDimension": DIMENSION,
        "signature": [4, 4],
        "coordinateOrder": [
            "x0",
            "x1",
            "x2",
            "x3",
            "t",
            "y1",
            "y2",
            "y3",
        ],
        "timeCoordinateIndexZeroBased": TIME_INDEX,
        "transverseIndicesZeroBased": TRANSVERSE_INDICES,
        "tangentMetric": clifford["metric"],
        "metricAnsatz": (
            "g=diag(a(t)^2,a(t)^2,a(t)^2,a(t)^2,-1,"
            "-a(t)^2,-a(t)^2,-a(t)^2)"
        ),
        "frameAnsatz": (
            "e_mu^a=diag(a(t),a(t),a(t),a(t),1,a(t),a(t),a(t))"
        ),
        "inverseFrameAnsatz": (
            "e_a^mu=diag(1/a(t),1/a(t),1/a(t),1/a(t),1,"
            "1/a(t),1/a(t),1/a(t))"
        ),
        "christoffelNonzero": christoffel_records,
        "spinConnectionNonzero": spin_connection_records,
        "spinConnectionFormula": (
            "omega_mu^a_b=e_b^nu(Gamma^rho_munu e_rho^a-"
            "partial_mu e_nu^a)"
        ),
        "spinorDerivativeConvention": (
            "D_mu=partial_mu+(1/8) omega_muab [gamma^a,gamma^b]"
        ),
        "homogeneousDiracOperator": "gamma^4(partial_t+(7/2)H)",
        "spinorBundle": {
            "structureGroup": "Spin(4,4)",
            "fiber": "Delta_R=Delta_plus direct-sum Delta_minus",
            "fiberDimension": SPINOR_DIMENSION,
            "halfSpinDimensions": [8, 8],
            "halfSpinIndicesZeroBased": clifford[
                "halfSpinIndicesZeroBased"
            ],
        },
        "spinorBilinear": {
            "definition": "C=gamma_1^+ gamma_2^+ gamma_3^+ gamma_4^+",
            "matrix": [[int(value) for value in row] for row in charge],
            "adjoint": "bar(psi)=psi^T C",
        },
        "sample": {
            "scaleFactor": [sample_scale.numerator, sample_scale.denominator],
            "scaleDerivative": [
                sample_derivative.numerator,
                sample_derivative.denominator,
            ],
            "hubble": [hubble.numerator, hubble.denominator],
        },
        "checks": checks,
        "measurements": {
            "nonzeroChristoffelComponents": 3 * len(TRANSVERSE_INDICES),
            "nonzeroLoweredSpinConnectionComponents": (
                2 * len(TRANSVERSE_INDICES)
            ),
            "spinorDimension": SPINOR_DIMENSION,
            "chargeRank": rank(charge),
            "chargeSignature": [8, 8],
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    failures = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"check_{name}={str(passed).lower()}")
    print(f"check_count={len(checks)}")
    print(f"failed_check_count={len(failures)}")
    print(f"output={output_path}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
