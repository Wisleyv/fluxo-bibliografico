import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.audit_character_issues import audit
from scripts.capture_collection import capture_file
from scripts.normalize_collection import normalize_project


class CharacterAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def capture(self, source, filename, content):
        path = Path(self.temporary.name) / filename
        path.write_bytes(content)
        return capture_file(
            project_root=self.root,
            source=source,
            query_id="test",
            query_literal="PIBID",
            input_file=path,
            method="manual_capture",
            records_exported=1,
        )

    def test_identifies_original_fields_and_preserves_input(self):
        bdtd = self.capture(
            "bdtd",
            "bdtd.csv",
            (
                "Autor(a),Título,Ano de defesa,Resumo\n"
                "Pessoa,Título\u0096teste,2024,Resumo\u0093texto\u0094\n"
            ).encode("utf-8"),
        )
        capes = self.capture(
            "catalogo-capes",
            "catalogo.csv",
            b"ID_PRODUCAO_INTELECTUAL;NM_SUBTIPO_PRODUCAO;NM_PRODUCAO;"
            b"DT_TITULACAO;DS_RESUMO\n"
            b"1;DISSERTACAO;PIBID;01JAN2024;A\x93B\x9d\n",
        )
        generation = normalize_project(self.root)
        before = {
            entry.raw_file: hashlib.sha256((self.root / entry.raw_file).read_bytes()).hexdigest()
            for entry in (bdtd, capes)
        }

        rows, _ = audit(self.root, generation["normalization_run_id"])

        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [(r["source_field"], r["original_code"]) for r in rows],
            [
                ("Título", "U+0096"),
                ("Resumo", "U+0093"),
                ("Resumo", "U+0094"),
                ("DS_RESUMO", "0x9D"),
            ],
        )
        self.assertIn("A\u201cB[byte 0x9D]", rows[-1]["context"])
        self.assertTrue(all(r["review_status"] == "pending" for r in rows))
        for raw_file, digest in before.items():
            self.assertEqual(hashlib.sha256((self.root / raw_file).read_bytes()).hexdigest(), digest)

    def test_refuses_raw_checksum_mismatch(self):
        capture = self.capture(
            "bdtd",
            "bdtd.csv",
            "Título,Ano de defesa\nA\u0096B,2024\n".encode("utf-8"),
        )
        generation = normalize_project(self.root)
        (self.root / capture.raw_file).write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            audit(self.root, generation["normalization_run_id"])

    def test_rejects_mismatched_character_report(self):
        self.capture(
            "bdtd",
            "bdtd.csv",
            "Título,Ano de defesa\nA\u0096B,2024\n".encode("utf-8"),
        )
        generation = normalize_project(self.root)
        issue_path = generation["paths"]["issues"]
        with issue_path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            rows = list(reader)
        for row in rows:
            if row["issue"] == "c1_control_character":
                row["raw_value"] = '{"U+0096": 2}'
        with issue_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, "character count mismatch"):
            audit(self.root, generation["normalization_run_id"])


if __name__ == "__main__":
    unittest.main()
