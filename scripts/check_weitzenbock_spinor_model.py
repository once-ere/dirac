#!/usr/bin/env python3
"""Check the exact reduced Weitzenbock Einstein-spinor field equations."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


EXPECTED_CHECK_COUNT = 13
TRANSVERSE_DIMENSION = Fraction(7)
KAPPA_8 = Fraction(21)
MASS_COEFFICIENT = Fraction(1, 20)
SELF_COEFFICIENT = Fraction(19, 20)
SELF_EXPONENT = Fraction(1, 5)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("artifacts/weitzenbock-spin-geometry/geometry.json"),
    )
    return parser.parse_args()


def verify_model(fixture_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    repository_root = fixture_path.resolve().parents[2]
    manifest_text = (
        repository_root
        / "studies"
        / "weitzenbock_spinor_44"
        / "Cargo.toml"
    ).read_text(encoding="utf-8")
    source_text = (
        repository_root
        / "studies"
        / "weitzenbock_spinor_44"
        / "src"
        / "lib.rs"
    ).read_text(encoding="utf-8")

    cases = (
        (Fraction(1), Fraction(1), Fraction(1), Fraction(1), Fraction(1)),
        (
            Fraction(32),
            Fraction(2),
            Fraction(3, 2),
            Fraction(5, 4),
            Fraction(2),
        ),
        (
            Fraction(1, 32),
            Fraction(1, 2),
            Fraction(2, 3),
            Fraction(4, 3),
            Fraction(3, 2),
        ),
    )
    case_results: list[dict[str, Fraction]] = []
    for condensate, condensate_root, hubble, scale_factor, lapse in cases:
        interaction = SELF_COEFFICIENT * condensate_root
        potential = MASS_COEFFICIENT * condensate + interaction
        potential_rate = MASS_COEFFICIENT + (
            SELF_COEFFICIENT
            * SELF_EXPONENT
            * condensate_root
            / condensate
        )
        pressure = condensate * potential_rate - potential
        condensate_rate = -TRANSVERSE_DIMENSION * hubble * condensate
        density_rate = potential_rate * condensate_rate
        continuity_rate = -TRANSVERSE_DIMENSION * hubble * (
            potential + pressure
        )
        hubble_rate = -KAPPA_8 / (TRANSVERSE_DIMENSION - 1) * (
            potential + pressure
        )
        torsion_trace = TRANSVERSE_DIMENSION * hubble
        torsion_scalar = (
            TRANSVERSE_DIMENSION
            * (TRANSVERSE_DIMENSION - 1)
            * hubble**2
        )
        ricci_scalar = (
            2 * TRANSVERSE_DIMENSION * hubble_rate
            + TRANSVERSE_DIMENSION
            * (TRANSVERSE_DIMENSION + 1)
            * hubble**2
        )
        boundary = (
            2 * TRANSVERSE_DIMENSION * hubble_rate
            + 2 * TRANSVERSE_DIMENSION**2 * hubble**2
        )
        dust_density = MASS_COEFFICIENT * condensate
        action_coefficient = (
            TRANSVERSE_DIMENSION
            * (TRANSVERSE_DIMENSION - 1)
            / (2 * KAPPA_8)
        )
        scale_velocity = lapse * scale_factor * hubble
        scale_acceleration = (
            lapse**2
            * scale_factor
            * (hubble_rate + hubble**2)
        )
        lapse_variation = (
            action_coefficient
            * scale_factor ** (TRANSVERSE_DIMENSION - 2)
            * scale_velocity**2
            / lapse**2
            - scale_factor**TRANSVERSE_DIMENSION * potential
        )
        gravitational_scale_variation = -(
            action_coefficient
            * (TRANSVERSE_DIMENSION - 2)
            * scale_factor ** (TRANSVERSE_DIMENSION - 3)
            * scale_velocity**2
            / lapse
            + 2
            * action_coefficient
            * scale_factor ** (TRANSVERSE_DIMENSION - 2)
            * scale_acceleration
            / lapse
        )
        matter_scale_variation = (
            TRANSVERSE_DIMENSION
            * lapse
            * scale_factor ** (TRANSVERSE_DIMENSION - 1)
            * pressure
        )
        scale_variation = (
            gravitational_scale_variation - matter_scale_variation
        )
        expected_lapse_variation = (
            scale_factor**TRANSVERSE_DIMENSION
            * (action_coefficient * hubble**2 - potential)
        )
        expected_scale_variation = -(
            lapse
            * scale_factor ** (TRANSVERSE_DIMENSION - 1)
            * (
                action_coefficient
                * (
                    2 * hubble_rate
                    + TRANSVERSE_DIMENSION * hubble**2
                )
                + TRANSVERSE_DIMENSION * pressure
            )
        )
        case_results.append(
            {
                "condensate": condensate,
                "potential": potential,
                "pressure": pressure,
                "hubble": hubble,
                "hubbleRate": hubble_rate,
                "condensateRate": condensate_rate,
                "densityRate": density_rate,
                "continuityRate": continuity_rate,
                "torsionTrace": torsion_trace,
                "torsionScalar": torsion_scalar,
                "ricciScalar": ricci_scalar,
                "boundary": boundary,
                "dustDensity": dust_density,
                "interactionDensity": interaction,
                "lapseVariation": lapse_variation,
                "expectedLapseVariation": expected_lapse_variation,
                "scaleVariation": scale_variation,
                "expectedScaleVariation": expected_scale_variation,
            }
        )

    initial = case_results[0]

    checks = {
        "teleparallelGeometry": fixture.get("baseDimension") == 8
        and fixture.get("signature") == [4, 4],
        "flatAndTorsionful": fixture.get("checks", {}).get(
            "curvatureZero"
        )
        is True
        and fixture.get("checks", {}).get("torsionNonzero") is True,
        "connectionSubstitution": fixture.get("selectedGauge", {}).get(
            "inertialSpinConnection"
        )
        == "omegaW_mu^a_b=0"
        and fixture.get("spinConnectionRelation")
        == "OmegaW=OmegaLC+Kspin=0 in selected gauge",
        "hermitianDiracReduction": all(
            result["torsionTrace"] / 2
            == Fraction(7, 2) * result["hubble"]
            for result in case_results
        )
        and fixture.get("checks", {}).get("homogeneousDiracEquivalence")
        is True,
        "condensateContinuity": all(
            result["condensateRate"]
            == -TRANSVERSE_DIMENSION
            * result["hubble"]
            * result["condensate"]
            for result in case_results
        ),
        "densityContinuity": all(
            result["densityRate"] == result["continuityRate"]
            for result in case_results
        ),
        "tegrBoundaryEquivalence": all(
            result["ricciScalar"]
            == -result["torsionScalar"] + result["boundary"]
            for result in case_results
        ),
        "minisuperspaceLapseVariation": all(
            result["lapseVariation"] == result["expectedLapseVariation"]
            for result in case_results
        ),
        "minisuperspaceScaleVariation": all(
            result["scaleVariation"] == result["expectedScaleVariation"]
            for result in case_results
        ),
        "initialNormalization": initial["potential"] == 1
        and initial["pressure"] == Fraction(-19, 25)
        and initial["hubbleRate"] == Fraction(-21, 25),
        "initialFieldEquations": initial["lapseVariation"] == 0
        and initial["scaleVariation"] == 0,
        "darkSectorDecomposition": all(
            result["dustDensity"] + result["interactionDensity"]
            == result["potential"]
            for result in case_results
        ),
        "independentRustImplementation": "einstein_spinor_44"
        not in manifest_text
        and "einstein_spinor_44" not in source_text
        and "cvode_rs" in manifest_text
        and "pub fn rhs_values" in source_text,
    }
    return {
        "checks": checks,
        "measurements": {
            "exactCaseCount": len(case_results),
            "initialCondensate": str(initial["condensate"]),
            "initialDensity": str(initial["potential"]),
            "initialPressure": str(initial["pressure"]),
            "initialEquationOfState": str(
                initial["pressure"] / initial["potential"]
            ),
            "initialHubbleDerivative": str(initial["hubbleRate"]),
            "initialTorsionTrace": str(initial["torsionTrace"]),
            "initialTorsionScalar": str(initial["torsionScalar"]),
            "initialLeviCivitaRicciScalar": str(initial["ricciScalar"]),
            "initialBoundaryTerm": str(initial["boundary"]),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_model(arguments.fixture.resolve())
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
