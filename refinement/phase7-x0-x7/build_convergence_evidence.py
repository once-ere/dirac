#!/usr/bin/env python3
"""Record deterministic replay and refined-convergence evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).resolve().with_name("convergence.json")
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts import check_einstein_spinor_44  # noqa: E402


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canonical",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts/einstein-spinor-44",
    )
    parser.add_argument(
        "--repeat",
        type=Path,
        default=REPOSITORY_ROOT / "build/phase7/einstein-spinor-repeat",
    )
    parser.add_argument(
        "--refined",
        type=Path,
        default=REPOSITORY_ROOT / "build/phase7/einstein-spinor-refined",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_record(directory: Path) -> dict[str, Any]:
    summary_path = directory / "summary.json"
    history_path = directory / "history.csv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return {
        "historySha256": sha256_file(history_path),
        "summarySha256": sha256_file(summary_path),
        "relativeTolerance": summary["relativeTolerance"],
        "absoluteTolerance": summary["absoluteTolerance"],
        "maximumStep": summary["maximumStep"],
        "sampleCount": summary["sampleCount"],
        "solverSteps": summary["solverSteps"],
        "rhsEvaluations": summary["rhsEvaluations"],
        "maximumRelativeError": summary["maximumRelativeError"],
        "verdict": summary["verdict"],
    }


def build_report(
    canonical: Path,
    repeat: Path,
    refined: Path,
) -> dict[str, Any]:
    verification = check_einstein_spinor_44.verify_output(
        canonical,
        repeat,
        refined,
        REPOSITORY_ROOT / "artifacts/curved-spin-geometry/geometry.json",
        REPOSITORY_ROOT / "artifacts/exact/cl44-seed.json",
    )
    transition = verification["measurements"].get("transition")
    if transition is not None:
        verification["measurements"]["transition"] = list(transition)
    return {
        "schemaVersion": 1,
        "canonical": artifact_record(canonical),
        "repeat": artifact_record(repeat),
        "refined": artifact_record(refined),
        "independentVerification": verification,
    }


def main() -> int:
    arguments = parse_arguments()
    report = build_report(
        arguments.canonical.resolve(),
        arguments.repeat.resolve(),
        arguments.refined.resolve(),
    )
    failures = [
        name
        for name, passed in report["independentVerification"]["checks"].items()
        if not passed
    ]
    output_path = arguments.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"output={output_path}")
    print(f"output_sha256={sha256_file(output_path)}")
    print(f"check_count={len(report['independentVerification']['checks'])}")
    print(f"failed_check_count={len(failures)}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())