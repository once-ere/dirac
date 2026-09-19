#!/usr/bin/env python3
"""Recheck and index every required Markdown and Wolfram artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


AUDIT_CLASSES = {
    "markdown",
    "wolfram-binary",
    "wolfram-notebook",
    "wolfram-source",
}
WORD_PATTERN = re.compile(r"\b\w+\b", flags=re.UNICODE)
HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\([^)]*\)")
MARKERS = ("TODO", "FIXME", "$Failed", "Failure[", "Message[")
CHUNK_SIZE = 1024 * 1024


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("audit/source-manifest.json"),
    )
    parser.add_argument(
        "--wolfram-report",
        type=Path,
        default=Path("audit/wolfram-structure.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit/structural-audit.json"),
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("audit/audit-ledger.md"),
    )
    parser.add_argument(
        "--decisions",
        type=Path,
        default=Path("config/audit-decisions.json"),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def update_framed_digest(digest: Any, value: str) -> None:
    encoded = value.encode("utf-8")
    digest.update(len(encoded).to_bytes(8, byteorder="big"))
    digest.update(encoded)


def analyze_text(
    path: Path,
    encoding: str,
    artifact_class: str,
) -> dict[str, Any]:
    line_digest = hashlib.sha256()
    word_digest = hashlib.sha256()
    line_count = 0
    nonempty_line_count = 0
    character_count = 0
    word_count = 0
    link_count = 0
    fence_line_count = 0
    headings: list[dict[str, Any]] = []
    marker_counts: Counter[str] = Counter()

    with path.open(
        "r",
        encoding=encoding,
        errors="strict",
        newline="",
    ) as source:
        for line_count, line in enumerate(source, start=1):
            character_count += len(line)
            if line.strip():
                nonempty_line_count += 1
            update_framed_digest(line_digest, line)
            words = WORD_PATTERN.findall(line)
            word_count += len(words)
            for word in words:
                update_framed_digest(word_digest, word)
            for marker in MARKERS:
                marker_counts[marker] += line.count(marker)
            if artifact_class == "markdown":
                heading = HEADING_PATTERN.match(line)
                if heading:
                    headings.append(
                        {
                            "line": line_count,
                            "level": len(heading.group(1)),
                            "text": heading.group(2),
                        }
                    )
                link_count += len(LINK_PATTERN.findall(line))
                if line.lstrip().startswith(("```", "~~~")):
                    fence_line_count += 1

    return {
        "encoding": encoding,
        "lineCount": line_count,
        "nonemptyLineCount": nonempty_line_count,
        "characterCount": character_count,
        "wordCount": word_count,
        "lineStreamSha256": line_digest.hexdigest(),
        "wordStreamSha256": word_digest.hexdigest(),
        "markerCounts": dict(marker_counts),
        "markdownHeadings": headings,
        "markdownLinkCount": link_count,
        "markdownFenceLineCount": fence_line_count,
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def path_for(record: dict[str, Any]) -> Path:
    return Path(record["rootPath"]).joinpath(
        *record["relativePath"].split("/")
    )


def index_by_logical_path(
    records: Iterable[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        logical_path = record["logicalPath"]
        if logical_path in indexed:
            raise ValueError(f"Duplicate logical path: {logical_path}")
        indexed[logical_path] = record
    return indexed


def validate_decision(
    decision: dict[str, Any],
    identifier: str,
) -> None:
    required_fields = {
        "authoredReview",
        "execution",
        "relevance",
        "defects",
        "disposition",
        "reviewSource",
    }
    missing = required_fields.difference(decision)
    if missing:
        raise ValueError(
            f"Incomplete audit decision for {identifier}: {sorted(missing)}"
        )
    if decision["authoredReview"] != "complete":
        raise ValueError(f"Review decision is not complete: {identifier}")


def load_decisions(
    path: Path,
    manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    document = load_json(path)
    if document.get("schemaVersion") != 1:
        raise ValueError("Unsupported audit-decision schema")
    decisions = index_by_logical_path(document.get("decisions", []))
    for logical_path, decision in decisions.items():
        validate_decision(decision, logical_path)

    root_reviews: dict[str, dict[str, Any]] = {}
    for review in document.get("rootReviews", []):
        root_id = review.get("rootId")
        if not isinstance(root_id, str) or not root_id:
            raise ValueError("Root review is missing rootId")
        if root_id in root_reviews:
            raise ValueError(f"Duplicate root review: {root_id}")
        validate_decision(review, root_id)
        root_reviews[root_id] = review

    manifest_root_ids = {root["id"] for root in manifest.get("roots", [])}
    unknown_roots = set(root_reviews).difference(manifest_root_ids)
    if unknown_roots:
        raise ValueError(f"Unknown reviewed roots: {sorted(unknown_roots)}")
    for record in manifest.get("files", []):
        if record["auditClass"] not in AUDIT_CLASSES:
            continue
        logical_path = record["logicalPath"]
        if logical_path in decisions:
            continue
        root_review = root_reviews.get(record["rootId"])
        if root_review:
            decisions[logical_path] = {
                key: value
                for key, value in root_review.items()
                if key != "rootId"
            } | {"logicalPath": logical_path}
    return decisions


def build_records(
    manifest: dict[str, Any],
    wolfram_report: dict[str, Any],
    decisions: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    decisions = decisions or {}
    wolfram_index = index_by_logical_path(wolfram_report.get("files", []))
    results: list[dict[str, Any]] = []
    for source_record in manifest.get("files", []):
        artifact_class = source_record["auditClass"]
        if artifact_class not in AUDIT_CLASSES:
            continue
        path = path_for(source_record)
        digest, size = sha256_file(path)
        if digest != source_record["sha256"] or size != source_record["size"]:
            raise RuntimeError(
                f"Source changed after manifest generation: "
                f"{source_record['logicalPath']}"
            )

        text_result: dict[str, Any] | None = None
        if artifact_class != "wolfram-binary":
            encoding = source_record.get("encoding")
            if not encoding:
                raise RuntimeError(
                    f"Required text has no verified encoding: "
                    f"{source_record['logicalPath']}"
                )
            text_result = analyze_text(path, encoding, artifact_class)
            if text_result["lineCount"] != source_record["lineCount"]:
                raise RuntimeError(
                    f"Line count changed after manifest generation: "
                    f"{source_record['logicalPath']}"
                )

        structure_result: dict[str, Any] | None = None
        if artifact_class in {"wolfram-notebook", "wolfram-source"}:
            structure_result = wolfram_index.get(source_record["logicalPath"])
            if structure_result is None:
                raise RuntimeError(
                    f"Missing Wolfram structure report: "
                    f"{source_record['logicalPath']}"
                )
            if (
                structure_result.get("sha256") != digest
                or not structure_result.get("hashMatchesManifest")
                or not structure_result.get("sizeMatchesManifest")
            ):
                raise RuntimeError(
                    f"Wolfram structure hash mismatch: "
                    f"{source_record['logicalPath']}"
                )

        parse_status = (
            structure_result.get("parseStatus", "not-applicable")
            if structure_result
            else (
                "hash-only"
                if artifact_class == "wolfram-binary"
                else "not-applicable"
            )
        )
        result = {
                "logicalPath": source_record["logicalPath"],
                "rootId": source_record["rootId"],
                "relativePath": source_record["relativePath"],
                "auditClass": artifact_class,
                "size": size,
                "sha256": digest,
                "byteCoverage": "complete",
                "authoredReview": (
                    "not-applicable"
                    if artifact_class == "wolfram-binary"
                    else "machine-indexed-human-pending"
                ),
                "structuralImport": parse_status,
                "execution": "pending",
                "relevance": "pending",
                "defects": "pending",
                "disposition": "pending",
                "textEvidence": text_result,
                "wolframEvidence": structure_result,
                "humanReviewEvidence": None,
            }
        decision = decisions.get(source_record["logicalPath"])
        if decision:
            for field in (
                "authoredReview",
                "execution",
                "relevance",
                "defects",
                "disposition",
            ):
                result[field] = decision[field]
            result["humanReviewEvidence"] = decision["reviewSource"]
        results.append(result)
    return results


def markdown_cell(value: object) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def render_ledger(records: list[dict[str, Any]]) -> str:
    lines = [
        "# Source audit ledger",
        "",
        (
            "Every listed artifact has complete byte coverage. "
            "Machine indexing and structural parsing do not substitute for "
            "human scientific review or execution."
        ),
        "",
        (
            "| Root | Path | Class | Bytes | SHA-256 | Byte coverage | "
            "Authored review | Structural import | Execution | Relevance | "
            "Defects | Disposition |"
        ),
        "|---|---|---:|---:|---|---|---|---|---|---|---|---|",
    ]
    for record in records:
        values = [
            record["rootId"],
            record["relativePath"],
            record["auditClass"],
            record["size"],
            record["sha256"],
            record["byteCoverage"],
            record["authoredReview"],
            record["structuralImport"],
            record["execution"],
            record["relevance"],
            record["defects"],
            record["disposition"],
        ]
        rendered_values = " | ".join(markdown_cell(value) for value in values)
        lines.append(f"| {rendered_values} |")
    lines.extend(["", f"Audit artifacts: {len(records)}", ""])
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as target:
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def main() -> int:
    arguments = parse_arguments()
    manifest_path = arguments.manifest.resolve()
    wolfram_path = arguments.wolfram_report.resolve()
    manifest = load_json(manifest_path)
    wolfram_report = load_json(wolfram_path)
    decisions = load_decisions(arguments.decisions.resolve(), manifest)
    manifest_hash, _ = sha256_file(manifest_path)
    if wolfram_report.get("sourceManifestSha256") != manifest_hash:
        raise RuntimeError(
            "Wolfram report was built from a different source manifest"
        )

    audit_paths = {
        record["logicalPath"]
        for record in manifest.get("files", [])
        if record["auditClass"] in AUDIT_CLASSES
    }
    unknown_decisions = set(decisions).difference(audit_paths)
    if unknown_decisions:
        raise RuntimeError(
            f"Audit decisions reference unknown paths: "
            f"{sorted(unknown_decisions)}"
        )
    records = build_records(manifest, wolfram_report, decisions)
    class_counts = Counter(record["auditClass"] for record in records)
    structural_failures = sum(
        record["structuralImport"] == "failed" for record in records
    )
    document = {
        "schemaVersion": 1,
        "sourceManifestSha256": manifest_hash,
        "wolframReportSha256": sha256_file(wolfram_path)[0],
        "summary": {
            "artifactCount": len(records),
            "classCounts": dict(sorted(class_counts.items())),
            "completeByteCoverageCount": sum(
                record["byteCoverage"] == "complete" for record in records
            ),
            "machineIndexedTextCount": sum(
                record["textEvidence"] is not None for record in records
            ),
            "structuralFailureCount": structural_failures,
            "reviewDecisionCount": len(decisions),
            "humanReviewCompleteCount": sum(
                record["authoredReview"] == "complete" for record in records
            ),
            "humanReviewPendingCount": sum(
                record["authoredReview"] == "machine-indexed-human-pending"
                for record in records
            ),
        },
        "files": records,
    }
    atomic_write(
        arguments.output.resolve(),
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
    )
    atomic_write(arguments.ledger.resolve(), render_ledger(records))
    print(f"artifacts={len(records)}")
    print(f"byte_complete={document['summary']['completeByteCoverageCount']}")
    print(f"text_indexed={document['summary']['machineIndexedTextCount']}")
    print(f"structural_failures={structural_failures}")
    print(
        "human_review_complete="
        f"{document['summary']['humanReviewCompleteCount']}"
    )
    print(
        "human_review_pending="
        f"{document['summary']['humanReviewPendingCount']}"
    )
    print(f"output={arguments.output.resolve()}")
    print(f"ledger={arguments.ledger.resolve()}")
    return 1 if structural_failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1) from error
