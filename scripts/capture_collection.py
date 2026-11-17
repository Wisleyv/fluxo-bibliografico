#!/usr/bin/env python3
"""Register official/manual exports as immutable raw collection files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse
from urllib.request import Request, urlopen


EXECUTION_FIELDS = [
    "source_run_id",
    "source",
    "query_id",
    "query_literal",
    "searched_fields",
    "filters_json",
    "method",
    "started_at",
    "completed_at",
    "source_reported_count",
    "records_exported",
    "records_imported",
    "output_files",
    "status",
    "notes",
]

FILE_FIELDS = [
    "raw_file",
    "original_filename",
    "format",
    "bytes",
    "sha256",
    "source",
    "source_run_id",
    "captured_at",
    "duplicate_of",
]

SOURCES = ("portal-capes", "bdtd", "scielo", "catalogo-capes", "google-scholar")
METHODS = ("assisted_export", "open_data_download", "manual_capture", "manual_search")
SUPPORTED_EXTENSIONS = {".bib", ".bibtex", ".csv", ".ris", ".xlsx", ".zip"}
CHUNK_SIZE = 1024 * 1024
QUERY_TEMPLATES = {
    "national": (
        "national-pibid",
        'PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"',
    ),
    "goias": (
        "goias-descriptors",
        '(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência") '
        'AND ("Goiás" OR "goiano" OR "goiana")',
    ),
}


@dataclass(frozen=True)
class CaptureResult:
    source_run_id: str
    raw_file: str
    sha256: str
    bytes: int
    status: str


@dataclass(frozen=True)
class SearchResult:
    source_run_id: str
    status: str


@dataclass(frozen=True)
class DownloadResult:
    capture: CaptureResult
    expected_bytes: int | None


def _append_csv(path: Path, fields: list[str], row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        if write_header:
            writer.writeheader()
        writer.writerow(row)
        stream.flush()
        os.fsync(stream.fileno())


def _read_known_hashes(path: Path) -> dict[tuple[str, str], str]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with path.open("r", encoding="utf-8", newline="") as stream:
        return {
            (row["source"], row["sha256"]): row["raw_file"]
            for row in csv.DictReader(stream)
            if row.get("source") and row.get("sha256") and row.get("raw_file")
        }


def _safe_query_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-_")
    if not cleaned:
        raise ValueError("query-id must contain at least one letter or number")
    return cleaned


def _hash_and_copy(source: Path, temporary_path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with source.open("rb") as input_stream, temporary_path.open("wb") as output_stream:
        while chunk := input_stream.read(CHUNK_SIZE):
            output_stream.write(chunk)
            digest.update(chunk)
            size += len(chunk)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    return digest.hexdigest(), size


def _execution_row(
    *,
    source_run_id: str,
    source: str,
    query_id: str,
    query_literal: str,
    searched_fields: str,
    filters_json: str,
    method: str,
    started_at: str,
    completed_at: str,
    source_reported_count: int | None,
    records_exported: int | None,
    output_files: list[str],
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "source_run_id": source_run_id,
        "source": source,
        "query_id": query_id,
        "query_literal": query_literal,
        "searched_fields": searched_fields,
        "filters_json": filters_json,
        "method": method,
        "started_at": started_at,
        "completed_at": completed_at,
        "source_reported_count": "" if source_reported_count is None else source_reported_count,
        "records_exported": "" if records_exported is None else records_exported,
        "records_imported": "",
        "output_files": json.dumps(output_files, ensure_ascii=False),
        "status": status,
        "notes": notes,
    }


def capture_file(
    *,
    project_root: Path,
    source: str,
    query_id: str,
    query_literal: str,
    input_file: Path,
    method: str,
    searched_fields: str = "",
    filters_json: str = "{}",
    source_reported_count: int | None = None,
    records_exported: int | None = None,
    original_filename: str | None = None,
) -> CaptureResult:
    started = datetime.now().astimezone()
    started_at = started.isoformat(timespec="seconds")
    source_run_id = str(uuid.uuid4())
    root = project_root.resolve()
    manifest_path = root / "dados" / "logs" / "execucoes.csv"
    inventory_path = root / "dados" / "logs" / "arquivos.csv"
    normalized_query_id = _safe_query_id(query_id)
    source_path = input_file.expanduser().resolve()
    temp_path: Path | None = None

    try:
        if source not in SOURCES:
            raise ValueError(f"unsupported source: {source}")
        if method not in METHODS:
            raise ValueError(f"unsupported method: {method}")
        if source == "google-scholar" and method != "manual_search":
            raise ValueError("Google Scholar is limited to manual_search; do not automate it")
        parsed_filters = json.loads(filters_json)
        if not isinstance(parsed_filters, dict):
            raise ValueError("filters-json must be a JSON object")
        if source_reported_count is not None and source_reported_count < 0:
            raise ValueError("reported-count cannot be negative")
        if records_exported is not None and records_exported < 0:
            raise ValueError("exported-count cannot be negative")
        if not source_path.is_file():
            raise FileNotFoundError(f"input file does not exist: {source_path}")
        extension = source_path.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"unsupported file extension {extension!r}; expected one of "
                f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        raw_directory = root / "dados" / "brutos" / source
        raw_directory.mkdir(parents=True, exist_ok=True)
        inventory = _read_known_hashes(inventory_path)
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".capture-", suffix=".tmp", dir=raw_directory, delete=False
        ) as temporary:
            temp_path = Path(temporary.name)

        source_stat_before = source_path.stat()
        checksum, size = _hash_and_copy(source_path, temp_path)
        source_stat_after = source_path.stat()
        if (
            source_stat_before.st_size != source_stat_after.st_size
            or source_stat_before.st_mtime_ns != source_stat_after.st_mtime_ns
            or size != source_stat_after.st_size
        ):
            raise OSError("input file changed while it was being captured")

        captured_at = datetime.now().astimezone()
        existing_raw_file = inventory.get((source, checksum))
        if existing_raw_file is not None:
            temp_path.unlink()
            temp_path = None
            status = "duplicate_skipped"
            raw_file = existing_raw_file
            notes = "Identical SHA-256 already registered; existing raw file retained."
        else:
            timestamp = captured_at.strftime("%Y%m%dT%H%M%S%f%z")
            stem = f"{source}__{normalized_query_id}__{timestamp}__{extension[1:].upper()}"
            destination = raw_directory / f"{stem}{extension}"
            suffix = 2
            while destination.exists():
                destination = raw_directory / f"{stem}__{suffix}{extension}"
                suffix += 1
            temp_path.replace(destination)
            temp_path = None
            raw_file = destination.relative_to(root).as_posix()
            _append_csv(
                inventory_path,
                FILE_FIELDS,
                {
                    "raw_file": raw_file,
                    "original_filename": original_filename or source_path.name,
                    "format": extension[1:].upper(),
                    "bytes": size,
                    "sha256": checksum,
                    "source": source,
                    "source_run_id": source_run_id,
                    "captured_at": captured_at.isoformat(timespec="seconds"),
                    "duplicate_of": "",
                },
            )
            status = "captured"
            notes = "Raw file copied without modification."

        completed_at = datetime.now().astimezone().isoformat(timespec="seconds")
        _append_csv(
            manifest_path,
            EXECUTION_FIELDS,
            _execution_row(
                source_run_id=source_run_id,
                source=source,
                query_id=normalized_query_id,
                query_literal=query_literal,
                searched_fields=searched_fields,
                filters_json=json.dumps(parsed_filters, ensure_ascii=False, sort_keys=True),
                method=method,
                started_at=started_at,
                completed_at=completed_at,
                source_reported_count=source_reported_count,
                records_exported=records_exported,
                output_files=[raw_file],
                status=status,
                notes=notes,
            ),
        )
        return CaptureResult(source_run_id, raw_file, checksum, size, status)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        completed_at = datetime.now().astimezone().isoformat(timespec="seconds")
        _append_csv(
            manifest_path,
            EXECUTION_FIELDS,
            _execution_row(
                source_run_id=source_run_id,
                source=source,
                query_id=query_id,
                query_literal=query_literal,
                searched_fields=searched_fields,
                filters_json=filters_json,
                method=method,
                started_at=started_at,
                completed_at=completed_at,
                source_reported_count=source_reported_count,
                records_exported=records_exported,
                output_files=[],
                status="failed",
                notes=f"{type(error).__name__}: {error}",
            ),
        )
        raise


def record_search(
    *,
    project_root: Path,
    source: str,
    query_id: str,
    query_literal: str,
    searched_fields: str = "",
    filters_json: str = "{}",
    source_reported_count: int | None = None,
    status: str = "search_completed",
    notes: str = "",
) -> SearchResult:
    started = datetime.now().astimezone()
    started_at = started.isoformat(timespec="seconds")
    source_run_id = str(uuid.uuid4())
    root = project_root.resolve()
    manifest_path = root / "dados" / "logs" / "execucoes.csv"
    normalized_query_id = query_id

    try:
        if source not in SOURCES:
            raise ValueError(f"unsupported source: {source}")
        if status not in ("search_completed", "export_unavailable"):
            raise ValueError("search status must be search_completed or export_unavailable")
        normalized_query_id = _safe_query_id(query_id)
        if source_reported_count is not None and source_reported_count < 0:
            raise ValueError("reported-count cannot be negative")
        parsed_filters = json.loads(filters_json)
        if not isinstance(parsed_filters, dict):
            raise ValueError("filters-json must be a JSON object")
        if not query_literal.strip():
            raise ValueError("query must not be empty")

        completed_at = datetime.now().astimezone().isoformat(timespec="seconds")
        _append_csv(
            manifest_path,
            EXECUTION_FIELDS,
            _execution_row(
                source_run_id=source_run_id,
                source=source,
                query_id=normalized_query_id,
                query_literal=query_literal,
                searched_fields=searched_fields,
                filters_json=json.dumps(parsed_filters, ensure_ascii=False, sort_keys=True),
                method="manual_search",
                started_at=started_at,
                completed_at=completed_at,
                source_reported_count=source_reported_count,
                records_exported=None,
                output_files=[],
                status=status,
                notes=notes,
            ),
        )
        return SearchResult(source_run_id, status)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        completed_at = datetime.now().astimezone().isoformat(timespec="seconds")
        _append_csv(
            manifest_path,
            EXECUTION_FIELDS,
            _execution_row(
                source_run_id=source_run_id,
                source=source,
                query_id=normalized_query_id,
                query_literal=query_literal,
                searched_fields=searched_fields,
                filters_json=filters_json,
                method="manual_search",
                started_at=started_at,
                completed_at=completed_at,
                source_reported_count=source_reported_count,
                records_exported=None,
                output_files=[],
                status="failed",
                notes=f"{type(error).__name__}: {error}",
            ),
        )
        raise


def download_open_data(
    *,
    project_root: Path,
    resource_url: str,
    query_id: str,
    dataset_id: str,
    max_bytes: int,
    expected_bytes: int | None = None,
    timeout: int = 60,
) -> DownloadResult:
    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    source_run_id = str(uuid.uuid4())
    root = project_root.resolve()
    manifest_path = root / "dados" / "logs" / "execucoes.csv"
    partial_path: Path | None = None

    try:
        normalized_query_id = _safe_query_id(query_id)
        parsed_url = urlparse(resource_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "dadosabertos.capes.gov.br"
            or parsed_url.username is not None
            or parsed_url.password is not None
        ):
            raise ValueError("only HTTPS resources hosted at dadosabertos.capes.gov.br are allowed")
        filename = Path(parsed_url.path).name
        extension = Path(filename).suffix.lower()
        if extension not in {".csv", ".xlsx"}:
            raise ValueError("official CAPES open-data resource must end in .csv or .xlsx")
        if not dataset_id.strip():
            raise ValueError("dataset-id must not be empty")
        if max_bytes <= 0:
            raise ValueError("max-bytes must be greater than zero")
        if expected_bytes is not None and (expected_bytes <= 0 or expected_bytes > max_bytes):
            raise ValueError("expected-bytes must be positive and no greater than max-bytes")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        staging_directory = root / "dados" / "staging" / "catalogo-capes"
        staging_directory.mkdir(parents=True, exist_ok=True)
        url_key = hashlib.sha256(resource_url.encode("utf-8")).hexdigest()[:16]
        partial_path = staging_directory / f"{normalized_query_id}__{url_key}.partial{extension}"
        offset = partial_path.stat().st_size if partial_path.exists() else 0
        if offset > max_bytes or (expected_bytes is not None and offset > expected_bytes):
            raise ValueError("existing partial download exceeds the configured size limit")

        remote_total: int | None = None
        if expected_bytes is None or offset != expected_bytes:
            headers = {"User-Agent": "PIBID-Bibliometric-Collection/1.0"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            request = Request(resource_url, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                response_url = urlparse(response.geturl())
                if (
                    response_url.scheme != "https"
                    or response_url.hostname != "dadosabertos.capes.gov.br"
                ):
                    raise ValueError("CAPES resource redirected outside dadosabertos.capes.gov.br")
                status_code = getattr(response, "status", response.getcode())
                response_headers = response.headers
                if offset and status_code == 206:
                    content_range = response_headers.get("Content-Range", "")
                    range_match = re.fullmatch(
                        rf"bytes {offset}-(\d+)/(\d+)", content_range
                    )
                    if range_match is None:
                        raise OSError("server returned an invalid Content-Range for resume")
                    range_end, remote_total = map(int, range_match.groups())
                    if range_end < offset or range_end >= remote_total:
                        raise OSError("server returned inconsistent Content-Range boundaries")
                    write_mode = "ab"
                    resumed_from = offset
                elif status_code == 200:
                    write_mode = "wb"
                    resumed_from = 0
                else:
                    raise OSError(f"unexpected HTTP status for CAPES resource: {status_code}")

                content_length_header = response_headers.get("Content-Length")
                response_length = (
                    int(content_length_header) if content_length_header is not None else None
                )
                if (
                    offset
                    and status_code == 206
                    and response_length is not None
                    and response_length != range_end - offset + 1
                ):
                    raise OSError("Content-Length does not match Content-Range")
                if response_length is not None and resumed_from + response_length > max_bytes:
                    raise ValueError("remote resource exceeds max-bytes")
                if expected_bytes is not None and response_length is not None:
                    if resumed_from + response_length != expected_bytes:
                        raise OSError("Content-Length does not match expected-bytes")

                received = 0
                with partial_path.open(write_mode) as destination:
                    while chunk := response.read(CHUNK_SIZE):
                        received += len(chunk)
                        if resumed_from + received > max_bytes:
                            raise ValueError("download exceeded max-bytes")
                        destination.write(chunk)
                    destination.flush()
                    os.fsync(destination.fileno())
                if response_length is not None and received != response_length:
                    raise OSError("download ended before the advertised Content-Length")

        final_size = partial_path.stat().st_size if partial_path.exists() else 0
        if expected_bytes is not None and final_size != expected_bytes:
            raise OSError(
                f"download is incomplete: expected {expected_bytes} bytes, received {final_size}"
            )
        if remote_total is not None and final_size != remote_total:
            raise OSError(
                f"download is incomplete: server reports {remote_total} bytes, received {final_size}"
            )
        if final_size > max_bytes:
            raise ValueError("download exceeds max-bytes")
    except (OSError, ValueError, TimeoutError) as error:
        completed_at = datetime.now().astimezone().isoformat(timespec="seconds")
        partial_note = (
            f"; resumable partial: {partial_path.relative_to(root).as_posix()}"
            if partial_path is not None and partial_path.exists()
            else ""
        )
        _append_csv(
            manifest_path,
            EXECUTION_FIELDS,
            _execution_row(
                source_run_id=source_run_id,
                source="catalogo-capes",
                query_id=query_id,
                query_literal=resource_url,
                searched_fields="official open-data resource",
                filters_json=json.dumps(
                    {
                        "dataset_id": dataset_id,
                        "expected_bytes": expected_bytes,
                        "max_bytes": max_bytes,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                method="open_data_download",
                started_at=started_at,
                completed_at=completed_at,
                source_reported_count=None,
                records_exported=None,
                output_files=[],
                status="download_incomplete",
                notes=f"{type(error).__name__}: {error}{partial_note}",
            ),
        )
        raise

    capture = capture_file(
        project_root=root,
        source="catalogo-capes",
        query_id=query_id,
        query_literal=resource_url,
        input_file=partial_path,
        method="open_data_download",
        searched_fields="official open-data resource",
        original_filename=filename,
        filters_json=json.dumps(
            {
                "dataset_id": dataset_id,
                "expected_bytes": expected_bytes,
                "max_bytes": max_bytes,
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )
    partial_path.unlink(missing_ok=True)
    return DownloadResult(capture, expected_bytes)


def _nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preserve and register an official/manual bibliographic export."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    register = subparsers.add_parser("register", help="copy an export to raw storage and log it")
    register.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    register.add_argument("--source", required=True, choices=SOURCES)
    register.add_argument("--query-id", required=True)
    register.add_argument("--query", required=True, help="exact query used at the source")
    register.add_argument("--file", required=True, type=Path)
    register.add_argument("--method", required=True, choices=METHODS)
    register.add_argument("--fields", default="")
    register.add_argument("--filters-json", default="{}")
    register.add_argument("--reported-count", type=_nonnegative_int)
    register.add_argument("--exported-count", type=_nonnegative_int)
    download = subparsers.add_parser(
        "download-capes-open-data",
        help="download an official CAPES open-data file with size limits and resume support",
    )
    download.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    download.add_argument("--url", required=True, help="HTTPS resource on dadosabertos.capes.gov.br")
    download.add_argument("--query-id", required=True)
    download.add_argument("--dataset-id", required=True)
    download.add_argument("--max-bytes", required=True, type=_nonnegative_int)
    download.add_argument("--expected-bytes", type=_nonnegative_int)
    download.add_argument("--timeout", type=_nonnegative_int, default=60)
    search = subparsers.add_parser(
        "record-search", help="log a manually executed search even when no export is available"
    )
    search.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    search.add_argument("--source", required=True, choices=SOURCES)
    search.add_argument("--query-id", required=True)
    search.add_argument("--query", required=True, help="exact query used at the source")
    search.add_argument("--fields", default="")
    search.add_argument("--filters-json", default="{}")
    search.add_argument("--reported-count", type=_nonnegative_int)
    search.add_argument(
        "--status",
        choices=("search_completed", "export_unavailable"),
        default="search_completed",
    )
    search.add_argument("--notes", default="")
    queries = subparsers.add_parser("queries", help="show approved national and Goiás query templates")
    queries.add_argument("--scope", choices=(*QUERY_TEMPLATES, "all"), default="all")
    return parser


def main(argv: list[str] | None = None, output: TextIO = sys.stdout) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "register":
        try:
            result = capture_file(
                project_root=args.root,
                source=args.source,
                query_id=args.query_id,
                query_literal=args.query,
                input_file=args.file,
                method=args.method,
                searched_fields=args.fields,
                filters_json=args.filters_json,
                source_reported_count=args.reported_count,
                records_exported=args.exported_count,
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Capture failed: {error}", file=sys.stderr)
            return 1
        print(
            f"{result.status}: {result.raw_file} "
            f"({result.bytes} bytes, sha256={result.sha256}, run={result.source_run_id})",
            file=output,
        )
        return 0
    if args.command == "download-capes-open-data":
        try:
            result = download_open_data(
                project_root=args.root,
                resource_url=args.url,
                query_id=args.query_id,
                dataset_id=args.dataset_id,
                max_bytes=args.max_bytes,
                expected_bytes=args.expected_bytes,
                timeout=args.timeout,
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"CAPES open-data download failed: {error}", file=sys.stderr)
            return 1
        capture = result.capture
        print(
            f"{capture.status}: {capture.raw_file} "
            f"({capture.bytes} bytes, sha256={capture.sha256}, run={capture.source_run_id})",
            file=output,
        )
        return 0
    if args.command == "record-search":
        try:
            result = record_search(
                project_root=args.root,
                source=args.source,
                query_id=args.query_id,
                query_literal=args.query,
                searched_fields=args.fields,
                filters_json=args.filters_json,
                source_reported_count=args.reported_count,
                status=args.status,
                notes=args.notes,
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Search registration failed: {error}", file=sys.stderr)
            return 1
        print(f"{result.status}: run={result.source_run_id}", file=output)
        return 0
    if args.command == "queries":
        scopes = QUERY_TEMPLATES if args.scope == "all" else {args.scope: QUERY_TEMPLATES[args.scope]}
        payload = [
            {"scope": scope, "query_id": query_id, "query": query}
            for scope, (query_id, query) in scopes.items()
        ]
        print(json.dumps(payload, ensure_ascii=True, indent=2), file=output)
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
