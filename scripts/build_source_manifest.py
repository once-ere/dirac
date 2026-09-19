#!/usr/bin/env python3
"""Build a byte-complete, deterministic manifest of the source corpus."""

from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import io
import json
import mimetypes
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


CHUNK_SIZE = 1024 * 1024
AUDIT_CLASSES = {
    "markdown",
    "wolfram-binary",
    "wolfram-notebook",
    "wolfram-source",
}
TEXT_EXTENSIONS = {
    "",
    ".adoc",
    ".bib",
    ".c",
    ".cfg",
    ".cmake",
    ".cpp",
    ".csv",
    ".css",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".ipynb",
    ".java",
    ".js",
    ".json",
    ".m",
    ".md",
    ".markdown",
    ".nb",
    ".ps1",
    ".py",
    ".rs",
    ".rst",
    ".sh",
    ".sql",
    ".svg",
    ".tex",
    ".toml",
    ".ts",
    ".txt",
    ".wl",
    ".wls",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {
    ".gitattributes",
    ".gitignore",
    "cargo.lock",
    "cargo.toml",
    "cmakelists.txt",
    "license",
    "makefile",
    "readme",
}
MEDIA_TYPES = {
    ".ipynb": "application/x-ipynb+json",
    ".m": "text/x-wolfram",
    ".mx": "application/x-wolfram-mx",
    ".nb": "application/x-wolfram-notebook",
    ".wl": "text/x-wolfram",
    ".wls": "text/x-wolfram-script",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/source-roots.json"),
        help="Source-root configuration relative to the current directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("audit"),
        help="Directory that receives generated audit artifacts.",
    )
    return parser.parse_args()


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> tuple[str, int]:
    before = path.stat()
    digest = hashlib.sha256()
    bytes_read = 0
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
            bytes_read += len(chunk)
    after = path.stat()
    if bytes_read != before.st_size or bytes_read != after.st_size:
        raise RuntimeError(
            f"File size changed while hashing {path}: "
            f"before={before.st_size}, "
            f"read={bytes_read}, "
            f"after={after.st_size}"
        )
    if before.st_mtime_ns != after.st_mtime_ns:
        raise RuntimeError(f"File timestamp changed while hashing {path}")
    return digest.hexdigest(), bytes_read


def is_text_candidate(path: Path, extension: str) -> bool:
    return (
        extension in TEXT_EXTENSIONS
        or path.name.casefold() in TEXT_FILENAMES
    )


def encoding_candidates(prefix: bytes) -> list[str]:
    if (
        prefix.startswith(codecs.BOM_UTF32_LE)
        or prefix.startswith(codecs.BOM_UTF32_BE)
    ):
        return ["utf-32"]
    if (
        prefix.startswith(codecs.BOM_UTF16_LE)
        or prefix.startswith(codecs.BOM_UTF16_BE)
    ):
        return ["utf-16"]
    if prefix.startswith(codecs.BOM_UTF8):
        return ["utf-8-sig"]
    if b"\x00" in prefix:
        return []
    return ["utf-8", "cp1252"]


def text_metadata(path: Path, extension: str) -> tuple[str | None, int | None]:
    if not is_text_candidate(path, extension):
        return None, None
    with path.open("rb") as source:
        prefix = source.read(4096)
    for encoding in encoding_candidates(prefix):
        try:
            with path.open(
                "r",
                encoding=encoding,
                errors="strict",
                newline=None,
            ) as source:
                line_count = sum(1 for _ in source)
            return encoding, line_count
        except UnicodeDecodeError:
            continue
    return None, None


def media_type(path: Path, extension: str, encoding: str | None) -> str:
    if extension in MEDIA_TYPES:
        return MEDIA_TYPES[extension]
    guessed, _ = mimetypes.guess_type(path.name, strict=False)
    if guessed:
        return guessed
    if encoding is not None:
        return "text/plain"
    return "application/octet-stream"


def m_source_class(path: Path, encoding: str | None) -> str:
    if encoding is None:
        return "binary"
    with path.open("r", encoding=encoding, errors="strict") as source:
        for line in source:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("%"):
                return "matlab-source"
            return "wolfram-source"
    return "wolfram-source"


def audit_class(path: Path, extension: str, encoding: str | None) -> str:
    if extension in {".md", ".markdown"}:
        return "markdown"
    if extension == ".nb":
        return "wolfram-notebook"
    if extension == ".m":
        return m_source_class(path, encoding)
    if extension in {".wl", ".wls"}:
        return "wolfram-source"
    if extension == ".mx":
        return "wolfram-binary"
    if extension == ".ipynb":
        return "jupyter-notebook"
    if extension == ".tex":
        return "latex-source"
    if extension == ".pdf":
        return "pdf"
    if extension in {".7z", ".bz2", ".gz", ".tar", ".xz", ".zip"}:
        return "archive"
    if extension in {
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".js",
        ".ps1",
        ".py",
        ".rs",
        ".sh",
        ".ts",
    }:
        return "source-code"
    if encoding is not None:
        return "other-text"
    return "binary"


def iter_files(root: Path) -> Iterable[Path]:
    paths: list[Path] = []
    walker = os.walk(root, followlinks=False)
    for directory, directory_names, file_names in walker:
        directory_names.sort(key=lambda value: (value.casefold(), value))
        file_names.sort(key=lambda value: (value.casefold(), value))
        current = Path(directory)
        for file_name in file_names:
            path = current / file_name
            if path.is_symlink():
                raise RuntimeError(
                    f"Symbolic-link files require explicit handling: {path}"
                )
            if not path.is_file():
                raise RuntimeError(
                    f"Directory walk returned a non-file: {path}"
                )
            paths.append(path)
    yield from sorted(
        paths,
        key=lambda path: (
            path.relative_to(root).as_posix().casefold(),
            path.relative_to(root).as_posix(),
        ),
    )


def load_roots(
    config_path: Path,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes.decode("utf-8"))
    if config.get("schemaVersion") != 1:
        raise ValueError("Unsupported source-root configuration schema")
    project_root = config_path.parent.parent.resolve()
    base_directory = (project_root / config["baseDirectory"]).resolve()
    roots: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for item in config["roots"]:
        root_id = item["id"]
        if root_id in seen_ids:
            raise ValueError(f"Duplicate source-root id: {root_id}")
        seen_ids.add(root_id)
        path = (base_directory / item["directory"]).resolve()
        if not path.is_dir():
            raise FileNotFoundError(f"Missing source root {root_id}: {path}")
        roots.append({"id": root_id, "path": str(path)})
    return {
        "schemaVersion": config["schemaVersion"],
        "sha256": hash_bytes(config_bytes),
        "path": config_path.resolve().as_posix(),
    }, roots


def inventory(roots: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root in roots:
        root_path = Path(root["path"])
        for path in iter_files(root_path):
            relative_path = path.relative_to(root_path).as_posix()
            if "\n" in relative_path or "\r" in relative_path:
                raise RuntimeError(f"Unsafe control character in path: {path}")
            extension = path.suffix.casefold()
            digest, bytes_read = hash_file(path)
            encoding, line_count = text_metadata(path, extension)
            records.append(
                {
                    "rootId": root["id"],
                    "rootPath": root["path"],
                    "relativePath": relative_path,
                    "logicalPath": f"{root['id']}/{relative_path}",
                    "size": bytes_read,
                    "bytesRead": bytes_read,
                    "sha256": digest,
                    "extension": extension,
                    "mediaType": media_type(path, extension, encoding),
                    "encoding": encoding,
                    "lineCount": line_count,
                    "auditClass": audit_class(path, extension, encoding),
                }
            )
    return records


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


def render_json(
    config_record: dict[str, Any],
    roots: list[dict[str, str]],
    records: list[dict[str, Any]],
) -> str:
    class_counts = Counter(record["auditClass"] for record in records)
    document = {
        "schemaVersion": 1,
        "hashAlgorithm": "SHA-256",
        "configuration": config_record,
        "roots": roots,
        "summary": {
            "rootCount": len(roots),
            "fileCount": len(records),
            "totalBytes": sum(record["size"] for record in records),
            "auditFileCount": sum(
                record["auditClass"] in AUDIT_CLASSES for record in records
            ),
            "classCounts": dict(sorted(class_counts.items())),
        },
        "files": records,
    }
    return json.dumps(document, indent=2, ensure_ascii=True) + "\n"


def render_csv(records: list[dict[str, Any]]) -> str:
    columns = [
        "rootId",
        "relativePath",
        "logicalPath",
        "size",
        "bytesRead",
        "sha256",
        "extension",
        "mediaType",
        "encoding",
        "lineCount",
        "auditClass",
        "rootPath",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def render_checksums(records: list[dict[str, Any]]) -> str:
    return "".join(
        f"{record['sha256']}  {record['logicalPath']}\n"
        for record in records
    )


def markdown_cell(value: object) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def ledger_status(record: dict[str, Any]) -> tuple[str, str, str]:
    artifact_class = record["auditClass"]
    if artifact_class == "markdown":
        return "pending", "not-applicable", "not-applicable"
    if artifact_class == "wolfram-notebook":
        return "pending", "pending", "pending"
    if artifact_class == "wolfram-source":
        return "pending", "not-applicable", "pending"
    if artifact_class == "wolfram-binary":
        return "not-applicable", "hash-only", "not-applicable"
    raise ValueError(f"Unexpected ledger class: {artifact_class}")


def render_ledger(records: list[dict[str, Any]]) -> str:
    audited = [
        record
        for record in records
        if record["auditClass"] in AUDIT_CLASSES
    ]
    lines = [
        "# Source audit ledger",
        "",
        (
            "This ledger is generated from `source-manifest.json`. "
            "Embedded notebook output is not accepted as proof."
        ),
        "",
        (
            "| Root | Path | Class | Bytes | SHA-256 | Byte coverage | "
            "Authored review | Structural import | Execution | Relevance | "
            "Defects | Disposition |"
        ),
        "|---|---|---:|---:|---|---|---|---|---|---|---|---|",
    ]
    for record in audited:
        authored, structural, execution = ledger_status(record)
        values = [
            record["rootId"],
            record["relativePath"],
            record["auditClass"],
            record["size"],
            record["sha256"],
            "complete",
            authored,
            structural,
            execution,
            "pending",
            "pending",
            "pending",
        ]
        row = " | ".join(markdown_cell(value) for value in values)
        lines.append(f"| {row} |")
    lines.extend(["", f"Audit artifacts: {len(audited)}", ""])
    return "\n".join(lines)


def main() -> int:
    arguments = parse_arguments()
    config_path = arguments.config.resolve()
    output_directory = arguments.output_dir.resolve()
    config_record, roots = load_roots(config_path)
    records = inventory(roots)
    atomic_write(
        output_directory / "source-manifest.json",
        render_json(config_record, roots, records),
    )
    atomic_write(output_directory / "source-manifest.csv", render_csv(records))
    atomic_write(output_directory / "SHA256SUMS", render_checksums(records))
    atomic_write(output_directory / "audit-ledger.md", render_ledger(records))
    audit_file_count = sum(
        record["auditClass"] in AUDIT_CLASSES for record in records
    )
    print(f"source_roots={len(roots)}")
    print(f"files={len(records)}")
    print(f"bytes={sum(record['size'] for record in records)}")
    print(f"audit_files={audit_file_count}")
    print(f"output={output_directory}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
