import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from scripts.normalize_collection import (
    NORMALIZED_FIELDS,
    _detect_encoding,
    _document_type,
    _parse_year,
    normalize_project,
)


class NormalizeCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()
        (self.root / "dados" / "brutos").mkdir(parents=True)
        (self.root / "dados" / "logs").mkdir(parents=True)
        self.inventory_rows = []
        self.execution_rows = []

    def tearDown(self):
        self.temporary_directory.cleanup()

    def register_raw(self, source, filename, content, record_count=None):
        raw_directory = self.root / "dados" / "brutos" / source
        raw_directory.mkdir(parents=True, exist_ok=True)
        raw_path = raw_directory / filename
        raw_path.write_bytes(content)
        relative = raw_path.relative_to(self.root).as_posix()
        run_id = f"run-{len(self.inventory_rows) + 1}"
        self.inventory_rows.append(
            {
                "raw_file": relative,
                "source": source,
                "source_run_id": run_id,
                "captured_at": "2026-11-08T12:00:00-03:00",
            }
        )
        self.execution_rows.append(
            {
                "source_run_id": run_id,
                "records_exported": "" if record_count is None else str(record_count),
                "output_files": json.dumps([relative]),
            }
        )
        return raw_path, relative

    def write_manifests(self):
        inventory = self.root / "dados" / "logs" / "arquivos.csv"
        with inventory.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["raw_file", "source", "source_run_id", "captured_at"],
            )
            writer.writeheader()
            writer.writerows(self.inventory_rows)
        manifest = self.root / "dados" / "logs" / "execucoes.csv"
        with manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["source_run_id", "records_exported", "output_files"],
            )
            writer.writeheader()
            writer.writerows(self.execution_rows)

    def read_csv(self, path):
        with path.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_document_types_keep_masters_and_doctorates_distinct(self):
        self.assertEqual(_document_type("masterThesis", "bdtd"), "dissertation")
        self.assertEqual(_document_type("doctoralThesis", "bdtd"), "thesis")
        self.assertEqual(_document_type("JOUR", "scielo"), "article")
        self.assertEqual(_document_type("Editorial", "portal-capes"), "other_academic")
        self.assertIsNone(_parse_year("20241"))

    def test_encoding_detection_uses_replacement_for_undefined_cp1252_bytes(self):
        latin1_file = Path(self.temporary_directory.name) / "latin1.csv"
        latin1_file.write_bytes("título;conteúdo\n".encode("latin-1"))
        self.assertEqual(_detect_encoding(latin1_file), "cp1252")

        mixed_file = Path(self.temporary_directory.name) / "mixed.csv"
        mixed_file.write_bytes(b"col\n" + bytes([0x9D]))
        self.assertEqual(_detect_encoding(mixed_file), "cp1252-replace")

    def test_capes_encoding_fallback_avoids_c1_control_corruption(self):
        content = (
            b"ID_PRODUCAO_INTELECTUAL;NM_SUBTIPO_PRODUCAO;NM_PRODUCAO;"
            b"DT_TITULACAO\n1;DISSERTA\xc7\xc3O;A\x93B\x9d;01JAN2024\n"
        )
        self.register_raw("catalogo-capes", "capes.csv", content, 1)
        self.write_manifests()

        result = normalize_project(self.root)

        record = self.read_csv(result["paths"]["records"])[0]
        quality = self.read_csv(result["paths"]["quality"])[0]
        self.assertEqual(record["title"], "A\u201cB\ufffd")
        self.assertEqual(quality["encoding"], "cp1252-replace")
        self.assertEqual(quality["c1_control_characters"], "0")
        self.assertEqual(quality["decode_replacement_characters"], "1")

    def test_expected_count_uses_any_manifest_run_for_the_same_raw_file(self):
        _, relative = self.register_raw("bdtd", "count.csv", b"", None)
        self.execution_rows.append(
            {
                "source_run_id": "later-count-check",
                "records_exported": "0",
                "output_files": json.dumps([relative]),
            }
        )
        self.write_manifests()

        result = normalize_project(self.root)

        quality = self.read_csv(result["paths"]["quality"])[0]
        self.assertEqual(quality["expected_records"], "0")
        self.assertEqual(quality["record_count_matches_expected"], "true")

    def test_normalizes_formats_preserves_raw_files_and_stable_ids(self):
        ris = (
            "\ufeffTY  - JOUR\n"
            "ID  - scielo-1\n"
            "TI  - Artigo de teste\n"
            "AU  - Autora Um\n"
            "AU  - Autor Dois\n"
            "PY  - 2025\n"
            "AB  - Resumo\n"
            "KW  - PIBID\n"
            "JO  - Revista\n"
            "DO  - 10.1/teste\n"
            "ER  -\n"
        ).encode("utf-8")
        ris_path, _ = self.register_raw("scielo", "sample.ris", ris, 1)

        bdtd_csv = (
            "Autor(a),Título,Ano de defesa,Instituição de defesa,Tipo de documento,"
            "Assuntos em português,Resumo,Identificador persistente ARK\n"
            "Pessoa,""Dissertação PIBID"",2018,Universidade X,masterThesis,"
            "PIBID||Formação,Resumo BDTD,\n"
        ).encode("utf-8")
        bdtd_path, _ = self.register_raw("bdtd", "sample.csv", bdtd_csv, 1)

        zip_content = (
            "Autor(a),Título,Ano de defesa,Instituição de defesa,Tipo de documento\n"
            "Pessoa,Dissertação Goiás,2020,Universidade Y,masterThesis\n"
        ).encode("utf-8")
        zip_path = self.root / "dados" / "brutos" / "bdtd" / "regional.zip"
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("regional.csv", zip_content)
        zip_relative = zip_path.relative_to(self.root).as_posix()
        self.inventory_rows.append(
            {
                "raw_file": zip_relative,
                "source": "bdtd",
                "source_run_id": "run-3",
                "captured_at": "2026-11-08T12:00:00-03:00",
            }
        )
        self.execution_rows.append(
            {
                "source_run_id": "run-3",
                "records_exported": "1",
                "output_files": json.dumps([zip_relative]),
            }
        )

        catalog_headers = (
            "ID_PRODUCAO_INTELECTUAL;NM_SUBTIPO_PRODUCAO;NM_PRODUCAO;"
            "DT_TITULACAO;NM_ENTIDADE_ENSINO;NM_PROGRAMA;NM_DISCENTE;"
            "DS_PALAVRA_CHAVE;DS_RESUMO;DS_URL_TEXTO_COMPLETO;NM_IDIOMA\n"
        )
        catalog_row = (
            "123;DISSERTAÇÃO;Tese PIBID;03MAR2024:00:00:00;"
            "IES;Programa;Discente;PIBID;Resumo;https://example.test/1;pt\n"
        )
        catalog_path, _ = self.register_raw(
            "catalogo-capes",
            "catalogo.csv",
            (catalog_headers + catalog_row).encode("utf-8"),
            1,
        )
        original_hashes = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ris_path, bdtd_path, zip_path, catalog_path)
        }
        self.write_manifests()

        first = normalize_project(self.root)
        first_records = self.read_csv(first["paths"]["records"])
        second = normalize_project(self.root)
        second_records = self.read_csv(second["paths"]["records"])

        self.assertEqual(len(first_records), 4)
        self.assertEqual(
            [row["record_id"] for row in first_records],
            [row["record_id"] for row in second_records],
        )
        self.assertEqual(first_records[0]["authors_json"], '["Autora Um","Autor Dois"]')
        self.assertEqual(first_records[0]["publication_year"], "2025")
        self.assertEqual(first_records[0]["defense_year"], "")
        self.assertEqual(first_records[1]["publication_year"], "")
        self.assertEqual(first_records[1]["defense_year"], "2018")
        self.assertEqual(first_records[1]["document_type_normalized"], "dissertation")
        self.assertEqual(first_records[2]["source_metadata_json"], '{"__archive_member__":"regional.csv"}')
        self.assertEqual(first_records[3]["defense_year"], "2024")
        self.assertEqual(first_records[3]["publication_year"], "")
        self.assertEqual(set(first_records[0]), set(NORMALIZED_FIELDS))
        for path, digest in original_hashes.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

        quality = self.read_csv(first["paths"]["quality"])
        self.assertEqual(len(quality), 4)
        self.assertTrue(all(row["record_count_matches_expected"] == "true" for row in quality))
        institutions = self.read_csv(first["paths"]["institutions"])
        institution_rows = {row["institution_original"]: row for row in institutions}
        self.assertEqual(
            set(institution_rows),
            {"IES", "Universidade X", "Universidade Y"},
        )
        self.assertTrue(
            all(
                row["status"] == "pending" and row["institution_normalized"] == ""
                for row in institutions
            )
        )
        self.assertEqual(institution_rows["Universidade X"]["occurrences"], "1")
        issues = self.read_csv(first["paths"]["issues"])
        self.assertEqual(
            [row["issue"] for row in issues],
            ["missing_source_record_id", "missing_source_record_id"],
        )
        with (self.root / "dados" / "logs" / "normalizacoes.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            log_rows = list(csv.DictReader(stream))
        self.assertEqual([row["status"] for row in log_rows], ["completed", "completed"])

    def test_quality_report_marks_missing_and_out_of_period_values(self):
        csv_content = (
            "Autor(a),Título,Ano de defesa,Instituição de defesa,Tipo de documento\n"
            "Pessoa,,2006,Universidade X,masterThesis\n"
            "Pessoa,Título,ano inválido,Universidade X,masterThesis\n"
        ).encode("utf-8")
        self.register_raw("bdtd", "quality.csv", csv_content, 2)
        self.write_manifests()

        result = normalize_project(self.root)

        quality = self.read_csv(result["paths"]["quality"])[0]
        self.assertEqual(quality["missing_title_records"], "1")
        self.assertEqual(quality["out_of_period_records"], "1")
        self.assertEqual(quality["invalid_year_records"], "1")
        issues = self.read_csv(result["paths"]["issues"])
        self.assertEqual(
            {row["issue"] for row in issues},
            {"missing_title", "out_of_period", "invalid_year", "missing_source_record_id"},
        )

    def test_missing_registered_file_fails_and_is_logged(self):
        self.register_raw("bdtd", "missing.csv", b"", 0)
        (self.root / "dados" / "brutos" / "bdtd" / "missing.csv").unlink()
        self.write_manifests()

        with self.assertRaisesRegex(FileNotFoundError, "registered raw file is missing"):
            normalize_project(self.root)

        with (self.root / "dados" / "logs" / "normalizacoes.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["status"], "failed")


if __name__ == "__main__":
    unittest.main()
