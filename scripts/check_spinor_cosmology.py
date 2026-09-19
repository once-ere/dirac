#!/usr/bin/env python3
"""Validate spinor-cosmology CSV/JSON output and deterministic replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_CHECK_COUNT = 17
OMEGA_M0 = 0.305
OMEGA_R0 = 0.00009
OMEGA_PSI0 = 0.69491
W0 = -0.861
WA = -0.60


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/spinor-cosmology"),
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def analytic_density(e_fold: float) -> float:
    scale = math.exp(e_fold)
    exponent = -3.0 * (1.0 + W0 + WA) * e_fold - 3.0 * WA * (1.0 - scale)
    return OMEGA_PSI0 * math.exp(exponent)


def potential(condensate: float) -> float:
    scale = math.exp(-math.log(condensate) / 3.0)
    exponent = (1.0 + W0 + WA) * math.log(condensate) - 3.0 * WA * (1.0 - scale)
    return OMEGA_PSI0 * math.exp(exponent)


def relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), 1.0e-300)


def close(left: float, right: float, tolerance: float = 5.0e-13) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def verify_output(
    output_directory: Path,
    repeat_directory: Path | None,
    clifford_fixture_path: Path,
) -> dict[str, Any]:
    background_path = output_directory / "background.csv"
    summary_path = output_directory / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with background_path.open("r", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    expected_fields = [
        "N",
        "a",
        "tau",
        "rho",
        *[f"psi{index}" for index in range(16)],
        "S",
        "U",
        "w",
        "E",
        "S_relative_error",
        "rho_relative_error",
        "potential_relative_error",
        "friedmann_relative_error",
    ]
    fields = list(rows[0]) if rows else []
    e_folds = [float(row["N"]) for row in rows]
    scales = [float(row["a"]) for row in rows]
    densities = [float(row["rho"]) for row in rows]
    spinors = [
        [float(row[f"psi{index}"]) for index in range(16)]
        for row in rows
    ]
    recorded_derived = [
        [float(row[name]) for name in ("S", "U", "w", "E")]
        for row in rows
    ]
    recorded_errors = [
        [
            float(row["S_relative_error"]),
            float(row["rho_relative_error"]),
            float(row["potential_relative_error"]),
            float(row["friedmann_relative_error"]),
        ]
        for row in rows
    ]

    recomputed_derived: list[list[float]] = []
    recomputed_errors: list[list[float]] = []
    for e_fold, scale, density, spinor in zip(
        e_folds,
        scales,
        densities,
        spinors,
        strict=True,
    ):
        condensate = sum(value * value for value in spinor)
        reconstructed_potential = potential(condensate)
        expected_condensate = math.exp(-3.0 * e_fold)
        expected_density = analytic_density(e_fold)
        numerical_hubble_squared = (
            OMEGA_R0 * math.exp(-4.0 * e_fold)
            + OMEGA_M0 * math.exp(-3.0 * e_fold)
            + density
        )
        analytic_hubble_squared = (
            OMEGA_R0 * math.exp(-4.0 * e_fold)
            + OMEGA_M0 * math.exp(-3.0 * e_fold)
            + expected_density
        )
        recomputed_derived.append(
            [
                condensate,
                reconstructed_potential,
                W0 + WA * (1.0 - scale),
                math.sqrt(numerical_hubble_squared),
            ]
        )
        recomputed_errors.append(
            [
                relative_error(condensate, expected_condensate),
                relative_error(density, expected_density),
                relative_error(density, reconstructed_potential),
                relative_error(numerical_hubble_squared, analytic_hubble_squared),
            ]
        )

    maximum_errors = [
        max(values[index] for values in recomputed_errors)
        if recomputed_errors
        else math.inf
        for index in range(4)
    ]
    summary_errors = summary.get("maximumRelativeError", {})
    summary_error_values = [
        summary_errors.get("condensate", math.nan),
        summary_errors.get("density", math.nan),
        summary_errors.get("potential", math.nan),
        summary_errors.get("friedmann", math.nan),
    ]
    repeat_compared = repeat_directory is not None
    repeat_equal = True
    if repeat_directory is not None:
        repeat_equal = all(
            (output_directory / name).read_bytes() == (repeat_directory / name).read_bytes()
            for name in ("background.csv", "summary.json")
        )

    expected_parameters = {
        "omegaM0": OMEGA_M0,
        "omegaR0": OMEGA_R0,
        "omegaPsi0": OMEGA_PSI0,
        "w0": W0,
        "wa": WA,
    }
    checks = {
        "filesPresent": background_path.is_file() and summary_path.is_file(),
        "schemaVersion": summary.get("schemaVersion") == 1,
        "studyName": summary.get("study") == "real-spinor-cosmology",
        "stateDimension": summary.get("stateDimension") == 18,
        "fixtureHash": summary.get("cl44FixtureSha256")
        == sha256_file(clifford_fixture_path),
        "parameters": all(
            close(summary.get("parameters", {}).get(name, math.nan), value)
            for name, value in expected_parameters.items()
        ),
        "flatness": close(OMEGA_M0 + OMEGA_R0 + OMEGA_PSI0, 1.0),
        "csvHeader": fields == expected_fields,
        "sampleCount": len(rows) == summary.get("sampleCount") == 1201,
        "finiteValues": all(
            math.isfinite(float(value)) for row in rows for value in row.values()
        ),
        "eFoldGrid": len(e_folds) == 1201
        and all(close(value, -4.0 + index / 240.0, 1.0e-14) for index, value in enumerate(e_folds)),
        "presentEpochOnce": sum(abs(value) <= 1.0e-15 for value in e_folds) == 1,
        "recordedDerivedValues": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                recorded_derived,
                recomputed_derived,
                strict=True,
            )
            for stored, calculated in zip(stored_row, calculated_row, strict=True)
        ),
        "recordedErrors": all(
            close(stored, calculated)
            for stored_row, calculated_row in zip(
                recorded_errors,
                recomputed_errors,
                strict=True,
            )
            for stored, calculated in zip(stored_row, calculated_row, strict=True)
        ),
        "errorLimits": all(value <= 1.0e-8 for value in maximum_errors),
        "summaryErrors": all(
            close(stored, calculated)
            for stored, calculated in zip(
                summary_error_values,
                maximum_errors,
                strict=True,
            )
        )
        and summary.get("verdict") == "SUCCESS",
        "repeatByteIdentity": not repeat_compared or repeat_equal,
    }
    return {
        "checks": checks,
        "measurements": {
            "sampleCount": len(rows),
            "maximumRelativeErrors": maximum_errors,
            "backgroundSha256": sha256_file(background_path),
            "summarySha256": sha256_file(summary_path),
            "repeatCompared": repeat_compared,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_output(
        arguments.output.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        arguments.clifford_fixture.resolve(),
    )
    failures = [name for name, passed in report["checks"].items() if not passed]
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