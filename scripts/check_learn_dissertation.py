#!/usr/bin/env python3
"""Verify the self-contained Learn dissertation and its exact examples."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts import build_dissertation_tex
except ModuleNotFoundError:
    import build_dissertation_tex


EXPECTED_CHECK_COUNT = 21
EXPECTED_SECTIONS = [
    "1. How to use this guide",
    "2. Toolkit I: vectors, matrices, and forms",
    "3. Toolkit II: algebras, tensors, and exact computation",
    "4. Toolkit III: groups, Lie algebras, and representations",
    "5. Clifford algebras from geometry",
    "6. The exact `Cl(4,4)` construction",
    "7. Chirality and the two half-spin modules",
    "8. Type `D4` and the scope of representation classification",
    "9. From familiar number systems to split octonions",
    "10. Split octonions from Zorn data",
    "11. The para-product and its invariant trilinear form",
    "12. Related triples and split-real triality",
    "13. Compatibility of the Clifford and split-octonion pictures",
    "14. Numerical toolkit: ODEs, invariants, and error",
    "15. Numerical study I: 24-state triality transport",
    "16. Cosmology toolkit: expansion, density, and equation of state",
    "17. Numerical study II: an 18-state real-spinor background",
    "18. Geometry toolkit: curved metrics, frames, and spinors",
    "19. Numerical study III: coupled Einstein-spinor gravity",
    "20. Weitzenböck connection and teleparallel gravity",
    "21. Numerical study IV: independent teleparallel spinor dynamics",
    "22. Reproducibility and independent evidence",
    "23. Claim-to-evidence map and limitations",
    "24. Exercises",
    "25. Complete solutions",
    "26. Glossary",
    "27. Notation index",
    "28. Reference capsules and bibliography",
    "29. Conclusion",
]
REQUIRED_PHRASES = [
    "full 16-dimensional Clifford module is irreducible",
    "restriction to the even algebra and to `Spin(4,4)` splits",
    "rank 256",
    "even monomials have rank 128",
    "representation_commutant_dimensions=(1,1,1)",
    "pairwise intertwiner dimensions",
    "finite-dimensional irreducible algebraic representations",
    "do not classify all possible infinite-dimensional",
    "constraint rank 56",
    "five nonidentity elements are outer",
    "the fifth generator in the ordered Clifford list",
    "not independently compare it with a numerical quadrature",
    "derived from the density comparison, not an independent diagnostic",
    "background consistency calculation",
    "not observational fits",
    "does not establish stability of perturbations",
    "historical notebook outputs constitute proof",
    "R_{LC}=-\\mathbb T+B",
    "There is no quintessence scalar and no cosmological constant",
    "does not call the Levi-Civita application",
    "TEGR torsion is not an extra dark fluid",
]
PROHIBITED_DELEGATION = re.compile(
    r"\b(?:look it up|look this up|consult an external|"
    r"required reading|read elsewhere)\b",
    flags=re.IGNORECASE,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("dissertation/Learn_dirac-triality.md"),
    )
    parser.add_argument(
        "--tex",
        type=Path,
        default=Path("dissertation/Learn_dirac-triality.tex"),
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def product(
    tensor: list[list[list[int]]],
    left: list[int],
    right: list[int],
) -> list[int]:
    return [
        sum(
            left[first] * right[second] * tensor[first][second][output]
            for first in range(8)
            for second in range(8)
        )
        for output in range(8)
    ]


def inner(metric: list[list[int]], left: list[int], right: list[int]) -> int:
    return sum(
        left[row] * metric[row][column] * right[column]
        for row in range(8)
        for column in range(8)
    )


def exact_example_checks(repository_root: Path, text: str) -> dict[str, bool]:
    clifford = load_json(repository_root / "artifacts/exact/cl44-seed.json")
    split = load_json(repository_root / "artifacts/exact/split-octonion.json")
    triality = load_json(repository_root / "artifacts/exact/triality44.json")
    transport = load_json(
        repository_root / "artifacts/triality-transport/summary.json"
    )
    cosmology = load_json(
        repository_root / "artifacts/spinor-cosmology/summary.json"
    )
    curved = load_json(
        repository_root / "artifacts/curved-spin-geometry/geometry.json"
    )
    einstein = load_json(
        repository_root / "artifacts/einstein-spinor-44/summary.json"
    )
    weitzenbock_geometry = load_json(
        repository_root / "artifacts/weitzenbock-spin-geometry/geometry.json"
    )
    weitzenbock = load_json(
        repository_root / "artifacts/weitzenbock-spinor-44/summary.json"
    )

    basis = [[int(row == column) for column in range(8)] for row in range(8)]
    tensor = split["multiplicationTensor"]
    para_tensor = split["paraMultiplicationTensor"]
    metric = split["metric"]
    associator = [
        left - right
        for left, right in zip(
            product(tensor, product(tensor, basis[1], basis[2]), basis[4]),
            product(tensor, basis[1], product(tensor, basis[2], basis[4])),
            strict=True,
        )
    ]
    cyclic_values = [
        inner(
            metric,
            product(para_tensor, basis[left], basis[right]),
            basis[output],
        )
        for left, right, output in ((1, 2, 3), (2, 3, 1), (3, 1, 2))
    ]
    volume = clifford["volumeElement"]
    measurements = triality["measurements"]

    return {
        "cliffordFixtureExamples": clifford["halfSpinIndicesZeroBased"]
        == {
            "Plus": [0, 3, 5, 6, 9, 10, 12, 15],
            "Minus": [1, 2, 4, 7, 8, 11, 13, 14],
        }
        and [volume[index][index] for index in range(16)]
        == [1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1]
        and "plus_indices_zero_based=[0,3,5,6,9,10,12,15]" in text,
        "splitFixtureExamples": product(tensor, basis[1], basis[2])
        == [0, 0, 0, -1, 0, 0, 0, 0]
        and product(tensor, basis[2], basis[1]) == [0, 0, 0, 1, 0, 0, 0, 0]
        and associator == [0, 0, 0, 0, 0, 0, 0, 2]
        and cyclic_values == [-1, -1, -1]
        and "[e_1,e_2,e_4]=2e_7" in text,
        "trialityFixtureMeasurements": measurements["constraintRank"] == 56
        and measurements["trialityDimension"] == 28
        and measurements["projectionRanks"] == [28, 28, 28]
        and measurements["representationCommutantDimensions"] == [1, 1, 1]
        and measurements["representationIntertwinerDimensions"] == [0, 0, 0]
        and measurements["s3ElementCount"] == 6,
        "transportMeasurements": transport["stateDimension"] == 24
        and transport["sampleCount"] == 41
        and transport["solverSteps"] == 237
        and transport["rhsEvaluations"] == 251
        and transport["maximumDrift"]
        == {
            "vectorNorm": 1.2915224445464446e-12,
            "plusNorm": 3.070876886113183e-12,
            "minusNorm": 2.8042013155982204e-12,
            "trilinear": 2.9650726318664056e-12,
        }
        and transport["verdict"] == "SUCCESS",
        "cosmologyMeasurements": cosmology["stateDimension"] == 18
        and cosmology["sampleCount"] == 1201
        and cosmology["solverSteps"] == 711
        and cosmology["rhsEvaluations"] == 783
        and cosmology["maximumRelativeError"]
        == {
            "condensate": 6.565508926246135e-9,
            "density": 8.67334933419025e-10,
            "potential": 7.707676290195425e-9,
            "friedmann": 3.0848480998659325e-11,
        }
        and cosmology["verdict"] == "SUCCESS",
        "curvedGeometryMeasurements": curved["baseDimension"] == 8
        and curved["signature"] == [4, 4]
        and curved["measurements"]["nonzeroChristoffelComponents"] == 21
        and curved["measurements"][
            "nonzeroLoweredSpinConnectionComponents"
        ]
        == 14
        and all(curved["checks"].values()),
        "einsteinSpinorMeasurements": einstein["stateDimension"] == 18
        and einstein["sampleCount"] == 171
        and einstein["solverSteps"] == 1372
        and einstein["rhsEvaluations"] == 1486
        and einstein["accelerationTransitionScaleFactor"]
        == 0.8631436165767085
        and all(
            value < 7.5e-9
            for value in einstein["maximumRelativeError"].values()
        )
        and einstein["verdict"] == "SUCCESS",
        "weitzenbockMeasurements": weitzenbock_geometry["checks"][
            "curvatureZero"
        ]
        and weitzenbock_geometry["checks"]["torsionNonzero"]
        and weitzenbock_geometry["teleparallelScalars"]["identity"]
        == "RLC=-T+B"
        and weitzenbock["sampleCount"] == 171
        and weitzenbock["maximumRelativeError"][
            "homogeneousDiracEquivalenceAbsolute"
        ]
        == 0.0
        and weitzenbock["verdict"] == "SUCCESS",
    }


def verify_document(
    markdown_path: Path,
    tex_path: Path,
    repository_root: Path,
) -> dict[str, Any]:
    markdown_bytes = markdown_path.read_bytes()
    text = markdown_bytes.decode("utf-8")
    normalized_text = re.sub(r"\s+", " ", text)
    tex_bytes = tex_path.read_bytes()
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    worked_examples = [
        int(value)
        for value in re.findall(
            r"^### Worked example W(\d+):", text, re.MULTILINE
        )
    ]
    misconceptions = [
        int(value)
        for value in re.findall(
            r"^### Misconception check M(\d+):", text, re.MULTILINE
        )
    ]
    exercises = [
        int(value)
        for value in re.findall(
            r"^### Exercise E(\d+):", text, re.MULTILINE
        )
    ]
    solutions = [
        int(value)
        for value in re.findall(
            r"^### Solution E(\d+):", text, re.MULTILINE
        )
    ]
    glossary_text = text.split("## 26. Glossary", 1)[1].split(
        "## 27. Notation index", 1
    )[0]
    glossary_entries = re.findall(
        r"^### (.+)$", glossary_text, flags=re.MULTILINE
    )
    reference_capsules = re.findall(r"^### 28\.\d+ ", text, flags=re.MULTILINE)
    generated_tex = build_dissertation_tex.convert(
        text,
        strip_heading_numbers=True,
    ).encode("utf-8")

    checks = {
        "utf8LfSource": b"\r" not in markdown_bytes,
        "titleAndSubtitle": text.startswith(
            "# Learning Real Clifford Algebra, Split Octonions, "
            "and Triality in Signature (4,4)\n\n"
            "## A self-contained guide from matrices to verified computation\n"
        ),
        "sectionSequence": headings[1:] == EXPECTED_SECTIONS,
        "minimumDepth": len(re.findall(r"\b[\w'-]+\b", text)) >= 10_000,
        "claimCoverage": all(
            phrase in normalized_text for phrase in REQUIRED_PHRASES
        ),
        "workedExampleCoverage": worked_examples == list(range(1, 21)),
        "misconceptionCoverage": misconceptions == list(range(1, 21)),
        "exerciseSolutionParity": exercises == list(range(1, 23))
        and solutions == exercises,
        "glossaryCoverage": len(glossary_entries) >= 45,
        "referenceCapsules": len(reference_capsules) >= 6,
        "noPlaceholders": not any(
            marker in text for marker in ("TODO", "FIXME", "TBD")
        ),
        "noDelegatedPrerequisites": PROHIBITED_DELEGATION.search(text) is None,
        "generatedTexAgreement": generated_tex == tex_bytes,
    }
    checks.update(exact_example_checks(repository_root, text))
    return {
        "checks": checks,
        "measurements": {
            "markdownBytes": len(markdown_bytes),
            "lineCount": len(text.splitlines()),
            "wordCount": len(re.findall(r"\b[\w'-]+\b", text)),
            "sectionCount": len(EXPECTED_SECTIONS),
            "workedExampleCount": len(worked_examples),
            "misconceptionCount": len(misconceptions),
            "exerciseCount": len(exercises),
            "solutionCount": len(solutions),
            "glossaryEntryCount": len(glossary_entries),
        },
    }


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path(__file__).resolve().parent.parent
    report = verify_document(
        arguments.markdown.resolve(),
        arguments.tex.resolve(),
        repository_root,
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
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
