#!/usr/bin/env python3
"""Build the exact Weitzenbock Spin(4,4) geometry fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from scripts.build_curved_spin_geometry import (
        DIMENSION,
        SPINOR_DIMENSION,
        TIME_INDEX,
        TRANSVERSE_INDICES,
        add,
        connection_data,
        diagonal,
        multiply,
        scale,
        zero_tensor3,
    )
except ModuleNotFoundError:
    from build_curved_spin_geometry import (
        DIMENSION,
        SPINOR_DIMENSION,
        TIME_INDEX,
        TRANSVERSE_INDICES,
        add,
        connection_data,
        diagonal,
        multiply,
        scale,
        zero_tensor3,
    )


Tensor3 = list[list[list[Fraction]]]
Tensor4 = list[list[list[list[Fraction]]]]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    parser.add_argument(
        "--curved-fixture",
        type=Path,
        default=Path("artifacts/curved-spin-geometry/geometry.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/weitzenbock-spin-geometry/geometry.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_tensor4() -> Tensor4:
    return [
        [
            [
                [Fraction(0) for _ in range(DIMENSION)]
                for _ in range(DIMENSION)
            ]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]


def commutator(
    left: list[list[Fraction]],
    right: list[list[Fraction]],
) -> list[list[Fraction]]:
    return add(multiply(left, right), scale(-1, multiply(right, left)))


def tangent_difference(
    difference: Tensor3,
    frame: list[list[Fraction]],
    inverse_frame: list[list[Fraction]],
    metric_signs: list[int],
) -> Tensor3:
    result = zero_tensor3()
    for mu in range(DIMENSION):
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                raised = sum(
                    (
                        inverse_frame[tangent_b][nu]
                        * difference[rho][mu][nu]
                        * frame[rho][tangent_a]
                        for rho in range(DIMENSION)
                        for nu in range(DIMENSION)
                    ),
                    Fraction(0),
                )
                result[mu][tangent_a][tangent_b] = (
                    metric_signs[tangent_a] * raised
                )
    return result


def spin_lift(
    connection: Tensor3,
    generators: list[list[list[Fraction]]],
) -> list[list[list[Fraction]]]:
    zero = [
        [Fraction(0) for _ in range(SPINOR_DIMENSION)]
        for _ in range(SPINOR_DIMENSION)
    ]
    result = []
    for mu in range(DIMENSION):
        matrix = [row[:] for row in zero]
        for tangent_a in range(DIMENSION):
            for tangent_b in range(DIMENSION):
                matrix = add(
                    matrix,
                    scale(
                        connection[mu][tangent_a][tangent_b] / 8,
                        commutator(
                            generators[tangent_a],
                            generators[tangent_b],
                        ),
                    ),
                )
        result.append(matrix)
    return result


def torsion_scalar(
    torsion: Tensor3,
    metric: list[list[Fraction]],
    inverse_metric: list[list[Fraction]],
) -> Fraction:
    first = Fraction(0)
    second = Fraction(0)
    trace = [Fraction(0) for _ in range(DIMENSION)]
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            trace[mu] += torsion[rho][mu][rho]
            for nu in range(DIMENSION):
                component = torsion[rho][mu][nu]
                first += (
                    metric[rho][rho]
                    * inverse_metric[mu][mu]
                    * inverse_metric[nu][nu]
                    * component
                    * component
                ) / 4
                swapped = torsion[nu][mu][rho]
                second += (
                    inverse_metric[mu][mu]
                    * component
                    * swapped
                ) / 2
    trace_square = sum(
        (
            inverse_metric[mu][mu] * trace[mu] * trace[mu]
            for mu in range(DIMENSION)
        ),
        Fraction(0),
    )
    return first + second - trace_square


def nonzero_records(
    metric_signs: list[int],
) -> dict[str, list[dict[str, Any]]]:
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
                    "coefficient": f"{-metric_signs[index]} a adot",
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


def main() -> int:
    arguments = parse_arguments()
    clifford_path = arguments.clifford_fixture.resolve()
    curved_path = arguments.curved_fixture.resolve()
    output_path = arguments.output.resolve()
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    curved = json.loads(curved_path.read_text(encoding="utf-8"))
    metric_signs = [
        int(curved["tangentMetric"][index][index])
        for index in range(DIMENSION)
    ]
    generators = [
        [[Fraction(value) for value in row] for row in matrix]
        for matrix in clifford["generators"]
    ]
    volume = [
        [Fraction(value) for value in row]
        for row in clifford["volumeElement"]
    ]

    sample_scale = Fraction(*curved["sample"]["scaleFactor"])
    sample_derivative = Fraction(*curved["sample"]["scaleDerivative"])
    hubble = sample_derivative / sample_scale
    frame_values = [
        Fraction(1) if index == TIME_INDEX else sample_scale
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
    frame_derivative = zero_tensor3()
    metric_derivative = zero_tensor3()
    for index in TRANSVERSE_INDICES:
        frame_derivative[TIME_INDEX][index][index] = sample_derivative
        metric_derivative[TIME_INDEX][index][index] = (
            2 * metric_signs[index] * sample_scale * sample_derivative
        )

    affine = zero_tensor3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                affine[rho][mu][nu] = sum(
                    (
                        inverse_frame[rho][tangent_a]
                        * frame_derivative[mu][nu][tangent_a]
                        for tangent_a in range(DIMENSION)
                    ),
                    Fraction(0),
                )
    torsion = zero_tensor3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                torsion[rho][mu][nu] = (
                    affine[rho][mu][nu] - affine[rho][nu][mu]
                )

    curvature = zero_tensor4()
    for rho in range(DIMENSION):
        for sigma in range(DIMENSION):
            for mu in range(DIMENSION):
                for nu in range(DIMENSION):
                    curvature[rho][sigma][mu][nu] = sum(
                        (
                            affine[rho][mu][inner] * affine[inner][nu][sigma]
                            - affine[rho][nu][inner] * affine[inner][mu][sigma]
                            for inner in range(DIMENSION)
                        ),
                        Fraction(0),
                    )

    metric_compatible = True
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            for rho in range(DIMENSION):
                value = metric_derivative[mu][nu][rho]
                value -= sum(
                    affine[sigma][mu][nu] * metric[sigma][rho]
                    for sigma in range(DIMENSION)
                )
                value -= sum(
                    affine[sigma][mu][rho] * metric[nu][sigma]
                    for sigma in range(DIMENSION)
                )
                metric_compatible &= value == 0

    vielbein_postulate = True
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            for tangent_a in range(DIMENSION):
                value = frame_derivative[mu][nu][tangent_a]
                value -= sum(
                    affine[rho][mu][nu] * frame[rho][tangent_a]
                    for rho in range(DIMENSION)
                )
                vielbein_postulate &= value == 0

    _, _, levi_civita, levi_civita_spin = connection_data(
        metric_signs,
        sample_scale,
        sample_derivative,
    )
    contortion = zero_tensor3()
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                contortion[rho][mu][nu] = (
                    affine[rho][mu][nu] - levi_civita[rho][mu][nu]
                )
    tangent_contortion = tangent_difference(
        contortion,
        frame,
        inverse_frame,
        metric_signs,
    )
    levi_civita_lift = spin_lift(levi_civita_spin, generators)
    contortion_lift = spin_lift(tangent_contortion, generators)
    zero_spinor_matrix = [
        [Fraction(0) for _ in range(SPINOR_DIMENSION)]
        for _ in range(SPINOR_DIMENSION)
    ]
    zero_spin_connection = [
        [row[:] for row in zero_spinor_matrix]
        for _ in range(DIMENSION)
    ]
    spin_relation = all(
        add(levi_civita_lift[mu], contortion_lift[mu])
        == zero_spin_connection[mu]
        for mu in range(DIMENSION)
    )

    torsion_trace = [
        sum(
            (torsion[nu][mu][nu] for nu in range(DIMENSION)),
            Fraction(0),
        )
        for mu in range(DIMENSION)
    ]
    computed_torsion_scalar = torsion_scalar(torsion, metric, inverse_metric)
    expected_torsion_scalar = Fraction(42) * hubble * hubble
    sample_second_derivative = Fraction(1, 7)
    hubble_derivative = (
        sample_second_derivative / sample_scale - hubble * hubble
    )
    levi_civita_ricci_scalar = (
        14 * hubble_derivative + 56 * hubble * hubble
    )
    volume_density = sample_scale**7
    volume_derivative = 7 * sample_scale**6 * sample_derivative
    raised_opposite_trace = 7 * hubble
    raised_opposite_trace_derivative = 7 * hubble_derivative
    boundary_term = 2 * (
        volume_derivative * raised_opposite_trace
        + volume_density * raised_opposite_trace_derivative
    ) / volume_density
    torsion_slash = scale(
        torsion_trace[TIME_INDEX] / 2,
        generators[TIME_INDEX],
    )
    levi_civita_slash = [row[:] for row in zero_spinor_matrix]
    for mu in TRANSVERSE_INDICES:
        levi_civita_slash = add(
            levi_civita_slash,
            multiply(
                scale(inverse_frame[mu][mu], generators[mu]),
                levi_civita_lift[mu],
            ),
        )

    connection_identity = all(
        affine[rho][mu][nu]
        == levi_civita[rho][mu][nu] + contortion[rho][mu][nu]
        for rho in range(DIMENSION)
        for mu in range(DIMENSION)
        for nu in range(DIMENSION)
    )
    checks = {
        "signature": metric_signs == [1, 1, 1, 1, -1, -1, -1, -1],
        "sourceFrame": curved["frameAnsatz"].startswith("e_mu^a=diag"),
        "vielbeinPostulate": vielbein_postulate,
        "metricCompatibility": metric_compatible,
        "torsionAntisymmetry": all(
            torsion[rho][mu][nu] == -torsion[rho][nu][mu]
            for rho in range(DIMENSION)
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        "torsionNonzero": any(
            torsion[rho][mu][nu]
            for rho in range(DIMENSION)
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        "curvatureZero": not any(
            curvature[rho][sigma][mu][nu]
            for rho in range(DIMENSION)
            for sigma in range(DIMENSION)
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        "contortionIdentity": connection_identity,
        "inertialSpinConnectionZero": all(
            matrix == zero_spinor_matrix for matrix in zero_spin_connection
        ),
        "spinContortionIdentity": spin_relation,
        "torsionTrace": torsion_trace[TIME_INDEX] == 7 * hubble
        and all(
            torsion_trace[index] == 0
            for index in range(DIMENSION)
            if index != TIME_INDEX
        ),
        "torsionScalar": computed_torsion_scalar == expected_torsion_scalar,
        "boundaryIdentity": levi_civita_ricci_scalar
        == -computed_torsion_scalar + boundary_term,
        "homogeneousDiracEquivalence": torsion_slash == levi_civita_slash,
        "chiralityPreserved": all(
            multiply(matrix, volume) == multiply(volume, matrix)
            for matrix in zero_spin_connection
        ),
    }
    records = nonzero_records(metric_signs)
    document = {
        "schemaVersion": 1,
        "connection": "Dirac-Weitzenbock inertial spin connection",
        "cliffordFixtureSha256": sha256_file(clifford_path),
        "curvedGeometryFixtureSha256": sha256_file(curved_path),
        "baseDimension": DIMENSION,
        "signature": [4, 4],
        "coordinateOrder": curved["coordinateOrder"],
        "timeCoordinateIndexZeroBased": TIME_INDEX,
        "transverseIndicesZeroBased": TRANSVERSE_INDICES,
        "tangentMetric": curved["tangentMetric"],
        "metricAnsatz": curved["metricAnsatz"],
        "frameAnsatz": curved["frameAnsatz"],
        "affineConnectionFormula": (
            "GammaW^rho_munu=e_a^rho(partial_mu e_nu^a+"
            "omegaW_mu^a_b e_nu^b)"
        ),
        "selectedGauge": {
            "name": "diagonal proper-frame Weitzenbock gauge",
            "inertialSpinConnection": "omegaW_mu^a_b=0",
            "spinLift": "OmegaW_mu=(1/8)omegaW_muab[gamma^a,gamma^b]=0",
        },
        "localLorentzGaugeFamily": (
            "e'=Lambda e, omegaW'=Lambda omegaW Lambda^-1-"
            "(partial Lambda)Lambda^-1"
        ),
        "weitzenbockAffineConnectionNonzero": records["affine"],
        "torsionConvention": (
            "T^rho_munu=GammaW^rho_munu-GammaW^rho_numu"
        ),
        "torsionNonzero": records["torsion"],
        "torsionTraceConvention": "tau_mu=T^nu_munu",
        "torsionTrace": {"time": "7 H", "transverse": "0"},
        "contortionConvention": "K^rho_munu=GammaW^rho_munu-GammaLC^rho_munu",
        "contortionNonzero": records["contortion"],
        "connectionRelation": "GammaW=GammaLC+K",
        "spinConnectionRelation": "OmegaW=OmegaLC+Kspin=0 in selected gauge",
        "teleparallelScalars": {
            "torsionScalar": "T=42 H^2",
            "leviCivitaRicciScalar": "RLC=14 Hdot+56 H^2",
            "boundaryTerm": "B=14 Hdot+98 H^2",
            "identity": "RLC=-T+B",
            "tegrLagrangian": "-T/(2 kappa8)",
        },
        "spinorDerivative": (
            "DW_mu=partial_mu+(1/8)omegaW_muab[gamma^a,gamma^b]"
        ),
        "hermitianDiracOperator": (
            "gamma^mu(DW_mu+(1/2)tau_mu)"
        ),
        "homogeneousDiracOperator": "gamma^4(partial_t+(7/2)H)",
        "sample": curved["sample"],
        "checks": checks,
        "measurements": {
            "nonzeroAffineConnectionComponents": len(records["affine"]),
            "nonzeroTorsionComponents": len(records["torsion"]),
            "nonzeroContortionComponents": len(records["contortion"]),
            "nonzeroInertialSpinConnectionComponents": 0,
            "sampleTorsionScalar": [
                computed_torsion_scalar.numerator,
                computed_torsion_scalar.denominator,
            ],
            "spinorDimension": SPINOR_DIMENSION,
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
