#!/usr/bin/env python3
"""Independently verify the Weitzenbock Einstein-spinor solution."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_CHECK_COUNT = 32
EXPECTED_HISTORY_SHA256 = (
    "c88ed61cafa59ea0d7693da41527c7b4486ded7cc09ac680b4f20f893d42b62a"
)
EXPECTED_SUMMARY_SHA256 = (
    "d03a90539887702ad6bdbe0ee3a5d783094b052609fc0e4d2b761a12b97fa6c8"
)
TRANSVERSE_DIMENSION = 7.0
TORSION_SCALAR_COEFFICIENT = 42.0
RICCI_RATE_COEFFICIENT = 14.0
RICCI_HUBBLE_COEFFICIENT = 56.0
BOUNDARY_RATE_COEFFICIENT = 14.0
BOUNDARY_HUBBLE_COEFFICIENT = 98.0
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
        default=Path("artifacts/weitzenbock-spinor-44"),
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--refined", type=Path)
    parser.add_argument(
        "--weitzenbock-fixture",
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
    parser.add_argument(
        "--baseline-output",
        type=Path,
        default=Path("artifacts/einstein-spinor-44"),
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
    hubble_rate = -KAPPA_8 / 6.0 * (density + pressure)
    acceleration = hubble * hubble + hubble_rate
    return (
        [
            condensate,
            density,
            pressure,
            pressure / density,
            MASS_COEFFICIENT * condensate / density,
            interaction / density,
            acceleration,
        ],
        [
            relative_error(condensate, expected_condensate),
            relative_error(density, expected_density),
            relative_error(hubble * hubble, density),
        ],
    )


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
    pressure = (SELF_EXPONENT - 1.0) * interaction
    potential_rate = (
        MASS_COEFFICIENT
        + SELF_COEFFICIENT
        * SELF_EXPONENT
        * condensate ** (SELF_EXPONENT - 1.0)
    )
    trace = TRANSVERSE_DIMENSION * hubble
    gamma_spinor = [
        sum(time_gamma[row][column] * spinor[column] for column in range(16))
        for row in range(16)
    ]
    return [
        scale_factor * hubble,
        -KAPPA_8 / 6.0 * (density + pressure),
        *[
            -0.5 * trace * spinor[index]
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


def teleparallel_values(
    hubble: float,
    density: float,
    pressure: float,
) -> list[float]:
    hubble_rate = -KAPPA_8 / 6.0 * (density + pressure)
    trace = TRANSVERSE_DIMENSION * hubble
    torsion = TORSION_SCALAR_COEFFICIENT * hubble * hubble
    ricci = (
        RICCI_RATE_COEFFICIENT * hubble_rate
        + RICCI_HUBBLE_COEFFICIENT * hubble * hubble
    )
    boundary = (
        BOUNDARY_RATE_COEFFICIENT * hubble_rate
        + BOUNDARY_HUBBLE_COEFFICIENT * hubble * hubble
    )
    return [
        hubble_rate,
        trace,
        torsion,
        ricci,
        boundary,
        ricci + torsion - boundary,
        trace / 2.0 - TRANSVERSE_DIMENSION * hubble / 2.0,
    ]


def read_rows(directory: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    summary = json.loads(
        (directory / "summary.json").read_text(encoding="utf-8")
    )
    with (directory / "history.csv").open(
        "r", encoding="utf-8", newline=""
    ) as source:
        rows = list(csv.DictReader(source))
    return summary, rows


def expected_fields() -> list[str]:
    return [
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
        "Hdot",
        "torsion_trace_time",
        "torsion_scalar",
        "levi_civita_ricci_scalar",
        "boundary_term",
        "boundary_identity_residual",
        "dirac_equivalence_residual",
        "S_relative_error",
        "density_relative_error",
        "friedmann_relative_error",
    ]


def maximum_state_difference(
    rows: list[dict[str, str]],
    comparison: list[dict[str, str]],
) -> float:
    state_fields = ["a", "H", *[f"psi{index}" for index in range(16)]]
    return max(
        abs(float(row[field]) - float(other[field]))
        / max(1.0, abs(float(row[field])), abs(float(other[field])))
        for row, other in zip(rows, comparison, strict=True)
        for field in state_fields
    )


def verify_output(
    output_directory: Path,
    repeat_directory: Path | None,
    refined_directory: Path | None,
    weitzenbock_path: Path,
    curved_path: Path,
    clifford_path: Path,
    baseline_directory: Path,
    *,
    require_canonical_hash: bool = True,
) -> dict[str, Any]:
    history_path = output_directory / "history.csv"
    summary_path = output_directory / "summary.json"
    summary, rows = read_rows(output_directory)
    weitzenbock = json.loads(weitzenbock_path.read_text(encoding="utf-8"))
    curved = json.loads(curved_path.read_text(encoding="utf-8"))
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    charge: list[list[int]] = curved["spinorBilinear"]["matrix"]
    time_gamma: list[list[int]] = clifford["generators"][4]
    fields = expected_fields()
    times = [float(row["t"]) for row in rows]
    scales = [float(row["a"]) for row in rows]
    hubbles = [float(row["H"]) for row in rows]
    spinors = [
        [float(row[f"psi{index}"]) for index in range(16)]
        for row in rows
    ]
    matter_names = (
        "S",
        "rho",
        "pressure",
        "w",
        "dust_like_fraction",
        "negative_pressure_fraction",
        "acceleration",
    )
    error_names = (
        "S_relative_error",
        "density_relative_error",
        "friedmann_relative_error",
    )
    teleparallel_names = (
        "Hdot",
        "torsion_trace_time",
        "torsion_scalar",
        "levi_civita_ricci_scalar",
        "boundary_term",
        "boundary_identity_residual",
        "dirac_equivalence_residual",
    )
    stored_matter = [
        [float(row[name]) for name in matter_names] for row in rows
    ]
    stored_errors = [
        [float(row[name]) for name in error_names] for row in rows
    ]
    stored_teleparallel = [
        [float(row[name]) for name in teleparallel_names] for row in rows
    ]
    recomputed = [
        derived_values(scale_factor, hubble, spinor, charge)
        for scale_factor, hubble, spinor in zip(
            scales, hubbles, spinors, strict=True
        )
    ]
    recomputed_matter = [value[0] for value in recomputed]
    recomputed_errors = [value[1] for value in recomputed]
    recomputed_teleparallel = [
        teleparallel_values(hubble, values[1], values[2])
        for hubble, values in zip(
            hubbles, recomputed_matter, strict=True
        )
    ]
    maximum_errors = [
        max(values[index] for values in recomputed_errors)
        for index in range(3)
    ]
    maximum_boundary = max(
        abs(values[5]) for values in recomputed_teleparallel
    )
    maximum_dirac = max(
        abs(values[6]) for values in recomputed_teleparallel
    )

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
        expected_rhs = rhs_values(
            states[index], charge, time_gamma
        )
        for component in range(18):
            residual = derivative[component] - expected_rhs[component]
            component_squared_errors[component] += residual * residual
        density = recomputed_matter[index][1]
        pressure = recomputed_matter[index][2]
        spatial_residual = (
            6.0 * derivative[1]
            + 21.0 * hubbles[index] * hubbles[index]
            + KAPPA_8 * pressure
        )
        spatial_errors.append(
            abs(spatial_residual)
            / max(KAPPA_8 * density, 1.0e-300)
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

    _, baseline_rows = read_rows(baseline_directory)
    state_names = ["t", "a", "H", *[f"psi{index}" for index in range(16)]]
    baseline_state_equal = len(rows) == len(baseline_rows) and all(
        row[name] == other[name]
        for row, other in zip(rows, baseline_rows, strict=True)
        for name in state_names
    )
    summary_errors = summary.get("maximumRelativeError", {})
    diagnostics = summary.get("darkSectorDiagnostics", {})
    present_index = next(
        (index for index, time in enumerate(times) if abs(time) <= 1.0e-15),
        None,
    )
    expected_parameters = {
        "kappa8": KAPPA_8,
        "massCoefficient": MASS_COEFFICIENT,
        "selfCoefficient": SELF_COEFFICIENT,
        "selfExponent": SELF_EXPONENT,
    }
    interpretation = summary.get("interpretation", {})
    canonical_hashes = (
        sha256_file(history_path) == EXPECTED_HISTORY_SHA256
        and sha256_file(summary_path) == EXPECTED_SUMMARY_SHA256
    )
    checks = {
        "filesPresent": history_path.is_file() and summary_path.is_file(),
        "schemaVersion": summary.get("schemaVersion") == 1,
        "studyAndDimensions": summary.get("study")
        == "weitzenbock-spinor-44"
        and summary.get("stateDimension") == 18
        and summary.get("baseDimension") == 8
        and summary.get("signature") == [4, 4],
        "connectionDescription": summary.get("connection")
        == "flat inertial Spin(4,4) connection in diagonal Weitzenbock gauge",
        "fixtureHashes": summary.get("cl44FixtureSha256")
        == sha256_file(clifford_path)
        and summary.get("curvedGeometryFixtureSha256")
        == sha256_file(curved_path)
        and summary.get("weitzenbockGeometryFixtureSha256")
        == sha256_file(weitzenbock_path),
        "parameters": all(
            close(
                summary.get("parameters", {}).get(name, math.nan), value
            )
            for name, value in expected_parameters.items()
        ),
        "csvHeader": bool(rows) and list(rows[0]) == fields,
        "sampleCount": len(rows) == summary.get("sampleCount") == 171,
        "timeGrid": len(times) == 171
        and all(
            close(
                time,
                T_MIN + index * OUTPUT_STEP,
                1.0e-13,
            )
            for index, time in enumerate(times)
        )
        and close(times[-1], T_MAX),
        "presentEpochOnce": sum(abs(time) <= 1.0e-15 for time in times) == 1,
        "finiteValues": all(
            math.isfinite(float(value))
            for row in rows
            for value in row.values()
        ),
        "initialData": present_index is not None
        and close(scales[present_index], 1.0)
        and close(hubbles[present_index], 1.0)
        and close(spinors[present_index][0], 1.0)
        and close(spinors[present_index][15], 0.5),
        "recordedMatterValues": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                stored_matter, recomputed_matter, strict=True
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ),
        "recordedMatterErrors": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                stored_errors, recomputed_errors, strict=True
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ),
        "recordedTeleparallelValues": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                stored_teleparallel,
                recomputed_teleparallel,
                strict=True,
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ),
        "summaryErrors": all(
            close(stored, calculated)
            for stored, calculated in zip(
                [
                    summary_errors.get("condensate", math.nan),
                    summary_errors.get("density", math.nan),
                    summary_errors.get("friedmann", math.nan),
                    summary_errors.get(
                        "teleparallelBoundaryIdentityAbsolute", math.nan
                    ),
                    summary_errors.get(
                        "homogeneousDiracEquivalenceAbsolute", math.nan
                    ),
                ],
                [
                    *maximum_errors,
                    maximum_boundary,
                    maximum_dirac,
                ],
                strict=True,
            )
        ),
        "positiveDomain": all(
            scale_factor > 0.0 and values[0] > 0.0
            for scale_factor, values in zip(
                scales, recomputed_matter, strict=True
            )
        ),
        "errorLimits": all(value <= 1.0e-8 for value in maximum_errors),
        "flatTorsionful": all(
            weitzenbock.get("checks", {}).get(name) is True
            for name in ("curvatureZero", "torsionNonzero")
        )
        and max(abs(values[2]) for values in recomputed_teleparallel) > 1.0,
        "boundaryIdentity": maximum_boundary <= 1.0e-12,
        "diracEquivalence": maximum_dirac == 0.0,
        "connectionFixture": all(weitzenbock.get("checks", {}).values()),
        "teleparallelFriedmann": max(
            relative_error(values[2] / 42.0, matter[1])
            for values, matter in zip(
                recomputed_teleparallel, recomputed_matter, strict=True
            )
        )
        <= 1.0e-8,
        "transition": transition is not None
        and close(
            summary.get("accelerationTransitionTime", math.nan),
            transition[0],
        )
        and close(
            summary.get("accelerationTransitionScaleFactor", math.nan),
            transition[1],
        ),
        "finiteDifferenceOdeResiduals": maximum_component_rms < 1.0e-3,
        "finiteDifferenceSpatialEinstein": maximum_spatial_error < 1.0e-6,
        "darkSectorFractions": all(
            close(values[4] + values[5], 1.0)
            for values in recomputed_matter
        ),
        "darkSectorSummary": present_index is not None
        and all(
            close(stored, calculated)
            for stored, calculated in zip(
                [
                    diagnostics.get("presentEquationOfState", math.nan),
                    diagnostics.get("presentDustLikeFraction", math.nan),
                    diagnostics.get(
                        "presentNegativePressureFraction", math.nan
                    ),
                    diagnostics.get("finalEquationOfState", math.nan),
                    diagnostics.get("finalDustLikeFraction", math.nan),
                    diagnostics.get(
                        "finalNegativePressureFraction", math.nan
                    ),
                ],
                [
                    recomputed_matter[present_index][3],
                    recomputed_matter[present_index][4],
                    recomputed_matter[present_index][5],
                    recomputed_matter[-1][3],
                    recomputed_matter[-1][4],
                    recomputed_matter[-1][5],
                ],
                strict=True,
            )
        ),
        "interpretationBounds": interpretation.get("observationalClaim")
        is False
        and "not an additional dark component"
        in interpretation.get("torsionSector", ""),
        "canonicalStateAgreement": baseline_state_equal,
        "canonicalHashes": not require_canonical_hash or canonical_hashes,
        "summaryVerdict": summary.get("solverSteps") == 1372
        and summary.get("rhsEvaluations") == 1486
        and summary.get("verdict") == "SUCCESS",
    }

    repeat_compared = repeat_directory is not None
    if repeat_directory is not None:
        checks["repeatByteIdentity"] = all(
            (output_directory / name).read_bytes()
            == (repeat_directory / name).read_bytes()
            for name in ("history.csv", "summary.json")
        )
    refined_compared = refined_directory is not None
    refined_state_difference: float | None = None
    if refined_directory is not None:
        refined_summary, refined_rows = read_rows(refined_directory)
        refined_state_difference = maximum_state_difference(rows, refined_rows)
        refined_spinors = [
            [float(row[f"psi{index}"]) for index in range(16)]
            for row in refined_rows
        ]
        refined_recomputed = [
            derived_values(
                float(row["a"]),
                float(row["H"]),
                spinor,
                charge,
            )
            for row, spinor in zip(
                refined_rows, refined_spinors, strict=True
            )
        ]
        refined_errors = [
            max(values[1][index] for values in refined_recomputed)
            for index in range(3)
        ]
        refined_matter = [values[0] for values in refined_recomputed]
        refined_teleparallel = [
            teleparallel_values(
                float(row["H"]),
                matter[1],
                matter[2],
            )
            for row, matter in zip(
                refined_rows, refined_matter, strict=True
            )
        ]
        refined_stored_teleparallel = [
            [float(row[name]) for name in teleparallel_names]
            for row in refined_rows
        ]
        refined_boundary_error = max(
            abs(values[5]) for values in refined_teleparallel
        )
        refined_dirac_error = max(
            abs(values[6]) for values in refined_teleparallel
        )
        refined_summary_errors = refined_summary.get(
            "maximumRelativeError", {}
        )
        refined_teleparallel_valid = all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                refined_stored_teleparallel,
                refined_teleparallel,
                strict=True,
            )
            for stored, calculated in zip(
                stored_row, calculated_row, strict=True
            )
        ) and all(
            close(stored, calculated)
            for stored, calculated in zip(
                [
                    refined_summary_errors.get("condensate", math.nan),
                    refined_summary_errors.get("density", math.nan),
                    refined_summary_errors.get("friedmann", math.nan),
                    refined_summary_errors.get(
                        "teleparallelBoundaryIdentityAbsolute", math.nan
                    ),
                    refined_summary_errors.get(
                        "homogeneousDiracEquivalenceAbsolute", math.nan
                    ),
                ],
                [
                    *refined_errors,
                    refined_boundary_error,
                    refined_dirac_error,
                ],
                strict=True,
            )
        )
        checks["refinedConvergence"] = (
            len(refined_rows) == len(rows)
            and list(refined_rows[0]) == fields
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
            and refined_teleparallel_valid
            and refined_boundary_error <= 1.0e-12
            and refined_dirac_error == 0.0
            and refined_state_difference < 2.0e-9
            and all(
                refined < canonical
                for refined, canonical in zip(
                    refined_errors, maximum_errors, strict=True
                )
            )
        )
    return {
        "checks": checks,
        "measurements": {
            "sampleCount": len(rows),
            "maximumRelativeErrors": maximum_errors,
            "maximumBoundaryIdentityResidual": maximum_boundary,
            "maximumDiracEquivalenceResidual": maximum_dirac,
            "maximumComponentOdeRms": maximum_component_rms,
            "maximumSpatialEinsteinFiniteDifferenceError": (
                maximum_spatial_error
            ),
            "maximumBaselineStateDifference": maximum_state_difference(
                rows, baseline_rows
            ),
            "historySha256": sha256_file(history_path),
            "summarySha256": sha256_file(summary_path),
            "repeatCompared": repeat_compared,
            "refinedCompared": refined_compared,
            "maximumRefinedStateDifference": refined_state_difference,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_output(
        arguments.output.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        arguments.refined.resolve() if arguments.refined else None,
        arguments.weitzenbock_fixture.resolve(),
        arguments.curved_fixture.resolve(),
        arguments.clifford_fixture.resolve(),
        arguments.baseline_output.resolve(),
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
    expected = EXPECTED_CHECK_COUNT + int(arguments.repeat is not None)
    expected += int(arguments.refined is not None)
    if len(report["checks"]) != expected:
        print(f"ERROR: expected {expected} checks")
        return 1
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
