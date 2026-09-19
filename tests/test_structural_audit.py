from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_structural_audit as subject


class StructuralAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def manifest_record(
        self,
        path: Path,
        artifact_class: str,
        encoding: str | None,
    ) -> dict[str, object]:
        content = path.read_bytes()
        return {
            "logicalPath": f"fixture/{path.name}",
            "rootId": "fixture",
            "rootPath": str(self.root),
            "relativePath": path.name,
            "auditClass": artifact_class,
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "encoding": encoding,
            "lineCount": content.count(b"\n"),
        }

    def test_text_analysis_processes_every_line_and_word(self) -> None:
        path = self.root / "guide.md"
        path.write_text("# Heading\nTwo words.\n", encoding="utf-8")
        result = subject.analyze_text(path, "utf-8", "markdown")
        self.assertEqual(result["lineCount"], 2)
        self.assertEqual(result["wordCount"], 3)
        self.assertEqual(result["markdownHeadings"][0]["text"], "Heading")
        self.assertEqual(len(result["lineStreamSha256"]), 64)
        self.assertEqual(len(result["wordStreamSha256"]), 64)

    def test_build_records_merges_wolfram_structure(self) -> None:
        source = self.root / "model.wl"
        source.write_text("value = 1;\n", encoding="utf-8")
        source_record = self.manifest_record(
            source,
            "wolfram-source",
            "utf-8",
        )
        digest = source_record["sha256"]
        manifest = {"files": [source_record]}
        wolfram = {
            "files": [
                {
                    "logicalPath": source_record["logicalPath"],
                    "parseStatus": "parsed",
                    "sha256": digest,
                    "hashMatchesManifest": True,
                    "sizeMatchesManifest": True,
                }
            ]
        }
        records = subject.build_records(manifest, wolfram)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["structuralImport"], "parsed")
        self.assertEqual(
            records[0]["authoredReview"],
            "machine-indexed-human-pending",
        )

    def test_binary_artifact_is_hash_only(self) -> None:
        binary = self.root / "state.mx"
        binary.write_bytes(b"\x00\x01")
        manifest = {
            "files": [self.manifest_record(binary, "wolfram-binary", None)]
        }
        records = subject.build_records(manifest, {"files": []})
        self.assertEqual(records[0]["structuralImport"], "hash-only")
        self.assertIsNone(records[0]["textEvidence"])

    def test_human_review_decision_overlays_pending_fields(self) -> None:
        path = self.root / "guide.md"
        path.write_text("# Guide\n", encoding="utf-8")
        source_record = self.manifest_record(path, "markdown", "utf-8")
        decision = {
            "logicalPath": source_record["logicalPath"],
            "authoredReview": "complete",
            "execution": "not-required",
            "relevance": "low",
            "defects": "none",
            "disposition": "historical-evidence",
            "reviewSource": "audit/reviews/fixture.md",
        }
        records = subject.build_records(
            {"files": [source_record]},
            {"files": []},
            {source_record["logicalPath"]: decision},
        )
        self.assertEqual(records[0]["authoredReview"], "complete")
        self.assertEqual(
            records[0]["humanReviewEvidence"],
            "audit/reviews/fixture.md",
        )

    def test_root_review_expands_to_each_audit_artifact(self) -> None:
        decisions_path = self.root / "decisions.json"
        decisions_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "decisions": [],
                    "rootReviews": [
                        {
                            "rootId": "fixture",
                            "authoredReview": "complete",
                            "execution": "see-review",
                            "relevance": "mixed",
                            "defects": "see-review",
                            "disposition": "mixed-see-review",
                            "reviewSource": "audit/reviews/fixture.md",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        manifest = {
            "roots": [{"id": "fixture"}],
            "files": [
                {
                    "rootId": "fixture",
                    "logicalPath": "fixture/a.md",
                    "auditClass": "markdown",
                },
                {
                    "rootId": "fixture",
                    "logicalPath": "fixture/a.py",
                    "auditClass": "source-code",
                },
            ],
        }
        decisions = subject.load_decisions(decisions_path, manifest)
        self.assertEqual(set(decisions), {"fixture/a.md"})
        self.assertEqual(decisions["fixture/a.md"]["relevance"], "mixed")

    def test_ledger_escapes_table_delimiters(self) -> None:
        record = {
            "rootId": "fixture",
            "relativePath": "a|b.md",
            "auditClass": "markdown",
            "size": 1,
            "sha256": "0" * 64,
            "byteCoverage": "complete",
            "authoredReview": "machine-indexed-human-pending",
            "structuralImport": "not-applicable",
            "execution": "pending",
            "relevance": "pending",
            "defects": "pending",
            "disposition": "pending",
        }
        ledger = subject.render_ledger([record])
        self.assertIn("a\\|b.md", ledger)
        self.assertTrue(ledger.endswith("Audit artifacts: 1\n"))


if __name__ == "__main__":
    unittest.main()
