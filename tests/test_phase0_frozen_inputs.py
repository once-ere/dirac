from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_phase0


class Phase0FrozenInputTests(unittest.TestCase):
    def test_local_prompt_may_be_absent_when_tracked_backup_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory)
            backup_root = repository_root / "backups" / "pre-bootstrap"
            backup_root.mkdir(parents=True)
            files = {
                "prompt.txt": b"private prompt\n",
                "19sep26.txt": b"tracked specification\n",
            }
            records = []
            for name, content in files.items():
                digest = hashlib.sha256(content).hexdigest().upper()
                (backup_root / name).write_bytes(content)
                records.append(
                    {
                        "name": name,
                        "sourceHash": digest,
                        "sourceSize": len(content),
                        "backupHash": digest,
                        "backupSize": len(content),
                        "backupMatch": True,
                    }
                )
            (repository_root / "19sep26.txt").write_bytes(files["19sep26.txt"])
            (backup_root / "manifest.json").write_text(
                json.dumps(
                    {
                        "files": records,
                        "verification": {"allFilesMatched": True},
                    }
                ),
                encoding="utf-8",
            )

            original_root = check_phase0.REPOSITORY_ROOT
            check_phase0.REPOSITORY_ROOT = repository_root
            try:
                check_phase0.validate_frozen_inputs()
            finally:
                check_phase0.REPOSITORY_ROOT = original_root