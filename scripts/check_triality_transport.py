#!/usr/bin/env python3
"""Validate triality-transport CSV/JSON output and deterministic replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_CHECK_COUNT = 15


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/triality-transport"),
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument(
        "--triality-fixture",
        type=Path,
        default=Path("artifacts/exact/triality44.json"),
    )
    parser.add_argument(
        "--split-fixture",
        type=Path,
        default=Path("artifacts/exact/split-octonion.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def split_norm(vector: list[float], metric: list[int]) -> float:
    return sum(sign * value * value for sign, value in zip(metric, vector, strict=True))


def trilinear(
    plus: list[float],
    minus: list[float],
    vector: list[float],
    para_tensor: list[list[list[int]]],
    metric: list[int],
) -> float:
    value = 0.0
    for left in range(8):
        for right in range(8):
            for output in range(8):
                value += (
                    plus[left]
                    * minus[right]
                    * para_tensor[left][right][output]
                    * metric[output]
                    * vector[output]
                )
    return value


def nearly_equal(left: float, right: float, tolerance: float = 1.0e-14) -> bool:
    return abs(left - right) <= tolerance


def verify_output(
    output_directory: Path,
    repeat_directory: Path | None,
    triality_fixture_path: Path,
    split_fixture_path: Path,
) -> dict[str, Any]:
    trajectory_path = output_directory / "trajectory.csv"
    summary_path = output_directory / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    split_fixture = json.loads(split_fixture_path.read_text(encoding="utf-8"))
    metric = [split_fixture["metric"][index][index] for index in range(8)]
    para_tensor = split_fixture["paraMultiplicationTensor"]

    with trajectory_path.open("r", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    expected_fields = [
        "t",
        *[f"y{index}" for index in range(24)],
        "norm_v",
        "norm_plus",
        "norm_minus",
        "trilinear",
    ]
    fields = list(rows[0]) if rows else []
    times = [float(row["t"]) for row in rows]
    states = [
        [float(row[f"y{index}"]) for index in range(24)]
        for row in rows
    ]
    recorded = [
        [
            float(row["norm_v"]),
            float(row["norm_plus"]),
            float(row["norm_minus"]),
            float(row["trilinear"]),
        ]
        for row in rows
    ]
    recomputed = [
        [
            split_norm(state[0:8], metric),
            split_norm(state[8:16], metric),
            split_norm(state[16:24], metric),
            trilinear(state[8:16], state[16:24], state[0:8], para_tensor, metric),
        ]
        for state in states
    ]
    initial = recomputed[0] if recomputed else [math.nan] * 4
    maximum_drift = [
        max(abs(values[index] - initial[index]) for values in recomputed)
        if recomputed
        else math.inf
        for index in range(4)
    ]
    summary_drift = summary.get("maximumDrift", {})
    summary_drift_values = [
        summary_drift.get("vectorNorm", math.nan),
        summary_drift.get("plusNorm", math.nan),
        summary_drift.get("minusNorm", math.nan),
        summary_drift.get("trilinear", math.nan),
    ]

    repeat_present = repeat_directory is not None
    repeat_equal = True
    if repeat_directory is not None:
        repeat_equal = all(
            (output_directory / name).read_bytes() == (repeat_directory / name).read_bytes()
            for name in ("trajectory.csv", "summary.json")
        )

    checks = {
        "filesPresent": trajectory_path.is_file() and summary_path.is_file(),
        "schemaVersion": summary.get("schemaVersion") == 1,
        "studyName": summary.get("study") == "triality-transport",
        "stateDimension": summary.get("stateDimension") == 24,
        "fixtureHashes": summary.get("trialityFixtureSha256")
        == sha256_file(triality_fixture_path)
        and summary.get("splitFixtureSha256") == sha256_file(split_fixture_path),
        "csvHeader": fields == expected_fields,
        "sampleCount": len(rows) == summary.get("sampleCount") == 41,
        "finiteValues": all(math.isfinite(value) for row in states for value in row)
        and all(math.isfinite(value) for row in recomputed for value in row),
        "timeGrid": len(times) == 41
        and all(nearly_equal(time, index / 10.0) for index, time in enumerate(times)),
        "initialInvariants": all(nearly_equal(value, 1.0) for value in initial),
        "recordedInvariants": all(
            nearly_equal(stored, calculated)
            for stored_row, calculated_row in zip(recorded, recomputed, strict=True)
            for stored, calculated in zip(stored_row, calculated_row, strict=True)
        ),
        "driftLimit": all(value <= 1.0e-8 for value in maximum_drift),
        "summaryDrift": all(
            nearly_equal(stored, calculated)
            for stored, calculated in zip(
                summary_drift_values,
                maximum_drift,
                strict=True,
            )
        ),
        "summaryVerdict": summary.get("verdict") == "SUCCESS",
        "repeatByteIdentity": not repeat_present or repeat_equal,
    }
    return {
        "checks": checks,
        "measurements": {
            "sampleCount": len(rows),
            "maximumDrift": maximum_drift,
            "trajectorySha256": sha256_file(trajectory_path),
            "summarySha256": sha256_file(summary_path),
            "repeatCompared": repeat_present,
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_output(
        arguments.output.resolve(),
        arguments.repeat.resolve() if arguments.repeat else None,
        arguments.triality_fixture.resolve(),
        arguments.split_fixture.resolve(),
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