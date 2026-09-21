#!/usr/bin/env python3
"""Independently verify the curved Spin(4,4) geometry fixture."""

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
EXPECTED_CHECK_COUNT = 16
Matrix = list[list[Fraction]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/curved-spin-geometry/geometry.json"),
    )
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    parser.add_argument(
        "--wolfram-report",
        type=Path,
        default=Path(
            "artifacts/curved-spin-geometry/wolfram-report.json"
        ),
    )
    parser.add_argument(
        "--clifford-package",
        type=Path,
        default=Path("wolfram/Cl44.wl"),
    )
    parser.add_argument(
        "--geometry-package",
        type=Path,
        default=Path("wolfram/CurvedSpinGeometry.wl"),
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


def decode_rational(value: list[int]) -> Fraction:
    return Fraction(value[0], value[1])


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


def verify_fixture(
    fixture_path: Path,
    clifford_path: Path,
    wolfram_report_path: Path,
    clifford_package_path: Path,
    geometry_package_path: Path,
) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    wolfram_report = json.loads(
        wolfram_report_path.read_text(encoding="utf-8")
    )
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
    stored_charge = [
        [[Fraction(value) for value in row] for row in fixture["spinorBilinear"]["matrix"]]
    ][0]

    scale_factor = decode_rational(fixture["sample"]["scaleFactor"])
    scale_derivative = decode_rational(fixture["sample"]["scaleDerivative"])
    hubble = decode_rational(fixture["sample"]["hubble"])
    frame_values = [
        Fraction(1) if index == TIME_INDEX else scale_factor
        for index in range(DIMENSION)
    ]
    inverse_frame_values = [Fraction(1) / value for value in frame_values]

    metric_values = [
        Fraction(metric_signs[index]) * frame_values[index] ** 2
        for index in range(DIMENSION)
    ]
    inverse_metric_values = [Fraction(1) / value for value in metric_values]
    metric_derivative = [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    frame_derivative = [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for index in TRANSVERSE_INDICES:
        metric_derivative[TIME_INDEX][index][index] = (
            2 * metric_signs[index] * scale_factor * scale_derivative
        )
        frame_derivative[TIME_INDEX][index][index] = scale_derivative

    christoffel = [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                christoffel[rho][mu][nu] = (
                    inverse_metric_values[rho]
                    * (
                        metric_derivative[mu][nu][rho]
                        + metric_derivative[nu][mu][rho]
                        - metric_derivative[rho][mu][nu]
                    )
                    / 2
                )

    omega = [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for mu in range(DIMENSION):
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                raised = inverse_frame_values[tangent_b] * (
                    christoffel[tangent_a][mu][tangent_b]
                    * frame_values[tangent_a]
                    - frame_derivative[mu][tangent_b][tangent_a]
                )
                omega[mu][tangent_a][tangent_b] = (
                    metric_signs[tangent_a] * raised
                )

    postulate = True
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            for tangent_a in range(DIMENSION):
                derivative = (
                    scale_derivative
                    if mu == TIME_INDEX
                    and nu == tangent_a
                    and nu in TRANSVERSE_INDICES
                    else Fraction(0)
                )
                christoffel_term = (
                    christoffel[tangent_a][mu][nu]
                    * frame_values[tangent_a]
                )
                connection_term = sum(
                    (
                        metric_signs[tangent_a]
                        * omega[mu][tangent_a][tangent_b]
                        * (
                            frame_values[nu]
                            if nu == tangent_b
                            else Fraction(0)
                        )
                        for tangent_b in range(DIMENSION)
                    ),
                    Fraction(0),
                )
                postulate &= (
                    derivative - christoffel_term + connection_term == 0
                )

    zero = [
        [Fraction(0) for _ in range(SPINOR_DIMENSION)]
        for _ in range(SPINOR_DIMENSION)
    ]
    spin_matrices = []
    for mu in range(DIMENSION):
        spin_matrix = [row[:] for row in zero]
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                commutator = add(
                    multiply(generators[tangent_a], generators[tangent_b]),
                    scale(
                        Fraction(-1),
                        multiply(
                            generators[tangent_b], generators[tangent_a]
                        ),
                    ),
                )
                spin_matrix = add(
                    spin_matrix,
                    scale(
                        omega[mu][tangent_a][tangent_b] / 8,
                        commutator,
                    ),
                )
        spin_matrices.append(spin_matrix)
    slash_connection = [row[:] for row in zero]
    for index in TRANSVERSE_INDICES:
        slash_connection = add(
            slash_connection,
            multiply(
                scale(inverse_frame_values[index], generators[index]),
                spin_matrices[index],
            ),
        )
    expected_slash = scale(
        Fraction(len(TRANSVERSE_INDICES), 2) * hubble,
        generators[TIME_INDEX],
    )
    expected_christoffel, expected_omega = expected_records(metric_signs)

    checks = {
        "schemaVersion": fixture.get("schemaVersion") == 1,
        "cliffordFixtureHash": fixture.get("cliffordFixtureSha256")
        == sha256_file(clifford_path),
        "baseAndSignature": fixture.get("baseDimension") == DIMENSION
        and fixture.get("signature") == [4, 4]
        and fixture.get("tangentMetric") == clifford["metric"],
        "coordinateConvention": fixture.get("timeCoordinateIndexZeroBased")
        == TIME_INDEX
        and fixture.get("transverseIndicesZeroBased") == TRANSVERSE_INDICES,
        "componentInventory": fixture.get("christoffelNonzero")
        == expected_christoffel
        and fixture.get("spinConnectionNonzero") == expected_omega,
        "vielbeinPostulate": postulate,
        "spinConnectionAntisymmetry": all(
            omega[mu][a][b] == -omega[mu][b][a]
            for mu in range(DIMENSION)
            for a in range(DIMENSION)
            for b in range(DIMENSION)
        ),
        "chargeMatrix": stored_charge == charge
        and transpose(charge) == charge
        and multiply(charge, charge) == identity(SPINOR_DIMENSION),
        "chargeSignature": sum(charge[index][index] for index in range(16))
        == 0,
        "gammaChargeAdjoint": all(
            multiply(transpose(generator), charge)
            == scale(Fraction(-1), multiply(charge, generator))
            for generator in generators
        ),
        "slashConnection": slash_connection == expected_slash,
        "connectionPreservesChirality": all(
            multiply(matrix, volume) == multiply(volume, matrix)
            for matrix in spin_matrices
        ),
        "bundleDecomposition": fixture["spinorBundle"]["fiberDimension"]
        == SPINOR_DIMENSION
        and fixture["spinorBundle"]["halfSpinDimensions"] == [8, 8]
        and fixture["spinorBundle"]["halfSpinIndicesZeroBased"]
        == {
            "Plus": [
                index for index in range(16) if volume[index][index] == 1
            ],
            "Minus": [
                index for index in range(16) if volume[index][index] == -1
            ],
        },
        "storedChecks": len(fixture.get("checks", {})) == 12
        and all(fixture.get("checks", {}).values()),
        "wolframReport": wolfram_report.get("schemaVersion") == 1
        and len(wolfram_report.get("checks", {})) == 11
        and all(wolfram_report.get("checks", {}).values())
        and wolfram_report.get("measurements", {}).get(
            "nonzeroChristoffelComponents"
        )
        == 21
        and wolfram_report.get("measurements", {}).get(
            "nonzeroSpinConnectionComponents"
        )
        == 14,
        "wolframSourceHashes": wolfram_report.get("sourceSha256")
        == {
            "Cl44.wl": sha256_file(clifford_package_path),
            "CurvedSpinGeometry.wl": sha256_file(geometry_package_path),
        },
    }
    return {
        "checks": checks,
        "measurements": {
            "sampleScaleFactor": float(scale_factor),
            "sampleScaleDerivative": float(scale_derivative),
            "sampleHubble": float(hubble),
            "spinorDimension": SPINOR_DIMENSION,
            "nonzeroChristoffelComponents": len(expected_christoffel),
            "nonzeroSpinConnectionComponents": len(expected_omega),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_fixture(
        arguments.fixture.resolve(),
        arguments.clifford_fixture.resolve(),
        arguments.wolfram_report.resolve(),
        arguments.clifford_package.resolve(),
        arguments.geometry_package.resolve(),
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
    if len(report["checks"]) != EXPECTED_CHECK_COUNT:
        print(f"ERROR: expected {EXPECTED_CHECK_COUNT} checks")
        return 1
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
