#!/usr/bin/env python3
"""Create immutable, hash-verified backups of repository files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


CHUNK_SIZE = 1024 * 1024


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=Path("backups/edits"),
    )
    return parser.parse_args()


def file_hash(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def atomic_json(path: Path, value: object) -> None:
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
            json.dump(value, target, indent=2, ensure_ascii=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path(__file__).resolve().parent.parent
    backup_root = (repository_root / arguments.backup_root).resolve()
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination_root = backup_root / backup_id
    destination_root.mkdir(parents=True, exist_ok=False)

    files = []
    for requested_path in arguments.paths:
        source = (repository_root / requested_path).resolve()
        try:
            relative_path = source.relative_to(repository_root)
        except ValueError as error:
            raise ValueError(
                f"Path is outside the repository: {source}"
            ) from error
        if not source.is_file():
            raise FileNotFoundError(f"Cannot back up missing file: {source}")

        destination = destination_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(
                f"Backup destination already exists: {destination}"
            )

        source_hash, source_size = file_hash(source)
        shutil.copy2(source, destination)
        backup_hash, backup_size = file_hash(destination)
        if source_hash != backup_hash or source_size != backup_size:
            raise RuntimeError(f"Backup verification failed: {relative_path}")
        files.append(
            {
                "relativePath": relative_path.as_posix(),
                "sourceSha256": source_hash,
                "sourceSize": source_size,
                "backupSha256": backup_hash,
                "backupSize": backup_size,
                "match": True,
            }
        )

    manifest = {
        "schemaVersion": 1,
        "backupId": backup_id,
        "repositoryRoot": str(repository_root),
        "destinationRoot": str(destination_root),
        "files": files,
        "allFilesMatched": True,
    }
    atomic_json(destination_root / "manifest.json", manifest)
    print(f"backup_id={backup_id}")
    print(f"files={len(files)}")
    print("all_files_matched=true")
    print(f"manifest={destination_root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
