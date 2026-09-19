#!/usr/bin/env python3
"""Independently validate the frozen-source and structural-audit artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
AUDIT_CLASSES = {
    "markdown",
    "wolfram-binary",
    "wolfram-notebook",
    "wolfram-source",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
AUTHORED_CELL_STYLES = {
    "Abstract",
    "Chapter",
    "Code",
    "DisplayFormula",
    "ExternalLanguage",
    "InlineFormula",
    "Input",
    "Item",
    "ItemNumbered",
    "Program",
    "Section",
    "Subsection",
    "Subsubsection",
    "Subtitle",
    "Text",
    "Title",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(relative_path: str) -> dict[str, Any]:
    path = REPOSITORY_ROOT / relative_path
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def walk_files(root: Path) -> Iterable[Path]:
    for directory, directory_names, file_names in os.walk(
        root,
        followlinks=False,
    ):
        directory_names.sort(key=str.casefold)
        file_names.sort(key=str.casefold)
        for file_name in file_names:
            path = Path(directory) / file_name
            require(not path.is_symlink(), f"Unexpected symbolic link: {path}")
            yield path


def indexed(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        logical_path = record["logicalPath"]
        require(logical_path not in result, f"Duplicate path: {logical_path}")
        result[logical_path] = record
    return result


def validate_manifest() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json("audit/source-manifest.json")
    records = manifest.get("files", [])
    records_by_path = indexed(records)
    require(
        len(records) == len(records_by_path),
        "Manifest paths are not unique",
    )
    require(
        all(record["size"] == record["bytesRead"] for record in records),
        "Manifest contains an incomplete byte read",
    )
    require(
        all(SHA256_PATTERN.fullmatch(record["sha256"]) for record in records),
        "Manifest contains an invalid SHA-256 value",
    )

    filesystem_count = 0
    filesystem_bytes = 0
    for root in manifest["roots"]:
        for path in walk_files(Path(root["path"])):
            filesystem_count += 1
            filesystem_bytes += path.stat().st_size
    summary = manifest["summary"]
    require(filesystem_count == summary["fileCount"], "Filesystem count drift")
    require(filesystem_bytes == summary["totalBytes"], "Filesystem byte drift")
    require(len(records) == summary["fileCount"], "Manifest count mismatch")
    require(
        sum(record["size"] for record in records) == summary["totalBytes"],
        "Manifest byte total mismatch",
    )

    config_path = REPOSITORY_ROOT / "config" / "source-roots.json"
    require(
        sha256_file(config_path) == manifest["configuration"]["sha256"],
        "Source-root configuration hash mismatch",
    )
    checksum_lines = (REPOSITORY_ROOT / "audit" / "SHA256SUMS").read_text(
        encoding="utf-8"
    ).splitlines()
    require(
        len(checksum_lines) == len(records),
        "Checksum line count mismatch",
    )
    for line, record in zip(checksum_lines, records, strict=True):
        expected = f"{record['sha256']}  {record['logicalPath']}"
        require(
            line == expected,
            f"Checksum mismatch: {record['logicalPath']}",
        )
    return manifest, records_by_path


def validate_wolfram(
    manifest: dict[str, Any],
    records_by_path: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    report_path = REPOSITORY_ROOT / "audit" / "wolfram-structure.json"
    report = load_json("audit/wolfram-structure.json")
    manifest_path = REPOSITORY_ROOT / "audit" / "source-manifest.json"
    require(
        report["sourceManifestSha256"] == sha256_file(manifest_path),
        "Wolfram report references another source manifest",
    )
    expected = {
        record["logicalPath"]
        for record in manifest["files"]
        if record["auditClass"] in {"wolfram-notebook", "wolfram-source"}
    }
    actual = indexed(report["files"])
    require(set(actual) == expected, "Wolfram report coverage mismatch")
    for logical_path, record in actual.items():
        source = records_by_path[logical_path]
        require(
            record["parseStatus"] == "parsed",
            f"Parse failed: {logical_path}",
        )
        require(record["messageCount"] == 0, f"Parse messages: {logical_path}")
        require(
            record["hashMatchesManifest"],
            f"Hash mismatch: {logical_path}",
        )
        require(
            record["sizeMatchesManifest"],
            f"Size mismatch: {logical_path}",
        )
        require(
            record["sha256"] == source["sha256"],
            f"Digest drift: {logical_path}",
        )
        if source["auditClass"] == "wolfram-notebook":
            authored_cells = record.get("authoredCells")
            require(
                isinstance(authored_cells, list),
                f"Missing authored-cell index: {logical_path}",
            )
            expected_authored_count = sum(
                record.get("styleCounts", {}).get(style, 0)
                for style in AUTHORED_CELL_STYLES
            )
            require(
                record.get("authoredCellCount") == len(authored_cells)
                == expected_authored_count,
                f"Authored-cell count mismatch: {logical_path}",
            )
            require(
                SHA256_PATTERN.fullmatch(
                    record.get("authoredCellStreamSha256", "")
                )
                is not None,
                f"Invalid authored-cell stream digest: {logical_path}",
            )
            for ordinal, cell in enumerate(authored_cells, start=1):
                require(
                    cell.get("ordinal") == ordinal,
                    f"Authored-cell order mismatch: {logical_path}",
                )
                require(
                    cell.get("style") in AUTHORED_CELL_STYLES,
                    f"Unexpected authored-cell style: {logical_path}",
                )
                require(
                    SHA256_PATTERN.fullmatch(cell.get("bodySha256", ""))
                    is not None,
                    f"Invalid authored-cell digest: {logical_path}",
                )
                preview = cell.get("preview")
                require(
                    isinstance(preview, str) and len(preview) <= 240,
                    f"Invalid authored-cell preview: {logical_path}",
                )
                require(
                    cell.get("bodyCharacterCount", -1) >= len(preview),
                    f"Invalid authored-cell length: {logical_path}",
                )
    summary = report["summary"]
    require(
        summary["artifactCount"] == len(expected),
        "Wolfram count mismatch",
    )
    require(summary["parseFailureCount"] == 0, "Wolfram parse failures")
    require(summary["filesWithMessages"] == 0, "Wolfram parse messages")
    require(summary["hashFailureCount"] == 0, "Wolfram hash failures")
    require(summary["sizeFailureCount"] == 0, "Wolfram size failures")
    require(report_path.stat().st_size > 0, "Wolfram report is empty")
    return report


def validate_structural(
    manifest: dict[str, Any],
    wolfram_report: dict[str, Any],
) -> dict[str, Any]:
    report = load_json("audit/structural-audit.json")
    manifest_path = REPOSITORY_ROOT / "audit" / "source-manifest.json"
    wolfram_path = REPOSITORY_ROOT / "audit" / "wolfram-structure.json"
    require(
        report["sourceManifestSha256"] == sha256_file(manifest_path),
        "Structural report references another source manifest",
    )
    require(
        report["wolframReportSha256"] == sha256_file(wolfram_path),
        "Structural report references another Wolfram report",
    )
    expected = {
        record["logicalPath"]
        for record in manifest["files"]
        if record["auditClass"] in AUDIT_CLASSES
    }
    actual = indexed(report["files"])
    require(set(actual) == expected, "Structural report coverage mismatch")
    for logical_path, record in actual.items():
        require(record["byteCoverage"] == "complete", logical_path)
        if record["auditClass"] == "wolfram-binary":
            require(record["textEvidence"] is None, logical_path)
            require(record["structuralImport"] == "hash-only", logical_path)
        else:
            require(record["textEvidence"] is not None, logical_path)
        if record["auditClass"] in {"wolfram-notebook", "wolfram-source"}:
            require(record["structuralImport"] == "parsed", logical_path)
    summary = report["summary"]
    decision_document = load_json("config/audit-decisions.json")
    explicit_decisions = decision_document.get("decisions", [])
    reviewed_roots = {
        review["rootId"]
        for review in decision_document.get("rootReviews", [])
    }
    reviewed_paths = {
        decision["logicalPath"] for decision in explicit_decisions
    }
    reviewed_paths.update(
        record["logicalPath"]
        for record in manifest["files"]
        if record["auditClass"] in AUDIT_CLASSES
        and record["rootId"] in reviewed_roots
    )
    decision_count = len(reviewed_paths)
    review_sources = {
        decision["reviewSource"] for decision in explicit_decisions
    }
    review_sources.update(
        review["reviewSource"]
        for review in decision_document.get("rootReviews", [])
    )
    for review_source in review_sources:
        require(
            (REPOSITORY_ROOT / review_source).is_file(),
            f"Missing human-review evidence: {review_source}",
        )
    require(summary["artifactCount"] == len(expected), "Audit count mismatch")
    require(
        summary["completeByteCoverageCount"] == len(expected),
        "Incomplete audit byte coverage",
    )
    require(summary["structuralFailureCount"] == 0, "Structural failures")
    require(
        summary["reviewDecisionCount"] == decision_count,
        "Review-decision count mismatch",
    )
    require(
        summary["humanReviewCompleteCount"] == decision_count,
        "Human-review completion mismatch",
    )
    require(
        summary["humanReviewCompleteCount"]
        + summary["humanReviewPendingCount"]
        + sum(
            record["authoredReview"] == "not-applicable"
            for record in actual.values()
        )
        == len(expected),
        "Human-review status totals do not reconcile",
    )
    actual_class_counts = Counter(
        record["auditClass"] for record in actual.values()
    )
    require(
        summary["classCounts"] == dict(sorted(actual_class_counts.items())),
        "Structural class-count mismatch",
    )
    require(
        wolfram_report["summary"]["artifactCount"]
        == sum(
            record["auditClass"] in {"wolfram-notebook", "wolfram-source"}
            for record in actual.values()
        ),
        "Cross-report Wolfram count mismatch",
    )

    ledger_lines = (REPOSITORY_ROOT / "audit" / "audit-ledger.md").read_text(
        encoding="utf-8"
    ).splitlines()
    data_rows = [
        line
        for line in ledger_lines
        if line.startswith("| ") and not line.startswith("| Root ")
    ]
    require(len(data_rows) == len(expected), "Ledger row count mismatch")
    require(
        f"Audit artifacts: {len(expected)}" in ledger_lines,
        "Ledger summary mismatch",
    )
    return report


def validate_frozen_inputs() -> None:
    initial = load_json("backups/pre-bootstrap/manifest.json")
    require(initial["verification"]["allFilesMatched"], "Input backup failed")
    input_names = {record["name"] for record in initial["files"]}
    recorded_revisions: dict[str, set[tuple[str, int]]] = {
        name: set() for name in input_names
    }

    backup_manifests = (REPOSITORY_ROOT / "backups").rglob("manifest.json")
    for manifest_path in sorted(backup_manifests):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        destination_root_value = manifest.get(
            "destinationRoot",
            manifest.get("backupDirectory"),
        )
        require(
            destination_root_value is not None,
            f"Invalid backup: {manifest_path}",
        )
        destination_root = Path(destination_root_value)
        for record in manifest.get("files", []):
            relative_path = record.get("relativePath", record.get("name"))
            if relative_path not in input_names:
                continue
            source_hash = record.get("sourceSha256", record.get("sourceHash"))
            source_size = record.get("sourceSize")
            backup_hash = record.get("backupSha256", record.get("backupHash"))
            backup_size = record.get("backupSize")
            match = record.get("match", record.get("backupMatch", False))
            backup_path = destination_root.joinpath(*relative_path.split("/"))
            require(match is True, f"Unverified input backup: {manifest_path}")
            require(
                backup_path.is_file(),
                f"Missing input backup: {backup_path}",
            )
            require(
                sha256_file(backup_path).upper() == str(backup_hash).upper(),
                f"Input backup hash mismatch: {backup_path}",
            )
            require(
                backup_path.stat().st_size == source_size == backup_size,
                f"Input backup size mismatch: {backup_path}",
            )
            recorded_revisions[relative_path].add(
                (str(source_hash).lower(), int(source_size))
            )

    for name in sorted(input_names):
        source = REPOSITORY_ROOT / name
        require(source.is_file(), f"Missing frozen input: {name}")
        current = (sha256_file(source), source.stat().st_size)
        require(
            current in recorded_revisions[name],
            f"Live input has no immutable revision: {name}",
        )


def main() -> int:
    manifest, records_by_path = validate_manifest()
    wolfram_report = validate_wolfram(manifest, records_by_path)
    structural_report = validate_structural(manifest, wolfram_report)
    validate_frozen_inputs()
    print(f"source_roots={manifest['summary']['rootCount']}")
    print(f"source_files={manifest['summary']['fileCount']}")
    print(f"source_bytes={manifest['summary']['totalBytes']}")
    print(f"audit_artifacts={structural_report['summary']['artifactCount']}")
    print(f"wolfram_artifacts={wolfram_report['summary']['artifactCount']}")
    print(
        "human_reviews_complete="
        f"{structural_report['summary']['humanReviewCompleteCount']}"
    )
    print("phase0_structural_status=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1) from error
