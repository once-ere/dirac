#!/usr/bin/env python3
"""Semantically verify the repository-wide Developer Summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUMMARY = REPOSITORY_ROOT / "DEVELOPER_SUMMARY.md"

REQUIRED_SECTIONS = (
    "Repository contract",
    "Top-level architecture",
    "Build and verification graph",
    "Phase map",
    "Rust application architecture",
    "Exact mathematical core",
    "Curved spin geometry",
    "Einstein-spinor numerical method",
    "Verification strategy",
    "Developer workflows",
    "Canonical artifacts and provenance",
    "Release discipline",
    "Known boundaries and non-claims",
    "Change-impact guide",
    "Developer checklist",
    "Documentation map",
    "Rebuilding this summary",
)

REQUIRED_PHASES = (
    "Phase 0: source audit and bootstrap",
    "Phase 1: exact algebra and triality",
    "Phase 2: triality transport",
    "Phase 3: homogeneous spinor cosmology",
    "Phase 4: notebooks and publications",
    "Phase 5: curved Levi-Civita Einstein-spinor model",
    "Phase 6: Weitzenboeck spin geometry",
    "Phase 7: `{x0,...,x7}` component refinement",
)

REQUIRED_PATHS = (
    "Cargo.toml",
    "config/source-roots.json",
    "config/audit-decisions.json",
    "audit/source-manifest.json",
    "audit/audit-ledger.md",
    "artifacts/exact/cl44-seed.json",
    "artifacts/exact/split-octonion.json",
    "artifacts/exact/triality44.json",
    "artifacts/triality-transport/trajectory.csv",
    "artifacts/spinor-cosmology/background.csv",
    "artifacts/einstein-spinor-44/history.csv",
    "artifacts/weitzenbock-spinor-44/history.csv",
    "studies/triality_transport/Cargo.toml",
    "studies/spinor_cosmology/Cargo.toml",
    "studies/einstein_spinor_44/Cargo.toml",
    "studies/weitzenbock_spinor_44/Cargo.toml",
    "notebooks/DiracTriality.nb",
    "notebooks/dirac_triality.ipynb",
    "notebooks/dirac_triality.executed.ipynb",
    "wolfram/dirac_triality.wls",
    "dissertation/dirac-triality.md",
    "dissertation/Learn_dirac-triality.md",
    "provenance/EINSTEIN_SPINOR_44.md",
    "provenance/WEITZENBOCK_SPINOR_44.md",
    "refinement/phase7-x0-x7/evidence.json",
    "refinement/phase7-x0-x7/convergence.json",
    "refinement/phase7-x0-x7/VERIFICATION.md",
)

PHASE_GATES = (
    "verify_phase0",
    "verify_phase1",
    "verify_phase2_transport",
    "verify_phase3_cosmology",
    "verify_phase4_publication",
    "verify_phase5_curved_spin_gravity",
    "verify_phase6_weitzenbock_spinor",
    "verify_phase7_x0_x7_reports",
)

ARTIFACT_HASHES = {
    "artifacts/exact/cl44-seed.json": (
        "0660e436fdcf90ed0f0481c9a828e92659987f5820084ccbf5e1dfc96866cc54"
    ),
    "artifacts/exact/split-octonion.json": (
        "25044ea194c1e18e40341da1f0098b80bfeb9f4bcb6e7665a32d03f55ac360ca"
    ),
    "artifacts/exact/triality44.json": (
        "5985f5c0fdd6656c3c9f572ef1a5d06eee21aabe44cc9bf33747bb79b5e181dd"
    ),
    "artifacts/triality-transport/trajectory.csv": (
        "ee5ad82ee604f072f04bed8ef20cdd856bb02ba80e16c3973b10c6c43f972b9c"
    ),
    "artifacts/triality-transport/summary.json": (
        "61b8fe5a8a72e48d40d40d6850a6c559e2dd06ccfa9de97982590d35a82044fb"
    ),
    "artifacts/spinor-cosmology/background.csv": (
        "8a6f7ace34949d82d4022a9b5a660733ed018c91b2b931d934aab7793b5585c2"
    ),
    "artifacts/spinor-cosmology/summary.json": (
        "8f1e45a37c14cc10c7c6b6469ceca7c65e7b9ffc08b3c9dd5bfc518065c590db"
    ),
    "artifacts/curved-spin-geometry/geometry.json": (
        "6b5eab6b001d69c5face7b179af8a27e3cfe254cf80bc740cdcb7a2855fcdf67"
    ),
    "artifacts/einstein-spinor-44/history.csv": (
        "9553b36f201ef43a92c7de3fe2f46457a592e55285e6220d8aa7af6e36a26f9c"
    ),
    "artifacts/einstein-spinor-44/summary.json": (
        "6b15d084178d01aaed37b84b4bcf8f5246a6941bbe8366ad9c0c3db099eea0f1"
    ),
    "artifacts/weitzenbock-spin-geometry/geometry.json": (
        "804f00f31ffa4247fc1e30d8e89df3ea7ddbd7c8d9fe795317bd57155c93774c"
    ),
    "artifacts/weitzenbock-spinor-44/history.csv": (
        "c88ed61cafa59ea0d7693da41527c7b4486ded7cc09ac680b4f20f893d42b62a"
    ),
    "artifacts/weitzenbock-spinor-44/summary.json": (
        "d03a90539887702ad6bdbe0ee3a5d783094b052609fc0e4d2b761a12b97fa6c8"
    ),
    "refinement/phase7-x0-x7/evidence.json": (
        "58373d6aeea90807a3f064f395b8367502ff3a280050a5c8823c9e0cc0b2eb0b"
    ),
    "refinement/phase7-x0-x7/convergence.json": (
        "9cf9e89a2326786e2573eafbf1ad1cdcb1528eeb540bfb102cbf5c6988a1ef76"
    ),
}

PUBLICATION_HASHES = {
    "dissertation/dirac-triality.md": (
        "44b76c2d872598ad1b038a8d4ad1293b18885ab228297c921579daa86eeb1381"
    ),
    "dissertation/dirac-triality.tex": (
        "12df60627b5f11b09ccbbadd9ca38fd2ce7efcfccd769f69fd8280b78a6cec38"
    ),
    "dissertation/dirac-triality.pdf": (
        "8531af531c91fbf366fbcb30759da63e3881dcc241931698a9f6ee3a6ae0b69e"
    ),
    "dissertation/Learn_dirac-triality.md": (
        "ab6c653f6d0f2355411d61c9357d3c709ced8b9ac70167861e893a9029052676"
    ),
    "dissertation/Learn_dirac-triality.tex": (
        "533eeaef0619d3b590d74fa03a4a81aaa76163fce289d659a1007d1b10b0e03e"
    ),
    "dissertation/Learn_dirac-triality.pdf": (
        "7c683b51445a3b4964b244ea3e232bc0ba3f745b5427308b59a80d1532e19ff9"
    ),
    "notebooks/DiracTriality.nb": (
        "5c80d2d9367610db9835f4c570966dba1751cad77ae30f42dc0987bc917505e2"
    ),
    "notebooks/dirac_triality.ipynb": (
        "5813727a077a9afcc881e86928e7e48376056d48ce31409fb5c28e00d0844411"
    ),
    "notebooks/dirac_triality.executed.ipynb": (
        "2d998c596ac81be060562ed0d9a324c937b5069521320d95372f6a2dbce6b169"
    ),
    "wolfram/dirac_triality.wls": (
        "260558b921fd3d45c28a0c757aeb5dd9b23c0862394c12d5d874417506728dc4"
    ),
    "provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf": (
        "f64e3f8420c18c3886e201c64ee41d8e0564d7222038f5a8b83f45a46b7113f4"
    ),
    "provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf": (
        "8501d992709282039b5a69d1de045660018505f1048f09fecfedc40795484af9"
    ),
}

STUDY_SUMMARIES = {
    "artifacts/triality-transport/summary.json": (24, 41, 237, 251),
    "artifacts/spinor-cosmology/summary.json": (18, 1201, 711, 783),
    "artifacts/einstein-spinor-44/summary.json": (18, 171, 1372, 1486),
    "artifacts/weitzenbock-spinor-44/summary.json": (18, 171, 1372, 1486),
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_summary(summary_path: Path = DEFAULT_SUMMARY) -> dict[str, Any]:
    text = summary_path.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", " ", text)
    lines = text.splitlines()
    headings = [line for line in lines if re.match(r"^#{1,6}\s+", line)]
    tables = [line for line in lines if line.startswith("|") and "---" in line]
    words = re.findall(r"\b[\w'-]+\b", text)

    phase0 = json.loads(
        (REPOSITORY_ROOT / "audit/source-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    phase7_evidence = json.loads(
        (REPOSITORY_ROOT / "refinement/phase7-x0-x7/evidence.json").read_text(
            encoding="utf-8"
        )
    )
    phase7_convergence = json.loads(
        (
            REPOSITORY_ROOT
            / "refinement/phase7-x0-x7/convergence.json"
        ).read_text(encoding="utf-8")
    )

    artifact_hashes_match = all(
        sha256_file(REPOSITORY_ROOT / path) == expected
        and expected in text
        for path, expected in ARTIFACT_HASHES.items()
    )
    publication_hashes_match = all(
        sha256_file(REPOSITORY_ROOT / path) == expected
        and expected in text
        for path, expected in PUBLICATION_HASHES.items()
    )
    study_summaries_match = True
    for path, expected in STUDY_SUMMARIES.items():
        summary = json.loads(
            (REPOSITORY_ROOT / path).read_text(encoding="utf-8")
        )
        measured = (
            summary["stateDimension"],
            summary["sampleCount"],
            summary["solverSteps"],
            summary["rhsEvaluations"],
        )
        study_summaries_match &= measured == expected

    checks = {
        "developerTitle": text.startswith("# Developer Summary:"),
        "notExecutiveHeading": not any(
            re.match(r"^#{1,6}\s+Executive Summary\b", line)
            for line in lines
        ),
        "detailedScale": len(lines) >= 750 and len(words) >= 5000,
        "sectionCoverage": all(section in normalized for section in REQUIRED_SECTIONS),
        "phaseCoverage": all(phase in normalized for phase in REQUIRED_PHASES),
        "pathCoverage": all(
            path in text and (REPOSITORY_ROOT / path).exists()
            for path in REQUIRED_PATHS
        ),
        "gateCoverage": all(
            f"{gate}.ps1" in text and f"{gate}.sh" in text
            for gate in PHASE_GATES
        ),
        "phase0Metrics": (
            phase0["summary"]["fileCount"] == 5991
            and phase0["summary"]["totalBytes"] == 371942252
            and phase0["summary"]["auditFileCount"] == 209
            and "5,991" in text
            and "371,942,252" in text
        ),
        "artifactHashes": artifact_hashes_match,
        "publicationHashes": publication_hashes_match,
        "studySummaries": study_summaries_match,
        "phase7Evidence": all(phase7_evidence[section]["checks"] and all(
            phase7_evidence[section]["checks"].values()
        ) for section in ("exactComponents", "exactModel", "solver", "numericalOutput")),
        "phase7Convergence": all(
            phase7_convergence["independentVerification"]["checks"].values()
        ),
        "moduleDistinction": (
            "irreducible for `Cl(4,4)`" in normalized
            and "two inequivalent real eight-dimensional half-spin modules"
            in normalized
        ),
        "coordinateScope": (
            "adopts only the coordinate names and ordering" in normalized
            and "does not import that reference's metric or connection"
            in normalized
        ),
        "solverScope": (
            "No comparative benchmark establishes this as a globally optimal integrator"
            in normalized
            and "read-only Git submodule" in normalized
        ),
        "darkSectorBoundaries": all(
            phrase in normalized
            for phrase in (
                "model-internal analogies, not observational identifications",
                "dark-matter clustering",
                "an observational dark-energy fit",
            )
        ),
        "privateInputs": (
            "`prompt.txt` is local-only and ignored" in normalized
            and "external read-only references" in normalized
        ),
        "auditVocabulary": all(
            disposition in text
            for disposition in (
                "historical-evidence",
                "independently-reconstruct",
                "reuse-pattern",
                "generated",
                "mixed-see-review",
            )
        ),
        "toolchainCoverage": all(
            token in text
            for token in (
                "Python",
                "Rust compiler",
                "Cargo",
                "WolframScript",
                "MiKTeX-pdfTeX",
                "nbformat",
                "nbclient",
            )
        ),
        "workflowCoverage": all(
            phrase in text
            for phrase in (
                "git clone --recurse-submodules",
                "python -m unittest discover -s tests -v",
                "cargo clippy --workspace --all-targets -- -D warnings",
                "git fsck --full --strict",
            )
        ),
        "noPlaceholders": not re.search(r"\b(TODO|FIXME|TBD)\b", text),
        "tableCount": len(tables) >= 10,
        "headingCount": len(headings) >= 50,
    }
    return {
        "checks": checks,
        "measurements": {
            "byteCount": summary_path.stat().st_size,
            "lineCount": len(lines),
            "wordCount": len(words),
            "headingCount": len(headings),
            "tableCount": len(tables),
            "requiredPathCount": len(REQUIRED_PATHS),
            "artifactHashCount": len(ARTIFACT_HASHES),
            "publicationHashCount": len(PUBLICATION_HASHES),
            "studySummaryCount": len(STUDY_SUMMARIES),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    report = verify_summary(arguments.summary.resolve())
    failures = [
        name for name, passed in report["checks"].items() if not passed
    ]
    for name, passed in report["checks"].items():
        print(f"check_{name}={str(passed).lower()}")
    for name, value in report["measurements"].items():
        print(f"measurement_{name}={value}")
    print(f"check_count={len(report['checks'])}")
    print(f"failed_check_count={len(failures)}")
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
