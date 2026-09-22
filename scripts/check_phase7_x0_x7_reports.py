#!/usr/bin/env python3
"""Check the refined Phase 7 component and numerical reports semantically."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = (
    REPOSITORY_ROOT
    / "provenance"
    / "EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md"
)
NUMERICS_PATH = (
    REPOSITORY_ROOT
    / "provenance"
    / "EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md"
)
EVIDENCE_PATH = (
    REPOSITORY_ROOT / "refinement" / "phase7-x0-x7" / "evidence.json"
)
EVIDENCE_BUILDER_PATH = EVIDENCE_PATH.with_name("build_evidence.py")
CONVERGENCE_PATH = EVIDENCE_PATH.with_name("convergence.json")
EXPECTED_EVIDENCE_SHA256 = (
    "58373d6aeea90807a3f064f395b8367502ff3a280050a5c8823c9e0cc0b2eb0b"
)
EXPECTED_CONVERGENCE_SHA256 = (
    "9cf9e89a2326786e2573eafbf1ad1cdcb1528eeb540bfb102cbf5c6988a1ef76"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--components", type=Path, default=COMPONENTS_PATH)
    parser.add_argument("--numerics", type=Path, default=NUMERICS_PATH)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH)
    return parser.parse_args()


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latex_subscript(index: int) -> str:
    return str(index) if index < 10 else f"{{{index}}}"


def load_evidence_builder() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "phase7_build_evidence", EVIDENCE_BUILDER_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load Phase 7 evidence builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def all_nested_checks_pass(section: dict[str, Any]) -> bool:
    checks = section.get("checks", {})
    return bool(checks) and all(checks.values())


def verify_reports(
    components_path: Path = COMPONENTS_PATH,
    numerics_path: Path = NUMERICS_PATH,
    evidence_path: Path = EVIDENCE_PATH,
    convergence_path: Path = CONVERGENCE_PATH,
) -> dict[str, Any]:
    components = components_path.read_text(encoding="utf-8")
    numerics = numerics_path.read_text(encoding="utf-8")
    component_compact = compact(components)
    numerics_compact = compact(numerics)
    numerics_normalized = re.sub(r"\s+", " ", numerics)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    convergence = json.loads(convergence_path.read_text(encoding="utf-8"))
    rebuilt_evidence = load_evidence_builder().build_evidence()

    expected_metric = compact(
        r"g_{\mu\nu}=\operatorname{diag}\bigl("
        r"a(x4)^2,a(x4)^2,a(x4)^2,a(x4)^2,-1,"
        r"-a(x4)^2,-a(x4)^2,-a(x4)^2\bigr)"
    )
    condensate_terms = (
        r"\psi_1\psi_{16}",
        r"\psi_2\psi_{15}",
        r"-\psi_3\psi_{14}",
        r"-\psi_4\psi_{13}",
        r"+\psi_5\psi_{12}",
        r"+\psi_6\psi_{11}",
        r"-\psi_7\psi_{10}",
        r"-\psi_8\psi_9",
    )
    spinor_equations = []
    for index in range(1, 9):
        left = latex_subscript(index)
        right = latex_subscript(index + 8)
        spinor_equations.extend(
            [
                compact(
                    rf"\dot\psi_{left}&=-\frac72H\psi_{left}"
                    rf"-U\psi_{right}"
                ),
                compact(
                    rf"\dot\psi_{right}&=-\frac72H"
                    rf"\psi_{right}+U\psi_{left}"
                ),
            ]
        )
    diagonal_components = [f"E_{{{index}{index}}}:" for index in range(8)]
    off_diagonal_components = [
        f"E_{{{left}{right}}}"
        for left in range(8)
        for right in range(left + 1, 8)
    ]
    exact_measurements = (
        "7.44192091691309166\\times10^{-9}",
        "1.48948308787786630\\times10^{-9}",
        "1.20354325050525201\\times10^{-9}",
    )

    checks = {
        "evidenceHash": sha256_file(evidence_path) == EXPECTED_EVIDENCE_SHA256,
        "convergenceHash": sha256_file(convergence_path)
        == EXPECTED_CONVERGENCE_SHA256,
        "evidenceCanonical": evidence == rebuilt_evidence,
        "exactComponentEvidence": all_nested_checks_pass(
            evidence["exactComponents"]
        ),
        "exactModelEvidence": all_nested_checks_pass(evidence["exactModel"]),
        "solverEvidence": all_nested_checks_pass(evidence["solver"]),
        "numericalEvidence": all_nested_checks_pass(
            evidence["numericalOutput"]
        ),
        "convergenceEvidence": all_nested_checks_pass(
            convergence["independentVerification"]
        )
        and convergence["canonical"]["historySha256"]
        == convergence["repeat"]["historySha256"]
        and convergence["canonical"]["summarySha256"]
        == convergence["repeat"]["summarySha256"],
        "coordinateReference": (
            "coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}"
            in components
            and "Only the coordinate names and ordering are adopted"
            in components
        ),
        "covariantVersusHomogeneousScope": (
            "These are the unrestricted PDEs" in components
            and compact(
                "full 36-component symmetric Einstein system after the homogeneous ansatz"
            )
            in component_compact
        ),
        "correctMetricSigns": expected_metric in component_compact,
        "componentSumsEliminated": r"\sum_{B=1}^{16}" not in components,
        "condensateExpanded": all(
            compact(term) in component_compact for term in condensate_terms
        ),
        "spinorEquationsExpanded": all(
            equation in component_compact for equation in spinor_equations
        ),
        "diagonalEinsteinComplete": all(
            compact(component) in component_compact
            for component in diagonal_components
        ),
        "offDiagonalEinsteinComplete": all(
            compact(component) in component_compact
            for component in off_diagonal_components
        ),
        "indexMapping": (
            compact(r"\psi_A\ \text{in this report}=\texttt{psi}(A-1)")
            in component_compact
            and "one-based spinor labels" in numerics
        ),
        "positiveDomain": (
            "positive-condensate cone `S>0`" in components
            and "diverges as `S` approaches zero from above" in components
        ),
        "referenceInitialData": all(
            token in component_compact
            for token in (
                "a(0)=1",
                "H(0)=1",
                r"\psi_1(0)=1",
                r"\psi_{16}(0)=\frac12",
            )
        ),
        "twoBranchIntegration": (
            "backward from `x4=0` to `-0.2`" in components
            and "forward from `0` to `1.5`" in components
            and "backward branch is reversed" in numerics
        ),
        "accelerationCriterion": (
            compact(r"w< -\frac57") in component_compact
            and "0.8631436165767085" in components
        ),
        "darkSectorScope": (
            "exactly two" in components
            and "clustering" in components
            and "Infinitely many other potentials" in components
        ),
        "selectedMethodHonest": (
            "No comparison study establishes BDF as globally optimal"
            in numerics
            and "The best method for this system" not in numerics
        ),
        "solverConfiguration": all(
            phrase in numerics_normalized
            for phrase in (
                "SUNDIALS CVODE 7.8.0",
                "orders one through five",
                "default Newton nonlinear solver",
                "18-by-18 dense matrix",
                "difference-quotient Jacobian",
            )
        ),
        "semiAnalyticReduction": all(
            token in numerics_compact
            for token in (
                compact(r"\dot S=-7HS"),
                compact(r"\chi(x4)=\left(\cos\theta\,I_{16}"),
                compact(r"a(x4)^{7/2}\simeq"),
                compact(r"a(x4)^{7/10}\simeq"),
            )
        ),
        "errorDefinitions": all(
            token in numerics_compact
            for token in (
                compact(r"\varepsilon_S=\max\operatorname{rel}(S,a^{-7})"),
                compact(r"\varepsilon_F=\max\operatorname{rel}(H^2,\rho)"),
            )
        ),
        "recordedInvariantErrors": all(
            compact(value) in numerics_compact for value in exact_measurements
        ),
        "recordedResidualMeasurements": (
            "4.705850657056059\\times10^{-4}" in numerics_compact
            and "5.702272371471661\\times10^{-7}" in numerics_compact
            and "must not be reported as `1e-9` equation accuracy" in numerics
        ),
        "recordedRefinedConvergence": (
            "6.310776406656671\\times10^{-10}" in numerics_compact
            and "1.6415774988196702\\times10^{-9}" in numerics_compact
            and "2,294 solver steps" in numerics
            and "2,422 right-hand-side" in numerics
        ),
        "numericalLimitations": all(
            phrase in numerics
            for phrase in (
                "does not establish dark-matter clustering",
                "does not establish perturbative stability",
                "No compactification",
            )
        ),
        "reproductionCommands": all(
            phrase in components + numerics
            for phrase in (
                "verify_component_claims.py",
                "build_evidence.py",
                "verify_phase7_x0_x7_reports.ps1",
                "verify_phase7_x0_x7_reports.sh",
            )
        ),
    }

    return {
        "checks": checks,
        "measurements": {
            "checkCount": len(checks),
            "spinorEquationCount": len(spinor_equations),
            "diagonalEinsteinCount": len(diagonal_components),
            "offDiagonalEinsteinCount": len(off_diagonal_components),
            "exactEvidenceCheckCount": len(
                evidence["exactComponents"]["checks"]
            ),
            "modelEvidenceCheckCount": len(evidence["exactModel"]["checks"]),
            "solverEvidenceCheckCount": len(evidence["solver"]["checks"]),
            "numericalEvidenceCheckCount": len(
                evidence["numericalOutput"]["checks"]
            ),
            "convergenceCheckCount": len(
                convergence["independentVerification"]["checks"]
            ),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_reports(
        arguments.components.resolve(),
        arguments.numerics.resolve(),
        arguments.evidence.resolve(),
        CONVERGENCE_PATH,
    )
    failures = [
        name for name, passed in report["checks"].items() if not passed
    ]
    for name, passed in report["checks"].items():
        print(f"check_{name}={str(passed).lower()}")
    for name, value in report["measurements"].items():
        print(f"measurement_{name}={value}")
    print(f"failed_check_count={len(failures)}")
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())