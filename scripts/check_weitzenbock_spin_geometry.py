#!/usr/bin/env python3
"""Independently verify the exact Weitzenbock Spin(4,4) fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from scripts.check_einstein_spinor_model import derive_einstein_tensor
except ModuleNotFoundError:
    from check_einstein_spinor_model import derive_einstein_tensor


DIMENSION = 8
SPINOR_DIMENSION = 16
TIME_INDEX = 4
TRANSVERSE_INDICES = (0, 1, 2, 3, 5, 6, 7)
EXPECTED_CHECK_COUNT = 21
EXPECTED_FIXTURE_SHA256 = (
    "804f00f31ffa4247fc1e30d8e89df3ea7ddbd7c8d9fe795317bd57155c93774c"
)
Matrix = list[list[Fraction]]
Tensor3 = list[list[list[Fraction]]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/weitzenbock-spin-geometry/geometry.json"),
    )
    parser.add_argument(
        "--curved-fixture",
        type=Path,
        default=Path("artifacts/curved-spin-geometry/geometry.json"),
    )
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zeros3() -> Tensor3:
    return [
        [
            [Fraction(0) for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]


def zeros(dimension: int) -> Matrix:
    return [
        [Fraction(0) for _ in range(dimension)]
        for _ in range(dimension)
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


def commutator(left: Matrix, right: Matrix) -> Matrix:
    return add(multiply(left, right), scale(-1, multiply(right, left)))


def expected_records(signs: list[int]) -> dict[str, list[dict[str, Any]]]:
    affine = []
    torsion = []
    contortion = []
    for index in TRANSVERSE_INDICES:
        affine.append(
            {"rho": index, "mu": TIME_INDEX, "nu": index, "coefficient": "H"}
        )
        torsion.extend(
            [
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
                    "coefficient": "-H",
                },
            ]
        )
        contortion.extend(
            [
                {
                    "rho": TIME_INDEX,
                    "mu": index,
                    "nu": index,
                    "coefficient": f"{-signs[index]} a adot",
                },
                {
                    "rho": index,
                    "mu": index,
                    "nu": TIME_INDEX,
                    "coefficient": "-H",
                },
            ]
        )
    return {"affine": affine, "torsion": torsion, "contortion": contortion}


def spin_lift(connection: Tensor3, gamma: list[Matrix]) -> list[Matrix]:
    result = []
    for mu in range(DIMENSION):
        matrix = zeros(SPINOR_DIMENSION)
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                matrix = add(
                    matrix,
                    scale(
                        connection[mu][tangent_a][tangent_b] / 8,
                        commutator(gamma[tangent_a], gamma[tangent_b]),
                    ),
                )
        result.append(matrix)
    return result


def verify_fixture(
    fixture_path: Path,
    curved_path: Path,
    clifford_path: Path,
    *,
    require_canonical_hash: bool = True,
) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    curved = json.loads(curved_path.read_text(encoding="utf-8"))
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    signs = [
        int(curved["tangentMetric"][index][index])
        for index in range(DIMENSION)
    ]
    gamma = [
        [[Fraction(value) for value in row] for row in matrix]
        for matrix in clifford["generators"]
    ]
    scale_factor = Fraction(*curved["sample"]["scaleFactor"])
    scale_derivative = Fraction(*curved["sample"]["scaleDerivative"])
    hubble = scale_derivative / scale_factor
    frame = [
        Fraction(1) if index == TIME_INDEX else scale_factor
        for index in range(DIMENSION)
    ]
    inverse_frame = [Fraction(1) / value for value in frame]
    metric = [
        Fraction(signs[index]) * frame[index] ** 2
        for index in range(DIMENSION)
    ]
    inverse_metric = [Fraction(1) / value for value in metric]

    frame_derivative = zeros3()
    metric_derivative = zeros3()
    for index in TRANSVERSE_INDICES:
        frame_derivative[TIME_INDEX][index][index] = scale_derivative
        metric_derivative[TIME_INDEX][index][index] = (
            2 * signs[index] * scale_factor * scale_derivative
        )

    affine = zeros3()
    for index in TRANSVERSE_INDICES:
        affine[index][TIME_INDEX][index] = hubble
    torsion = zeros3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                torsion[rho][mu][nu] = (
                    affine[rho][mu][nu] - affine[rho][nu][mu]
                )

    levi_civita = zeros3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                levi_civita[rho][mu][nu] = (
                    inverse_metric[rho]
                    * (
                        metric_derivative[mu][nu][rho]
                        + metric_derivative[nu][mu][rho]
                        - metric_derivative[rho][mu][nu]
                    )
                    / 2
                )
    contortion = zeros3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                contortion[rho][mu][nu] = (
                    affine[rho][mu][nu] - levi_civita[rho][mu][nu]
                )

    metric_compatible = True
    postulate = True
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            for rho in range(DIMENSION):
                metric_value = metric_derivative[mu][nu][rho]
                if nu == rho:
                    metric_value -= 2 * affine[nu][mu][nu] * metric[nu]
                metric_compatible &= metric_value == 0
            for tangent_a in range(DIMENSION):
                frame_value = frame_derivative[mu][nu][tangent_a]
                if nu == tangent_a:
                    frame_value -= affine[nu][mu][nu] * frame[nu]
                postulate &= frame_value == 0

    curvature_zero = True
    for rho in range(DIMENSION):
        for sigma in range(DIMENSION):
            for mu in range(DIMENSION):
                for nu in range(DIMENSION):
                    value = sum(
                        (
                            affine[rho][mu][inner] * affine[inner][nu][sigma]
                            - affine[rho][nu][inner] * affine[inner][mu][sigma]
                            for inner in range(DIMENSION)
                        ),
                        Fraction(0),
                    )
                    curvature_zero &= value == 0

    trace = [
        sum(
            (torsion[nu][mu][nu] for nu in range(DIMENSION)),
            Fraction(0),
        )
        for mu in range(DIMENSION)
    ]
    first = Fraction(0)
    second = Fraction(0)
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                value = torsion[rho][mu][nu]
                first += (
                    metric[rho]
                    * inverse_metric[mu]
                    * inverse_metric[nu]
                    * value
                    * value
                    / 4
                )
                second += (
                    inverse_metric[mu]
                    * value
                    * torsion[nu][mu][rho]
                    / 2
                )
    trace_square = sum(
        inverse_metric[index] * trace[index] ** 2
        for index in range(DIMENSION)
    )
    scalar = first + second - trace_square

    levi_civita_spin = zeros3()
    tangent_contortion = zeros3()
    for mu in range(DIMENSION):
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                omega_raised = inverse_frame[tangent_b] * (
                    sum(
                        (
                            levi_civita[rho][mu][tangent_b]
                            * frame[rho]
                            * int(rho == tangent_a)
                            for rho in range(DIMENSION)
                        ),
                        Fraction(0),
                    )
                    - frame_derivative[mu][tangent_b][tangent_a]
                )
                levi_civita_spin[mu][tangent_a][tangent_b] = (
                    signs[tangent_a] * omega_raised
                )
                tangent_contortion[mu][tangent_a][tangent_b] = sum(
                    (
                        signs[tangent_a]
                        * inverse_frame[tangent_b]
                        * contortion[rho][mu][tangent_b]
                        * frame[rho]
                        * int(rho == tangent_a)
                        for rho in range(DIMENSION)
                    ),
                    Fraction(0),
                )
    levi_civita_lift = spin_lift(levi_civita_spin, gamma)
    contortion_lift = spin_lift(tangent_contortion, gamma)
    zero_spin = zeros(SPINOR_DIMENSION)
    spin_relation = all(
        add(levi_civita_lift[mu], contortion_lift[mu]) == zero_spin
        for mu in range(DIMENSION)
    )
    levi_civita_slash = zeros(SPINOR_DIMENSION)
    for mu in TRANSVERSE_INDICES:
        levi_civita_slash = add(
            levi_civita_slash,
            multiply(
                scale(inverse_frame[mu], gamma[mu]),
                levi_civita_lift[mu],
            ),
        )
    torsion_slash = scale(trace[TIME_INDEX] / 2, gamma[TIME_INDEX])

    sample_second_derivative = Fraction(1, 7)
    hubble_derivative = (
        sample_second_derivative / scale_factor - hubble * hubble
    )
    metric_values, einstein = derive_einstein_tensor(
        scale_factor,
        hubble,
        hubble_derivative,
        signs,
    )
    einstein_trace = sum(
        (
            einstein[index][index] / metric_values[index][index]
            for index in range(DIMENSION)
        ),
        Fraction(0),
    )
    ricci_scalar = -einstein_trace / 3
    volume_density = scale_factor**7
    volume_derivative = 7 * scale_factor**6 * scale_derivative
    raised_opposite_trace = 7 * hubble
    raised_opposite_trace_derivative = 7 * hubble_derivative
    boundary_term = 2 * (
        volume_derivative * raised_opposite_trace
        + volume_density * raised_opposite_trace_derivative
    ) / volume_density

    records = expected_records(signs)
    scalar_record = fixture.get("measurements", {}).get("sampleTorsionScalar")
    recorded_scalar = (
        Fraction(*scalar_record)
        if isinstance(scalar_record, list) and len(scalar_record) == 2
        else None
    )
    scalar_formulas = fixture.get("teleparallelScalars", {})
    checks = {
        "canonicalHash": not require_canonical_hash
        or sha256_file(fixture_path) == EXPECTED_FIXTURE_SHA256,
        "schemaVersion": fixture.get("schemaVersion") == 1,
        "sourceHashes": fixture.get("cliffordFixtureSha256")
        == sha256_file(clifford_path)
        and fixture.get("curvedGeometryFixtureSha256")
        == sha256_file(curved_path),
        "dimensionsAndSignature": fixture.get("baseDimension") == 8
        and fixture.get("signature") == [4, 4]
        and fixture.get("tangentMetric") == curved.get("tangentMetric"),
        "frameAgreement": fixture.get("frameAnsatz")
        == curved.get("frameAnsatz"),
        "affineComponents": fixture.get("weitzenbockAffineConnectionNonzero")
        == records["affine"],
        "torsionComponents": fixture.get("torsionNonzero")
        == records["torsion"],
        "contortionComponents": fixture.get("contortionNonzero")
        == records["contortion"],
        "zeroInertialSpinConnection": fixture.get("selectedGauge", {}).get(
            "spinLift"
        )
        == "OmegaW_mu=(1/8)omegaW_muab[gamma^a,gamma^b]=0",
        "vielbeinPostulate": postulate,
        "metricCompatibility": metric_compatible,
        "torsionAntisymmetry": all(
            torsion[rho][mu][nu] == -torsion[rho][nu][mu]
            for rho in range(DIMENSION)
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        "curvatureZero": curvature_zero,
        "torsionTrace": trace[TIME_INDEX] == 7 * hubble
        and all(
            trace[index] == 0
            for index in range(DIMENSION)
            if index != TIME_INDEX
        ),
        "torsionScalar": scalar == 42 * hubble**2
        and recorded_scalar == scalar,
        "connectionDecomposition": all(
            affine[rho][mu][nu]
            == levi_civita[rho][mu][nu] + contortion[rho][mu][nu]
            for rho in range(DIMENSION)
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        "spinContortion": spin_relation,
        "leviCivitaSpinAntisymmetric": all(
            levi_civita_spin[mu][tangent_a][tangent_b]
            == -levi_civita_spin[mu][tangent_b][tangent_a]
            for mu in range(DIMENSION)
            for tangent_a in range(DIMENSION)
            for tangent_b in range(DIMENSION)
        ),
        "homogeneousDirac": torsion_slash == levi_civita_slash,
        "boundaryIdentity": ricci_scalar == -scalar + boundary_term
        and scalar_formulas
        == {
            "torsionScalar": "T=42 H^2",
            "leviCivitaRicciScalar": "RLC=14 Hdot+56 H^2",
            "boundaryTerm": "B=14 Hdot+98 H^2",
            "identity": "RLC=-T+B",
            "tegrLagrangian": "-T/(2 kappa8)",
        },
        "embeddedChecks": len(fixture.get("checks", {})) == 15
        and all(fixture.get("checks", {}).values()),
    }
    return {
        "checks": checks,
        "measurements": {
            "fixtureSha256": sha256_file(fixture_path),
            "sampleTorsionScalar": str(scalar),
            "sampleTorsionTrace": str(trace[TIME_INDEX]),
            "nonzeroTorsionComponents": sum(
                bool(torsion[rho][mu][nu])
                for rho in range(DIMENSION)
                for mu in range(DIMENSION)
                for nu in range(DIMENSION)
            ),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_fixture(
        arguments.fixture.resolve(),
        arguments.curved_fixture.resolve(),
        arguments.clifford_fixture.resolve(),
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
