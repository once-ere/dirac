#!/usr/bin/env python3
"""Independently verify the coupled Spin(4,4) Einstein-spinor output."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_CHECK_COUNT = 22
EXPECTED_HISTORY_SHA256 = (
    "9553b36f201ef43a92c7de3fe2f46457a592e55285e6220d8aa7af6e36a26f9c"
)
EXPECTED_SUMMARY_SHA256 = (
    "6b15d084178d01aaed37b84b4bcf8f5246a6941bbe8366ad9c0c3db099eea0f1"
)
KAPPA_8 = 21.0
MASS_COEFFICIENT = 1.0 / 20.0
SELF_COEFFICIENT = 19.0 / 20.0
SELF_EXPONENT = 1.0 / 5.0
T_MIN = -0.2
T_MAX = 1.5
OUTPUT_STEP = 0.01
REFINED_RELATIVE_TOLERANCE = 1.0e-12
REFINED_ABSOLUTE_TOLERANCE = 1.0e-14
REFINED_MAXIMUM_STEP = 0.001


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/einstein-spinor-44"),
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--refined", type=Path)
    parser.add_argument(
        "--geometry-fixture",
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


def close(left: float, right: float, tolerance: float = 5.0e-13) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), 1.0e-300)


def bilinear(matrix: list[list[int]], spinor: list[float]) -> float:
    return sum(
        spinor[row] * matrix[row][column] * spinor[column]
        for row in range(16)
        for column in range(16)
    )


def derived_values(
    scale_factor: float,
    hubble: float,
    spinor: list[float],
    charge: list[list[int]],
) -> tuple[list[float], list[float]]:
    condensate = bilinear(charge, spinor)
    expected_condensate = scale_factor**-7.0
    interaction = SELF_COEFFICIENT * condensate**SELF_EXPONENT
    density = MASS_COEFFICIENT * condensate + interaction
    pressure = (SELF_EXPONENT - 1.0) * interaction
    expected_density = (
        MASS_COEFFICIENT * expected_condensate
        + SELF_COEFFICIENT * expected_condensate**SELF_EXPONENT
    )
    hubble_derivative = -KAPPA_8 / 6.0 * (density + pressure)
    acceleration = hubble * hubble + hubble_derivative
    values = [
        condensate,
        density,
        pressure,
        pressure / density,
        MASS_COEFFICIENT * condensate / density,
        interaction / density,
        acceleration,
    ]
    errors = [
        relative_error(condensate, expected_condensate),
        relative_error(density, expected_density),
        relative_error(hubble * hubble, density),
    ]
    return values, errors


def rhs_values(
    state: list[float],
    charge: list[list[int]],
    time_gamma: list[list[int]],
) -> list[float]:
    scale_factor, hubble = state[:2]
    spinor = state[2:]
    condensate = bilinear(charge, spinor)
    interaction = SELF_COEFFICIENT * condensate**SELF_EXPONENT
    density = MASS_COEFFICIENT * condensate + interaction
    pressure_value = (SELF_EXPONENT - 1.0) * interaction
    potential_rate = MASS_COEFFICIENT + (
        SELF_COEFFICIENT
        * SELF_EXPONENT
        * condensate ** (SELF_EXPONENT - 1.0)
    )
    gamma_spinor = [
        sum(time_gamma[row][column] * spinor[column] for column in range(16))
        for row in range(16)
    ]
    return [
        scale_factor * hubble,
        -KAPPA_8 / 6.0 * (density + pressure_value),
        *[
            -3.5 * hubble * spinor[index]
            - potential_rate * gamma_spinor[index]
            for index in range(16)
        ],
    ]


def five_point_derivatives(
    times: list[float],
    states: list[list[float]],
) -> list[tuple[int, list[float]]]:
    result = []
    for index in range(2, len(states) - 2):
        step = times[index + 1] - times[index]
        derivative = [
            (
                -states[index + 2][component]
                + 8.0 * states[index + 1][component]
                - 8.0 * states[index - 1][component]
                + states[index - 2][component]
            )
            / (12.0 * step)
            for component in range(18)
        ]
        result.append((index, derivative))
    return result


def refined_summary_is_valid(
    refined_summary: dict[str, Any],
    canonical_summary: dict[str, Any],
    refined_errors: list[float],
    canonical_errors: list[float],
) -> bool:
    recorded_errors = refined_summary.get("maximumRelativeError", {})
    linked_fields = (
        "study",
        "stateDimension",
        "baseDimension",
        "signature",
        "cl44FixtureSha256",
        "geometryFixtureSha256",
        "parameters",
        "sampleCount",
    )
    return (
        refined_summary.get("schemaVersion") == 1
        and all(
            refined_summary.get(field) == canonical_summary.get(field)
            for field in linked_fields
        )
        and close(
            refined_summary.get("relativeTolerance", math.nan),
            REFINED_RELATIVE_TOLERANCE,
        )
        and close(
            refined_summary.get("absoluteTolerance", math.nan),
            REFINED_ABSOLUTE_TOLERANCE,
        )
        and close(
            refined_summary.get("maximumStep", math.nan),
            REFINED_MAXIMUM_STEP,
        )
        and refined_summary.get("solverSteps") == 2294
        and refined_summary.get("rhsEvaluations") == 2422
        and refined_summary.get("verdict") == "SUCCESS"
        and all(
            close(recorded, recomputed)
            for recorded, recomputed in zip(
                [
                    recorded_errors.get("condensate", math.nan),
                    recorded_errors.get("density", math.nan),
                    recorded_errors.get("friedmann", math.nan),
                ],
                refined_errors,
                strict=True,
            )
        )
        and all(
            refined < canonical
            for refined, canonical in zip(
                refined_errors,
                canonical_errors,
                strict=True,
            )
        )
    )


def verify_output(
    output_directory: Path,
    repeat_directory: Path | None,
    refined_directory: Path | None,
    geometry_path: Path,
    clifford_path: Path,
) -> dict[str, Any]:
    history_path = output_directory / "history.csv"
    summary_path = output_directory / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    charge: list[list[int]] = geometry["spinorBilinear"]["matrix"]
    time_gamma: list[list[int]] = clifford["generators"][4]
    with history_path.open("r", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    expected_fields = [
        "t",
        "a",
        "H",
        *[f"psi{index}" for index in range(16)],
        "S",
        "rho",
        "pressure",
        "w",
        "dust_like_fraction",
        "negative_pressure_fraction",
        "acceleration",
        "S_relative_error",
        "density_relative_error",
        "friedmann_relative_error",
    ]
    times = [float(row["t"]) for row in rows]
    scales = [float(row["a"]) for row in rows]
    hubbles = [float(row["H"]) for row in rows]
    spinors = [
        [float(row[f"psi{index}"]) for index in range(16)] for row in rows
    ]
    stored_values = [
        [
            float(row[name])
            for name in (
                "S",
                "rho",
                "pressure",
                "w",
                "dust_like_fraction",
                "negative_pressure_fraction",
                "acceleration",
            )
        ]
        for row in rows
    ]
    stored_errors = [
        [
            float(row[name])
            for name in (
                "S_relative_error",
                "density_relative_error",
                "friedmann_relative_error",
            )
        ]
        for row in rows
    ]
    recomputed = [
        derived_values(scale_factor, hubble, spinor, charge)
        for scale_factor, hubble, spinor in zip(
            scales, hubbles, spinors, strict=True
        )
    ]
    recomputed_values = [value[0] for value in recomputed]
    recomputed_errors = [value[1] for value in recomputed]
    maximum_errors = [
        max(errors[index] for errors in recomputed_errors)
        if recomputed_errors
        else math.inf
        for index in range(3)
    ]
    states = [
        [scale_factor, hubble, *spinor]
        for scale_factor, hubble, spinor in zip(
            scales, hubbles, spinors, strict=True
        )
    ]
    derivative_rows = five_point_derivatives(times, states)
    component_squared_errors = [0.0] * 18
    spatial_errors = []
    for index, derivative in derivative_rows:
        expected_rhs = rhs_values(states[index], charge, time_gamma)
        for component in range(18):
            residual = derivative[component] - expected_rhs[component]
            component_squared_errors[component] += residual * residual
        pressure_value = recomputed_values[index][2]
        density = recomputed_values[index][1]
        spatial_residual = (
            6.0 * derivative[1]
            + 21.0 * hubbles[index] * hubbles[index]
            + KAPPA_8 * pressure_value
        )
        spatial_errors.append(
            abs(spatial_residual) / max(KAPPA_8 * density, 1.0e-300)
        )
    component_rms = [
        math.sqrt(value / len(derivative_rows))
        for value in component_squared_errors
    ]
    maximum_component_rms = max(component_rms)
    maximum_spatial_error = max(spatial_errors)

    transition_scale = (
        5.0
        * MASS_COEFFICIENT
        / (
            (2.0 - 7.0 * SELF_EXPONENT)
            * SELF_COEFFICIENT
        )
    ) ** (1.0 / (7.0 * (1.0 - SELF_EXPONENT)))
    transition_pair = next(
        (
            (index - 1, index)
            for index in range(1, len(rows))
            if scales[index - 1] <= transition_scale
            and scales[index] >= transition_scale
        ),
        None,
    )
    transition = None
    if transition_pair is not None:
        left, right = transition_pair
        fraction = (transition_scale - scales[left]) / (
            scales[right] - scales[left]
        )
        transition = (
            times[left] + fraction * (times[right] - times[left]),
            transition_scale,
        )

    summary_errors = summary.get("maximumRelativeError", {})
    expected_parameters = {
        "kappa8": KAPPA_8,
        "massCoefficient": MASS_COEFFICIENT,
        "selfCoefficient": SELF_COEFFICIENT,
        "selfExponent": SELF_EXPONENT,
    }
    repeat_compared = repeat_directory is not None
    repeat_equal = repeat_compared and all(
        (output_directory / name).read_bytes()
        == (repeat_directory / name).read_bytes()
        for name in ("history.csv", "summary.json")
    )
    refined_compared = refined_directory is not None
    maximum_refined_state_difference: float | None = None
    refined_maximum_errors: list[float] | None = None
    refined_convergence = False
    if refined_directory is not None:
        refined_summary = json.loads(
            (refined_directory / "summary.json").read_text(encoding="utf-8")
        )
        with (refined_directory / "history.csv").open(
            "r", encoding="utf-8", newline=""
        ) as source:
            refined_rows = list(csv.DictReader(source))
        state_fields = [
            "a",
            "H",
            *[f"psi{index}" for index in range(16)],
        ]
        if rows and len(refined_rows) == len(rows):
            maximum_refined_state_difference = max(
                abs(float(row[field]) - float(refined_row[field]))
                / max(
                    1.0,
                    abs(float(row[field])),
                    abs(float(refined_row[field])),
                )
                for row, refined_row in zip(
                    rows, refined_rows, strict=True
                )
                for field in state_fields
            )
            refined_recomputed = [
                derived_values(
                    float(row["a"]),
                    float(row["H"]),
                    [
                        float(row[f"psi{index}"])
                        for index in range(16)
                    ],
                    charge,
                )
                for row in refined_rows
            ]
            refined_maximum_errors = [
                max(values[1][index] for values in refined_recomputed)
                for index in range(3)
            ]
            refined_convergence = (
                list(refined_rows[0]) == expected_fields
                and all(
                    close(float(row["t"]), times[index], 1.0e-13)
                    for index, row in enumerate(refined_rows)
                )
                and refined_summary_is_valid(
                    refined_summary,
                    summary,
                    refined_maximum_errors,
                    maximum_errors,
                )
                and maximum_refined_state_difference < 2.0e-9
                and all(value < 3.0e-9 for value in refined_maximum_errors)
            )
    checks = {
        "filesPresent": history_path.is_file() and summary_path.is_file(),
        "schemaVersion": summary.get("schemaVersion") == 1,
        "studyAndDimensions": summary.get("study") == "einstein-spinor-44"
        and summary.get("stateDimension") == 18
        and summary.get("baseDimension") == 8
        and summary.get("signature") == [4, 4],
        "fixtureHashes": summary.get("cl44FixtureSha256")
        == sha256_file(clifford_path)
        and summary.get("geometryFixtureSha256")
        == sha256_file(geometry_path),
        "parameters": all(
            close(summary.get("parameters", {}).get(name, math.nan), value)
            for name, value in expected_parameters.items()
        ),
        "csvHeader": list(rows[0]) == expected_fields if rows else False,
        "sampleCount": len(rows) == summary.get("sampleCount") == 171,
        "timeGrid": len(times) == 171
        and all(
            close(time, T_MIN + index * OUTPUT_STEP, 1.0e-13)
            for index, time in enumerate(times)
        )
        and close(times[-1], T_MAX),
        "presentEpochOnce": sum(abs(time) <= 1.0e-15 for time in times) == 1,
        "finiteValues": all(
            math.isfinite(float(value))
            for row in rows
            for value in row.values()
        ),
        "initialData": bool(rows)
        and close(scales[20], 1.0)
        and close(hubbles[20], 1.0)
        and close(spinors[20][0], 1.0)
        and close(spinors[20][15], 0.5)
        and all(
            close(spinors[20][index], 0.0)
            for index in range(1, 15)
        ),
        "recordedDerivedValues": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                stored_values, recomputed_values, strict=True
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ),
        "recordedErrors": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                stored_errors, recomputed_errors, strict=True
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ),
        "positiveCondensateDomain": all(
            scale_factor > 0.0 and values[0] > 0.0
            for scale_factor, values in zip(
                scales, recomputed_values, strict=True
            )
        ),
        "errorLimits": all(value <= 1.0e-8 for value in maximum_errors),
        "summaryErrors": all(
            close(stored, calculated)
            for stored, calculated in zip(
                [
                    summary_errors.get("condensate", math.nan),
                    summary_errors.get("density", math.nan),
                    summary_errors.get("friedmann", math.nan),
                ],
                maximum_errors,
                strict=True,
            )
        ),
        "transition": transition is not None
        and close(
            summary.get("accelerationTransitionTime", math.nan),
            transition[0],
        )
        and close(
            summary.get("accelerationTransitionScaleFactor", math.nan),
            transition[1],
        )
        and 0.8 < transition[1] < 0.9,
        "finiteDifferenceOdeResiduals": maximum_component_rms < 1.0e-3,
        "finiteDifferenceSpatialEinstein": maximum_spatial_error < 1.0e-6,
        "darkSectorFractions": all(
            close(values[4] + values[5], 1.0) for values in recomputed_values
        ),
        "canonicalHashes": sha256_file(history_path)
        == EXPECTED_HISTORY_SHA256
        and sha256_file(summary_path) == EXPECTED_SUMMARY_SHA256,
        "summaryVerdict": summary.get("solverSteps") == 1372
        and summary.get("rhsEvaluations") == 1486
        and summary.get("verdict") == "SUCCESS",
    }
    if repeat_compared:
        checks["repeatByteIdentity"] = repeat_equal
    if refined_compared:
        checks["refinedConvergence"] = refined_convergence
    return {
        "checks": checks,
        "measurements": {
            "sampleCount": len(rows),
            "solverSteps": summary.get("solverSteps"),
            "rhsEvaluations": summary.get("rhsEvaluations"),
            "maximumRelativeErrors": maximum_errors,
            "componentOdeRms": component_rms,
            "maximumComponentOdeRms": maximum_component_rms,
            "maximumSpatialEinsteinFiniteDifferenceError": (
                maximum_spatial_error
            ),
            "transition": transition,
            "historySha256": sha256_file(history_path),
            "summarySha256": sha256_file(summary_path),
            "repeatCompared": repeat_compared,
            "refinedCompared": refined_compared,
            "maximumRefinedStateDifference": (
                maximum_refined_state_difference
            ),
            "refinedMaximumRelativeErrors": refined_maximum_errors,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_output(
        arguments.output.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        arguments.refined.resolve() if arguments.refined else None,
        arguments.geometry_fixture.resolve(),
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
    expected_check_count = (
        EXPECTED_CHECK_COUNT
        + int(arguments.repeat is not None)
        + int(arguments.refined is not None)
    )
    if len(report["checks"]) != expected_check_count:
        print(f"ERROR: expected {expected_check_count} checks")
        return 1
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
