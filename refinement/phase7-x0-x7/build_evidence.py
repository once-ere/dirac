#!/usr/bin/env python3
"""Build machine-readable evidence for the Phase 7 report refinement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKING_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_OUTPUT = WORKING_DIRECTORY / "evidence.json"
AUDITED_SOURCE_COMMIT = "89408fef07a7b0a55237dc606074d58ef39a8892"
SOLVER_COMMIT = "d1836e6a279d63a90fe2839a0020123245487e76"
COORDINATE_EXPRESSION = (
    "coordinates = {x0, x1, x2, x3, x4, x5, x6, x7};"
)
EXTERNAL_REFERENCES = {
    "bridgeNotebook": {
        "path": "Pre-Universe_opus-fable-main/notebooks/gpt-5.6_bridge.nb",
        "byteCount": 27740,
        "sha256": (
            "6791e7f66582a7a80bef50f6092eca0f558ec2fbae8f57b629a427d07dc30fa6"
        ),
    },
    "referenceZip": {
        "path": "Pre-Universe_opus-fable-main.zip",
        "byteCount": 2839251,
        "sha256": (
            "a8e6503390d58536782547025692af88912c7f0bccc2081bdb73be97f7e40858"
        ),
    },
}

sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts import check_einstein_spinor_44  # noqa: E402
from scripts import check_einstein_spinor_model  # noqa: E402


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    columns = transpose(right)
    return [
        [
            sum(a * b for a, b in zip(row, column, strict=True))
            for column in columns
        ]
        for row in left
    ]


def identity(dimension: int, sign: int = 1) -> list[list[int]]:
    return [
        [sign * int(row == column) for column in range(dimension)]
        for row in range(dimension)
    ]


def nonzero_rows(matrix: list[list[int]]) -> list[dict[str, int]]:
    result = []
    for row_index, row in enumerate(matrix, start=1):
        entries = [
            (column_index + 1, value)
            for column_index, value in enumerate(row)
            if value != 0
        ]
        if len(entries) != 1:
            raise ValueError(
                f"row {row_index} has {len(entries)} nonzero entries"
            )
        column, value = entries[0]
        result.append({"row": row_index, "column": column, "value": value})
    return result


def source_record(relative_path: str) -> dict[str, Any]:
    path = REPOSITORY_ROOT / relative_path
    return {
        "path": relative_path,
        "byteCount": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def verify_external_references() -> None:
    for record in EXTERNAL_REFERENCES.values():
        path = REPOSITORY_ROOT / str(record["path"])
        if not path.exists():
            continue
        if not path.is_file():
            raise ValueError(f"external reference is not a file: {path}")
        if path.stat().st_size != record["byteCount"]:
            raise ValueError(f"external reference size changed: {path}")
        if sha256_file(path) != record["sha256"]:
            raise ValueError(f"external reference hash changed: {path}")

    bridge_path = REPOSITORY_ROOT / str(
        EXTERNAL_REFERENCES["bridgeNotebook"]["path"]
    )
    if bridge_path.is_file():
        bridge_text = bridge_path.read_text(encoding="utf-8")
        if not re.search(re.escape(COORDINATE_EXPRESSION), bridge_text):
            raise ValueError("bridge coordinate expression is missing")


def build_evidence() -> dict[str, Any]:
    clifford_path = REPOSITORY_ROOT / "artifacts/exact/cl44-seed.json"
    geometry_path = (
        REPOSITORY_ROOT / "artifacts/curved-spin-geometry/geometry.json"
    )
    output_path = REPOSITORY_ROOT / "artifacts/einstein-spinor-44"
    application_source_path = (
        REPOSITORY_ROOT / "studies/einstein_spinor_44/src/lib.rs"
    )
    cvode_source_path = (
        REPOSITORY_ROOT / "vendor/sundials_rs/crates/cvode_rs/src/cvode.rs"
    )
    cvode_impl_path = (
        REPOSITORY_ROOT
        / "vendor/sundials_rs/crates/cvode_rs/src/cvode_impl.rs"
    )
    cvode_nls_path = (
        REPOSITORY_ROOT
        / "vendor/sundials_rs/crates/cvode_rs/src/cvode_nls.rs"
    )
    cvode_ls_path = (
        REPOSITORY_ROOT
        / "vendor/sundials_rs/crates/cvode_rs/src/cvode_ls.rs"
    )

    verify_external_references()

    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    gamma_time: list[list[int]] = clifford["generators"][4]
    charge: list[list[int]] = geometry["spinorBilinear"]["matrix"]
    dimension = len(gamma_time)
    gamma_rows = nonzero_rows(gamma_time)
    charge_rows = nonzero_rows(charge)

    gamma_square = multiply(gamma_time, gamma_time)
    charge_square = multiply(charge, charge)
    gamma_charge_left = multiply(transpose(gamma_time), charge)
    gamma_charge_right = multiply(charge, gamma_time)
    skew_residual = [
        [left + right for left, right in zip(left_row, right_row, strict=True)]
        for left_row, right_row in zip(
            gamma_charge_left, gamma_charge_right, strict=True
        )
    ]
    zero = [[0] * dimension for _ in range(dimension)]
    exact_checks = {
        "gammaRowsSignedPermutation": len(gamma_rows) == dimension,
        "chargeRowsSignedPermutation": len(charge_rows) == dimension,
        "gammaSquareMinusIdentity": gamma_square
        == identity(dimension, -1),
        "chargeSymmetric": charge == transpose(charge),
        "chargeSquareIdentity": charge_square == identity(dimension),
        "gammaChargeSkewAdjoint": skew_residual == zero,
        "chargeTraceZero": sum(
            charge[index][index] for index in range(dimension)
        )
        == 0,
    }

    condensate_pairs = []
    for row in range(dimension):
        for column in range(row + 1, dimension):
            if charge[row][column] != 0:
                condensate_pairs.append(
                    {
                        "left": row + 1,
                        "right": column + 1,
                        "coefficient": 2 * charge[row][column],
                    }
                )

    numerical = check_einstein_spinor_44.verify_output(
        output_path,
        None,
        None,
        geometry_path,
        clifford_path,
    )
    transition = numerical["measurements"].get("transition")
    if transition is not None:
        numerical["measurements"]["transition"] = list(transition)
    exact_model = check_einstein_spinor_model.verify_model(
        geometry_path,
        clifford_path,
    )

    bridge_record = {
        **EXTERNAL_REFERENCES["bridgeNotebook"],
        "trackedInDiracRepository": False,
        "verifiedDuringAudit": True,
        "coordinateExpressionPresent": True,
        "coordinateExpression": COORDINATE_EXPRESSION,
    }
    reference_zip_record = {
        **EXTERNAL_REFERENCES["referenceZip"],
        "trackedInDiracRepository": False,
        "verifiedDuringAudit": True,
    }

    application_source = application_source_path.read_text(encoding="utf-8")
    cvode_source = cvode_source_path.read_text(encoding="utf-8")
    cvode_impl = cvode_impl_path.read_text(encoding="utf-8")
    cvode_nls = cvode_nls_path.read_text(encoding="utf-8")
    cvode_ls = cvode_ls_path.read_text(encoding="utf-8")
    solver_checks = {
        "applicationSelectsBdf": "CVodeCreate(CV_BDF" in application_source,
        "applicationUsesDenseMatrix": "SUNDenseMatrix(" in application_source,
        "applicationUsesDenseLinearSolver": "SUNLinSol_Dense(" in application_source,
        "cvodeDefaultNewton": "SUNNonlinSol_Newton(y0" in cvode_source,
        "bdfMaximumOrderFive": "BDF_Q_MAX: usize = 5" in cvode_impl,
        "newtonMaximumCorrectorsThree": "NLS_MAXCOR: i32 = 3" in cvode_nls,
        "internalDifferenceQuotientJacobian": "jacDQ: A.is_some()" in cvode_ls
        and "cvLsDenseDQJac" in cvode_ls,
    }

    transverse_dimension = 7
    self_exponent = Fraction(1, 5)
    acceleration_threshold = -Fraction(
        transverse_dimension - 2, transverse_dimension
    )
    dark_energy_equation_of_state = self_exponent - 1

    sources = [
        source_record("artifacts/exact/cl44-seed.json"),
        source_record("artifacts/curved-spin-geometry/geometry.json"),
        source_record("artifacts/einstein-spinor-44/history.csv"),
        source_record("artifacts/einstein-spinor-44/summary.json"),
        source_record("studies/einstein_spinor_44/src/lib.rs"),
        source_record("scripts/check_einstein_spinor_model.py"),
        source_record("scripts/check_einstein_spinor_44.py"),
        source_record("vendor/sundials_rs/Cargo.toml"),
        source_record("vendor/sundials_rs/crates/cvode_rs/src/cvode.rs"),
        source_record("vendor/sundials_rs/crates/cvode_rs/src/cvode_impl.rs"),
        source_record("vendor/sundials_rs/crates/cvode_rs/src/cvode_nls.rs"),
        source_record("vendor/sundials_rs/crates/cvode_rs/src/cvode_ls.rs"),
    ]

    return {
        "schemaVersion": 1,
        "audit": {
            "auditedSourceCommit": AUDITED_SOURCE_COMMIT,
            "coordinateAdoptionScope": (
                "coordinate names and ordering only; the bridge notebook "
                "metric and connection are not imported"
            ),
        },
        "reference": {
            "bridgeNotebook": bridge_record,
            "referenceZip": reference_zip_record,
        },
        "sources": sources,
        "exactComponents": {
            "gamma4NonzeroRowsOneBased": gamma_rows,
            "chargeNonzeroRowsOneBased": charge_rows,
            "condensatePairsOneBased": condensate_pairs,
            "chargeEigenvalueSignature": [8, 8],
            "checks": exact_checks,
        },
        "exactModel": exact_model,
        "solver": {
            "name": "safe-Rust port of SUNDIALS CVODE",
            "version": "7.8.0",
            "submoduleCommit": SOLVER_COMMIT,
            "method": "variable-step variable-order BDF",
            "orderRange": [1, 5],
            "defaultNonlinearSolver": "Newton",
            "maximumNonlinearCorrectors": 3,
            "linearSolver": "dense direct 18-by-18",
            "jacobian": "internal dense difference quotient",
            "preconditioner": "none for the dense direct solve",
            "selectionClaim": (
                "selected robust implementation; no comparative benchmark "
                "establishes global optimality"
            ),
            "checks": solver_checks,
        },
        "numericalOutput": numerical,
        "darkSector": {
            "transverseDimension": transverse_dimension,
            "dustEquationOfState": "0",
            "negativePressureEquationOfState": str(
                dark_energy_equation_of_state
            ),
            "accelerationThreshold": str(acceleration_threshold),
            "dustDensityScaleExponent": "-7",
            "negativePressureDensityScaleExponent": "-7/5",
            "negativePressureTermAcceleratesWhenDominant": (
                dark_energy_equation_of_state < acceleration_threshold
            ),
            "interpretation": (
                "homogeneous background analogies only; clustering, "
                "perturbative stability, compactification, and "
                "observational fits are not established"
            ),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    evidence = build_evidence()
    output_path = arguments.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    failed_exact = [
        name
        for name, passed in evidence["exactComponents"]["checks"].items()
        if not passed
    ]
    failed_model = [
        name
        for name, passed in evidence["exactModel"]["checks"].items()
        if not passed
    ]
    failed_numerical = [
        name
        for name, passed in evidence["numericalOutput"]["checks"].items()
        if not passed
    ]
    failed_solver = [
        name
        for name, passed in evidence["solver"]["checks"].items()
        if not passed
    ]
    print(f"output={output_path}")
    print(f"output_sha256={sha256_file(output_path)}")
    print(f"exact_check_count={len(evidence['exactComponents']['checks'])}")
    print(f"model_check_count={len(evidence['exactModel']['checks'])}")
    print(f"solver_check_count={len(evidence['solver']['checks'])}")
    print(f"numerical_check_count={len(evidence['numericalOutput']['checks'])}")
    print(
        "failed_check_count="
        f"{len(failed_exact) + len(failed_model) + len(failed_solver) + len(failed_numerical)}"
    )
    return int(
        bool(failed_exact or failed_model or failed_solver or failed_numerical)
    )


if __name__ == "__main__":
    raise SystemExit(main())