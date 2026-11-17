import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from unittest.mock import patch

from scripts.capture_collection import (
    QUERY_TEMPLATES,
    capture_file,
    download_open_data,
    record_search,
)


class CaptureCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "project"
        self.root.mkdir()
        self.input_directory = Path(self.temporary_directory.name) / "input"
        self.input_directory.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def capture(self, file_path):
        return capture_file(
            project_root=self.root,
            source="portal-capes",
            query_id="national search",
            query_literal='PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"',
            input_file=file_path,
            method="assisted_export",
            searched_fields="title,abstract",
            filters_json='{"publication_year": "2007:2026"}',
            source_reported_count=2777,
            records_exported=1,
        )

    def read_rows(self, relative_path):
        with (self.root / relative_path).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_capture_preserves_bytes_and_registers_metadata(self):
        content = b"TY  - article\r\nTI  - A title\r\nER  -\r\n"
        input_path = self.input_directory / "sample.ris"
        input_path.write_bytes(content)

        result = self.capture(input_path)

        raw_path = self.root / result.raw_file
        self.assertEqual(raw_path.read_bytes(), content)
        self.assertEqual(result.sha256, hashlib.sha256(content).hexdigest())
        self.assertEqual(result.status, "captured")
        self.assertIn("portal-capes__national-search__", result.raw_file)

        executions = self.read_rows("dados/logs/execucoes.csv")
        files = self.read_rows("dados/logs/arquivos.csv")
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "captured")
        self.assertEqual(executions[0]["source_reported_count"], "2777")
        self.assertEqual(executions[0]["records_exported"], "1")
        self.assertEqual(files[0]["sha256"], result.sha256)
        self.assertEqual(files[0]["bytes"], str(len(content)))

    def test_capture_preserves_zip_export_without_modification(self):
        input_path = self.input_directory / "export.zip"
        with ZipFile(input_path, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("records.csv", "title,year\nPIBID,2024\n")
        original_bytes = input_path.read_bytes()

        result = capture_file(
            project_root=self.root,
            source="bdtd",
            query_id="goias-descriptors",
            query_literal='(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência") '
            'AND ("Goiás" OR "goiano" OR "goiana")',
            input_file=input_path,
            method="assisted_export",
            source_reported_count=42,
            records_exported=42,
        )

        raw_path = self.root / result.raw_file
        self.assertEqual(raw_path.read_bytes(), original_bytes)
        self.assertTrue(result.raw_file.endswith(".zip"))
        with ZipFile(raw_path) as archive:
            self.assertEqual(archive.read("records.csv"), b"title,year\nPIBID,2024\n")

    def test_identical_export_is_logged_without_duplicate_raw_file(self):
        content = b"TY  - article\nID  - same\nER  -\n"
        first = self.input_directory / "first.ris"
        second = self.input_directory / "second.ris"
        first.write_bytes(content)
        second.write_bytes(content)

        first_result = self.capture(first)
        second_result = self.capture(second)

        self.assertEqual(first_result.status, "captured")
        self.assertEqual(second_result.status, "duplicate_skipped")
        self.assertEqual(first_result.raw_file, second_result.raw_file)
        self.assertEqual(len(list((self.root / "dados/brutos/portal-capes").glob("*.ris"))), 1)
        self.assertEqual(len(self.read_rows("dados/logs/arquivos.csv")), 1)
        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual([row["status"] for row in executions], ["captured", "duplicate_skipped"])

    def test_identical_bytes_from_different_sources_are_preserved_separately(self):
        content = b"TY  - article\nID  - same\nER  -\n"
        portal_file = self.input_directory / "portal.ris"
        scielo_file = self.input_directory / "scielo.ris"
        portal_file.write_bytes(content)
        scielo_file.write_bytes(content)

        portal_result = self.capture(portal_file)
        scielo_result = capture_file(
            project_root=self.root,
            source="scielo",
            query_id="manual-search",
            query_literal="PIBID",
            input_file=scielo_file,
            method="manual_capture",
        )

        self.assertEqual(portal_result.status, "captured")
        self.assertEqual(scielo_result.status, "captured")
        self.assertNotEqual(portal_result.raw_file, scielo_result.raw_file)
        self.assertEqual(len(self.read_rows("dados/logs/arquivos.csv")), 2)

    def test_failure_is_logged_and_original_is_not_copied(self):
        input_path = self.input_directory / "unexpected.json"
        input_path.write_text("{}", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "unsupported file extension"):
            self.capture(input_path)

        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "failed")
        self.assertIn("unsupported file extension", executions[0]["notes"])
        self.assertFalse((self.root / "dados/brutos/portal-capes").exists())

    def test_scholar_automation_method_is_rejected_and_logged(self):
        input_path = self.input_directory / "capture.ris"
        input_path.write_text("TY  - article\nER  -\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "limited to manual_search"):
            capture_file(
                project_root=self.root,
                source="google-scholar",
                query_id="exploratory",
                query_literal="PIBID",
                input_file=input_path,
                method="assisted_export",
            )

        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(executions[0]["status"], "failed")
        self.assertIn("limited to manual_search", executions[0]["notes"])

    def test_regional_query_template_includes_all_protocol_descriptors(self):
        query_id, query = QUERY_TEMPLATES["goias"]

        self.assertEqual(query_id, "goias-descriptors")
        self.assertIn('"Goiás"', query)
        self.assertIn('"goiano"', query)
        self.assertIn('"goiana"', query)
        self.assertIn("AND", query)

    def test_search_is_logged_without_export_and_preserves_exact_query(self):
        query = (
            '(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência") '
            'AND ("Goiás" OR "goiano" OR "goiana")'
        )

        result = record_search(
            project_root=self.root,
            source="bdtd",
            query_id="goias-descriptors",
            query_literal=query,
            searched_fields="todos os campos",
            filters_json='{"publication_year": "2007:2026"}',
            source_reported_count=123,
            status="export_unavailable",
            notes="Fonte não ofereceu exportação para esta amostra.",
        )

        self.assertEqual(result.status, "export_unavailable")
        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["query_id"], "goias-descriptors")
        self.assertEqual(executions[0]["query_literal"], query)
        self.assertEqual(executions[0]["method"], "manual_search")
        self.assertEqual(executions[0]["source_reported_count"], "123")
        self.assertEqual(executions[0]["records_exported"], "")
        self.assertEqual(executions[0]["output_files"], "[]")
        self.assertEqual(executions[0]["status"], "export_unavailable")

    def test_open_data_download_resumes_partial_and_archives_completed_file(self):
        resource_url = "https://dadosabertos.capes.gov.br/dataset/catalogo-2024.csv"
        url_key = hashlib.sha256(resource_url.encode("utf-8")).hexdigest()[:16]
        staging = self.root / "dados/staging/catalogo-capes"
        staging.mkdir(parents=True)
        partial = staging / f"catalogo-2024__{url_key}.partial.csv"
        partial.write_bytes(b"abc")

        class FakeResponse:
            status = 206
            headers = {"Content-Range": "bytes 3-5/6", "Content-Length": "3"}

            def __init__(self):
                self.remaining = b"def"

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def geturl(self):
                return resource_url

            def getcode(self):
                return self.status

            def read(self, _size):
                chunk, self.remaining = self.remaining, b""
                return chunk

        seen_requests = []

        def fake_urlopen(request, timeout):
            seen_requests.append((request, timeout))
            return FakeResponse()

        with patch("scripts.capture_collection.urlopen", side_effect=fake_urlopen):
            result = download_open_data(
                project_root=self.root,
                resource_url=resource_url,
                query_id="catalogo-2024",
                dataset_id="catalogo-2021-2024",
                max_bytes=1024,
                expected_bytes=6,
                timeout=15,
            )

        raw_path = self.root / result.capture.raw_file
        self.assertEqual(raw_path.read_bytes(), b"abcdef")
        self.assertEqual(result.capture.bytes, 6)
        self.assertEqual(result.capture.status, "captured")
        self.assertEqual(seen_requests[0][0].get_header("Range"), "bytes=3-")
        self.assertEqual(seen_requests[0][1], 15)
        self.assertFalse(partial.exists())
        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(executions[0]["status"], "captured")
        self.assertEqual(executions[0]["method"], "open_data_download")

    def test_open_data_download_rejects_nonofficial_host_and_logs_failure(self):
        with self.assertRaisesRegex(ValueError, "only HTTPS resources"):
            download_open_data(
                project_root=self.root,
                resource_url="https://example.org/catalogo.csv",
                query_id="catalogo-2024",
                dataset_id="catalogo-2021-2024",
                max_bytes=1024,
            )

        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["status"], "download_incomplete")
        self.assertIn("only HTTPS resources", executions[0]["notes"])

    def test_interrupted_open_data_download_keeps_partial_for_resume(self):
        resource_url = "https://dadosabertos.capes.gov.br/dataset/interrupted.csv"

        class InterruptedResponse:
            status = 200
            headers = {"Content-Length": "6"}

            def __init__(self):
                self.read_count = 0

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def geturl(self):
                return resource_url

            def getcode(self):
                return self.status

            def read(self, _size):
                self.read_count += 1
                if self.read_count == 1:
                    return b"abc"
                raise OSError("connection interrupted")

        with patch(
            "scripts.capture_collection.urlopen", return_value=InterruptedResponse()
        ):
            with self.assertRaisesRegex(OSError, "connection interrupted"):
                download_open_data(
                    project_root=self.root,
                    resource_url=resource_url,
                    query_id="interrupted",
                    dataset_id="catalogo-2021-2024",
                    max_bytes=1024,
                    expected_bytes=6,
                )

        partials = list((self.root / "dados/staging/catalogo-capes").glob("*.partial.csv"))
        self.assertEqual(len(partials), 1)
        self.assertEqual(partials[0].read_bytes(), b"abc")
        executions = self.read_rows("dados/logs/execucoes.csv")
        self.assertEqual(executions[0]["status"], "download_incomplete")
        self.assertIn("resumable partial:", executions[0]["notes"])


if __name__ == "__main__":
    unittest.main()
