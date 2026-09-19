from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_source_manifest as subject


class SourceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "fixture"
        (self.root / "nested").mkdir(parents=True)
        (self.root / "b.md").write_text("# Title\nBody\n", encoding="utf-8")
        (self.root / "a.nb").write_text(
            'Notebook[{Cell["Exact", "Text"]}]\n',
            encoding="utf-8",
        )
        (self.root / "binary.mx").write_bytes(b"\x00\x01\xff")
        (self.root / "nested" / "model.rs").write_text(
            "fn main() {}\n",
            encoding="utf-8",
        )

    def records(self) -> list[dict[str, object]]:
        roots = [{"id": "fixture", "path": str(self.root.resolve())}]
        return subject.inventory(roots)

    def test_configuration_path_is_repository_relative(self) -> None:
        project_root = Path(self.temporary_directory.name) / "project"
        config_directory = project_root / "config"
        source_root = project_root / "sources"
        config_directory.mkdir(parents=True)
        source_root.mkdir()
        config_path = config_directory / "source-roots.json"
        config_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "baseDirectory": ".",
                    "roots": [{"id": "fixture", "directory": "sources"}],
                }
            ),
            encoding="utf-8",
        )

        config_record, roots = subject.load_roots(config_path)

        self.assertEqual(config_record["path"], "config/source-roots.json")
        self.assertEqual(roots[0]["path"], str(source_root.resolve()))

    def test_inventory_is_sorted_and_byte_complete(self) -> None:
        records = self.records()
        self.assertEqual(
            [record["relativePath"] for record in records],
            ["a.nb", "b.md", "binary.mx", "nested/model.rs"],
        )
        for record in records:
            path = self.root / str(record["relativePath"])
            content = path.read_bytes()
            self.assertEqual(record["size"], len(content))
            self.assertEqual(record["bytesRead"], len(content))
            self.assertEqual(
                record["sha256"],
                hashlib.sha256(content).hexdigest(),
            )

    def test_text_and_artifact_classification(self) -> None:
        records = {
            record["relativePath"]: record for record in self.records()
        }
        self.assertEqual(records["a.nb"]["auditClass"], "wolfram-notebook")
        self.assertEqual(records["a.nb"]["encoding"], "utf-8")
        self.assertEqual(records["a.nb"]["lineCount"], 1)
        self.assertEqual(records["b.md"]["auditClass"], "markdown")
        self.assertEqual(records["b.md"]["lineCount"], 2)
        self.assertEqual(records["binary.mx"]["auditClass"], "wolfram-binary")
        self.assertIsNone(records["binary.mx"]["encoding"])
        self.assertEqual(
            records["nested/model.rs"]["auditClass"],
            "source-code",
        )

    def test_renderers_are_deterministic_and_cover_audit_files(self) -> None:
        records = self.records()
        roots = [{"id": "fixture", "path": str(self.root.resolve())}]
        config = {
            "schemaVersion": 1,
            "sha256": "0" * 64,
            "path": "fixture.json",
        }
        first_json = subject.render_json(config, roots, records)
        self.assertEqual(
            first_json,
            subject.render_json(config, roots, records),
        )
        document = json.loads(first_json)
        self.assertEqual(document["summary"]["fileCount"], 4)
        self.assertEqual(document["summary"]["auditFileCount"], 3)

        checksums = subject.render_checksums(records).splitlines()
        self.assertEqual(len(checksums), 4)
        self.assertTrue(checksums[0].endswith("  fixture/a.nb"))

        ledger = subject.render_ledger(records)
        self.assertIn("fixture | a.nb | wolfram-notebook", ledger)
        self.assertIn("fixture | b.md | markdown", ledger)
        self.assertIn("fixture | binary.mx | wolfram-binary", ledger)
        self.assertNotIn("nested/model.rs", ledger)
        self.assertTrue(ledger.endswith("Audit artifacts: 3\n"))

    def test_atomic_write_replaces_complete_content(self) -> None:
        destination = Path(self.temporary_directory.name) / "result.txt"
        subject.atomic_write(destination, "first\n")
        subject.atomic_write(destination, "second\n")
        self.assertEqual(destination.read_bytes(), b"second\n")
        self.assertEqual(list(destination.parent.glob(".result.txt.*")), [])

    def test_m_extension_is_classified_by_content(self) -> None:
        matlab = self.root / "plot.m"
        wolfram = self.root / "package.m"
        matlab.write_text("% MATLAB comment\nclear\n", encoding="utf-8")
        wolfram.write_text(
            "(* Wolfram comment *)\nvalue = 1;\n",
            encoding="utf-8",
        )
        records = {
            record["relativePath"]: record for record in self.records()
        }
        self.assertEqual(records["plot.m"]["auditClass"], "matlab-source")
        self.assertEqual(records["package.m"]["auditClass"], "wolfram-source")


if __name__ == "__main__":
    unittest.main()
