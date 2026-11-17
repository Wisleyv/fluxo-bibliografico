#!/usr/bin/env python3
"""Normalize registered bibliographic exports without modifying raw files."""

from __future__ import annotations

import argparse
import codecs
import csv
import io
import json
import re
import sys
import unicodedata
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, TextIO
from zipfile import ZipFile


NORMALIZED_FIELDS = [
    "record_id",
    "source",
    "source_record_id",
    "source_run_id",
    "raw_file",
    "document_type_original",
    "document_type_normalized",
    "title",
    "authors_json",
    "publication_year",
    "defense_year",
    "abstract",
    "keywords_json",
    "language",
    "institution_original",
    "institution_normalized",
    "author_affiliations_json",
    "program",
    "venue",
    "volume",
    "issue",
    "pages",
    "doi",
    "url",
    "collected_at",
    "source_metadata_json",
]

QUALITY_FIELDS = [
    "source",
    "raw_file",
    "source_run_id",
    "encoding",
    "records_normalized",
    "expected_records",
    "record_count_matches_expected",
    "missing_title_records",
    "missing_year_records",
    "invalid_year_records",
    "out_of_period_records",
    "missing_author_records",
    "missing_source_record_id_records",
    "c1_control_characters",
    "c1_control_records",
    "decode_replacement_characters",
    "decode_replacement_records",
    "missing_expected_fields_json",
    "unmapped_source_fields_json",
]

ISSUE_FIELDS = [
    "source",
    "source_run_id",
    "raw_file",
    "archive_member",
    "record_position",
    "record_id",
    "issue",
    "field",
    "raw_value",
]

INSTITUTION_FIELDS = [
    "institution_original",
    "sources_json",
    "occurrences",
    "institution_normalized",
    "status",
    "notes",
]

NORMALIZATION_LOG_FIELDS = [
    "normalization_run_id",
    "started_at",
    "completed_at",
    "status",
    "records_normalized",
    "input_files",
    "output_files",
    "notes",
]

PERIOD_START = 2007
PERIOD_END = 2026
RECORD_NAMESPACE = uuid.UUID("111a9f4d-98ec-4d33-b11a-b833cc232efb")

RIS_COMMON_TAGS = {
    "TY",
    "ID",
    "TI",
    "AU",
    "A1",
    "AD",
    "PY",
    "DA",
    "JO",
    "J2",
    "VL",
    "IS",
    "SP",
    "EP",
    "DO",
    "UR",
    "L1",
    "AB",
    "KW",
    "LA",
}

MISSING_MARKERS = {
    "",
    "nao informado pela instituicao",
    "nao informado",
    "not informed by the institution",
    "n/a",
    "na",
    "null",
    "none",
}


@dataclass(frozen=True)
class RawInput:
    source: str
    raw_file: str
    source_run_id: str
    captured_at: str
    expected_records: int | None
    path: Path


@dataclass
class FileQuality:
    source: str
    raw_file: str
    source_run_id: str
    encoding: str
    expected_records: int | None
    missing_expected_fields: list[str] = field(default_factory=list)
    unmapped_source_fields: list[str] = field(default_factory=list)
    records: int = 0
    missing_title: int = 0
    missing_year: int = 0
    invalid_year: int = 0
    out_of_period: int = 0
    missing_author: int = 0
    missing_source_id: int = 0
    c1_controls: int = 0
    c1_control_records: int = 0
    replacement_characters: int = 0
    replacement_records: int = 0


def _append_csv(path: Path, fields: list[str], row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        if write_header:
            writer.writeheader()
        writer.writerow(row)
        stream.flush()


def _read_inventory(root: Path) -> list[RawInput]:
    inventory_path = root / "dados" / "logs" / "arquivos.csv"
    if not inventory_path.is_file():
        raise FileNotFoundError(f"raw-file inventory not found: {inventory_path}")

    raw_inputs: list[RawInput] = []
    with inventory_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            raw_file = row.get("raw_file", "").strip()
            source = row.get("source", "").strip()
            source_run_id = row.get("source_run_id", "").strip()
            if not raw_file or not source or not source_run_id:
                raise ValueError(f"incomplete raw-file inventory row: {row!r}")
            path = root / Path(raw_file)
            if not path.is_file():
                raise FileNotFoundError(f"registered raw file is missing: {path}")
            raw_inputs.append(
                RawInput(
                    source=source,
                    raw_file=raw_file.replace("\\", "/"),
                    source_run_id=source_run_id,
                    captured_at=row.get("captured_at", "").strip(),
                    expected_records=None,
                    path=path,
                )
            )

    manifest_path = root / "dados" / "logs" / "execucoes.csv"
    manifest_counts: dict[str, set[int]] = {}
    manifest_by_run: dict[str, int] = {}
    with manifest_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            run_id = row.get("source_run_id", "").strip()
            count = row.get("records_exported", "").strip()
            if run_id and count.isdigit():
                parsed_count = int(count)
                manifest_by_run[run_id] = parsed_count
                output_files = json.loads(row.get("output_files", "[]") or "[]")
                if not isinstance(output_files, list):
                    raise ValueError(f"manifest output_files is not a list for run {run_id}")
                for output_file in output_files:
                    if isinstance(output_file, str):
                        normalized_path = output_file.replace("\\", "/")
                        manifest_counts.setdefault(normalized_path, set()).add(parsed_count)

    enriched: list[RawInput] = []
    for item in raw_inputs:
        counts = manifest_counts.get(item.raw_file, set())
        if len(counts) > 1:
            raise ValueError(
                f"conflicting exported counts for {item.raw_file}: {sorted(counts)}"
            )
        expected = next(iter(counts)) if counts else manifest_by_run.get(item.source_run_id)
        enriched.append(
            RawInput(
                source=item.source,
                raw_file=item.raw_file,
                source_run_id=item.source_run_id,
                captured_at=item.captured_at,
                expected_records=expected,
                path=item.path,
            )
        )
    return enriched


def _can_decode(path: Path, encoding: str) -> bool:
    decoder = codecs.getincrementaldecoder(encoding)(errors="strict")
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                decoder.decode(chunk)
            decoder.decode(b"", final=True)
        return True
    except UnicodeDecodeError:
        return False


def _detect_encoding(path: Path) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        if _can_decode(path, encoding):
            return encoding
    return "cp1252-replace"


def _encoding_errors(encoding: str) -> str:
    return "replace" if encoding.endswith("-replace") else "strict"


def _base_encoding(encoding: str) -> str:
    return encoding.removesuffix("-replace")


def _norm(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = value.strip()
    if _norm(cleaned) in MISSING_MARKERS:
        return ""
    return cleaned


def _json_array(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def _metadata_json(values: dict[str, object]) -> str:
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _parse_year(value: str) -> int | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    match = re.search(r"(?<!\d)(\d{4})(?!\d)", cleaned)
    if not match:
        return None
    year = int(match.group(1))
    return year if 1000 <= year <= 2999 else None


def _year_value(value: str) -> str:
    year = _parse_year(value)
    return str(year) if year is not None else ""


def _document_type(value: str, source: str) -> str:
    text = _norm(value)
    if not text:
        return "unknown"
    if any(token in text for token in ("article", "journal", "jour")):
        return "article"
    if any(token in text for token in ("master", "mestrado", "dissert")):
        return "dissertation"
    if any(token in text for token in ("doctoral", "doutor", "tese", "thes")):
        return "thesis"
    if "editorial" in text:
        return "other_academic"
    if "conference" in text or "proceedings" in text or "congresso" in text:
        return "conference_paper"
    if "chapter" in text or "capitulo" in text:
        return "book_chapter"
    if "book" in text or "livro" in text:
        return "book"
    if source in {"bdtd", "catalogo-capes"}:
        return "other_academic"
    return "unknown"


def _split_list(values: list[str], delimiter: str | None = None) -> list[str]:
    result: list[str] = []
    for value in values:
        if delimiter and delimiter in value:
            candidates = value.split(delimiter)
        else:
            candidates = [value]
        for candidate in candidates:
            cleaned = _clean(candidate)
            if cleaned:
                result.append(cleaned)
    return result


def _record_id(item: RawInput, position: int, source_record_id: str, member: str = "") -> str:
    key = "\x1f".join(
        (item.source, item.raw_file, member, str(position), source_record_id)
    )
    return str(uuid.uuid5(RECORD_NAMESPACE, key))


def _make_record(
    *,
    item: RawInput,
    position: int,
    values: dict[str, object],
    year_raw: str,
    year_field: str,
    member: str = "",
) -> dict[str, str]:
    source_record_id = _clean(str(values.get("source_record_id", "")))
    publication_year = _year_value(str(values.get("publication_year_raw", "")))
    defense_year = _year_value(str(values.get("defense_year_raw", "")))
    title = _clean(str(values.get("title", "")))
    document_type_original = _clean(str(values.get("document_type_original", "")))
    metadata = dict(values.get("source_metadata", {}))
    if member:
        metadata["__archive_member__"] = member

    record = {
        "record_id": _record_id(item, position, source_record_id, member),
        "source": item.source,
        "source_record_id": source_record_id,
        "source_run_id": item.source_run_id,
        "raw_file": item.raw_file,
        "document_type_original": document_type_original,
        "document_type_normalized": _document_type(document_type_original, item.source),
        "title": title,
        "authors_json": _json_array(list(values.get("authors", []))),
        "publication_year": publication_year,
        "defense_year": defense_year,
        "abstract": _clean(str(values.get("abstract", ""))),
        "keywords_json": _json_array(list(values.get("keywords", []))),
        "language": _clean(str(values.get("language", ""))),
        "institution_original": _clean(str(values.get("institution_original", ""))),
        "institution_normalized": "",
        "author_affiliations_json": _json_array(
            list(values.get("author_affiliations", []))
        ),
        "program": _clean(str(values.get("program", ""))),
        "venue": _clean(str(values.get("venue", ""))),
        "volume": _clean(str(values.get("volume", ""))),
        "issue": _clean(str(values.get("issue", ""))),
        "pages": _clean(str(values.get("pages", ""))),
        "doi": _clean(str(values.get("doi", ""))),
        "url": _clean(str(values.get("url", ""))),
        "collected_at": item.captured_at,
        "source_metadata_json": _metadata_json(metadata),
    }

    if not title:
        values["_quality_issues"].append(("missing_title", "title", ""))
    has_year = bool(publication_year or defense_year)
    if not has_year:
        issue = "invalid_year" if year_raw.strip() else "missing_year"
        values["_quality_issues"].append((issue, year_field, year_raw))
    else:
        reference_year = int(publication_year or defense_year)
        if not PERIOD_START <= reference_year <= PERIOD_END:
            values["_quality_issues"].append(
                ("out_of_period", year_field, str(reference_year))
            )
    if not record["authors_json"] or record["authors_json"] == "[]":
        values["_quality_issues"].append(("missing_author", "authors", ""))
    if not source_record_id:
        values["_quality_issues"].append(("missing_source_record_id", "source_record_id", ""))
    return record


def _parse_ris(path: Path) -> Iterator[tuple[dict[str, list[str]], list[str]]]:
    current: dict[str, list[str]] = {}
    parser_issues: list[str] = []
    last_tag = ""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for line in stream:
            line = line.rstrip("\r\n")
            if re.match(r"^ER\s{2}-", line):
                if current:
                    yield current, parser_issues
                current = {}
                parser_issues = []
                last_tag = ""
                continue
            match = re.match(r"^([A-Z0-9]{2})\s{2}-\s?(.*)$", line)
            if match:
                tag, value = match.groups()
                current.setdefault(tag, []).append(value)
                last_tag = tag
            elif line.strip() and current and last_tag:
                current[last_tag][-1] += " " + line.strip()
        if current:
            parser_issues.append("unterminated_ris_record")
            yield current, parser_issues


def _ris_record(
    tags: dict[str, list[str]]
) -> tuple[dict[str, object], str, str]:
    get = lambda tag: tags.get(tag, [])
    publication_raw = _clean((get("PY") or [""])[0])
    authors = _split_list(get("AU") or get("A1"))
    affiliations = _split_list(get("AD"))
    keywords = _split_list(get("KW"))
    abstract = "\n\n".join(value.strip() for value in get("AB") if value.strip())
    start_page = _clean((get("SP") or [""])[0])
    end_page = _clean((get("EP") or [""])[0])
    pages = start_page
    if end_page and end_page != start_page:
        pages = f"{start_page}-{end_page}" if start_page else end_page
    mapped = {
        "TY",
        "ID",
        "TI",
        "AU",
        "A1",
        "AD",
        "PY",
        "JO",
        "J2",
        "VL",
        "IS",
        "SP",
        "EP",
        "DO",
        "UR",
        "L1",
        "AB",
        "KW",
        "LA",
    }
    metadata = {tag: values for tag, values in tags.items() if tag not in mapped}
    values: dict[str, object] = {
        "source_record_id": (get("ID") or [""])[0],
        "document_type_original": (get("TY") or [""])[0],
        "title": (get("TI") or [""])[0],
        "authors": authors,
        "publication_year_raw": publication_raw,
        "defense_year_raw": "",
        "abstract": abstract,
        "keywords": keywords,
        "language": (get("LA") or [""])[0],
        "institution_original": "",
        "author_affiliations": affiliations,
        "program": "",
        "venue": (get("JO") or get("J2") or [""])[0],
        "volume": (get("VL") or [""])[0],
        "issue": (get("IS") or [""])[0],
        "pages": pages,
        "doi": (get("DO") or [""])[0],
        "url": (get("UR") or get("L1") or [""])[0],
        "source_metadata": metadata,
        "_quality_issues": [],
    }
    return values, publication_raw, "PY"


def _header_key(value: str) -> str:
    return _norm(value).replace("_", " ").strip()


def _find_value(row: dict[str, str | None], *names: str) -> str:
    normalized = {_header_key(key): value or "" for key, value in row.items() if key}
    for name in names:
        value = normalized.get(_header_key(name))
        if value is not None:
            return value
    return ""


def _source_metadata(
    row: dict[str, str | None], mapped_names: set[str], extra: list[str] | None = None
) -> dict[str, str]:
    mapped = {_header_key(name) for name in mapped_names}
    result = {
        key: value
        for key, value in row.items()
        if key and _header_key(key) not in mapped and value not in (None, "")
    }
    if extra:
        result["__extra_csv_values__"] = json.dumps(extra, ensure_ascii=False)
    return result


def _csv_record(
    row: dict[str, str | None],
    item: RawInput,
    position: int,
    extra: list[str] | None = None,
    member: str = "",
) -> tuple[dict[str, object], str, str]:
    if item.source == "bdtd":
        author = _find_value(row, "Autor(a)")
        subjects = _split_list(
            [
                _find_value(row, "Assuntos em português"),
                _find_value(row, "Assuntos em inglês"),
            ],
            "||",
        )
        abstracts = [
            _clean(_find_value(row, "Resumo em Português")),
            _clean(_find_value(row, "Resumo")),
            _clean(_find_value(row, "Resumo em Inglês")),
        ]
        abstract = "\n\n".join(dict.fromkeys(value for value in abstracts if value))
        year_raw = _find_value(row, "Ano de defesa")
        mapped = {
            "Autor(a)",
            "Título",
            "Ano de defesa",
            "Instituição de defesa",
            "Sigla da instituição de defesa",
            "Programa de Pós-Graduação da instituição de defesa",
            "Tipo de documento",
            "Assuntos em português",
            "Assuntos em inglês",
            "Idioma",
            "Resumo",
            "Resumo em Português",
            "Resumo em Inglês",
            "Link de acesso",
            "Identificador persistente ARK",
        }
        source_id = _find_value(row, "Identificador persistente ARK")
        values: dict[str, object] = {
            "source_record_id": source_id,
            "document_type_original": _find_value(row, "Tipo de documento"),
            "title": _find_value(row, "Título"),
            "authors": _split_list([author], "||"),
            "publication_year_raw": "",
            "defense_year_raw": year_raw,
            "abstract": abstract,
            "keywords": subjects,
            "language": _find_value(row, "Idioma"),
            "institution_original": _find_value(row, "Instituição de defesa"),
            "author_affiliations": [],
            "program": _find_value(
                row, "Programa de Pós-Graduação da instituição de defesa"
            ),
            "venue": "",
            "volume": "",
            "issue": "",
            "pages": "",
            "doi": "",
            "url": _find_value(row, "Link de acesso"),
            "source_metadata": _source_metadata(row, mapped, extra),
            "_quality_issues": [],
        }
        return values, year_raw, "Ano de defesa"

    if item.source == "catalogo-capes":
        year_raw = _find_value(row, "DT_TITULACAO")
        keyword_values = [
            _find_value(row, "DS_PALAVRA_CHAVE"),
            _find_value(row, "DS_KEYWORD"),
        ]
        keywords = _split_list(keyword_values, ";")
        mapped = {
            "ID_PRODUCAO_INTELECTUAL",
            "NM_SUBTIPO_PRODUCAO",
            "NM_PRODUCAO",
            "DS_PALAVRA_CHAVE",
            "DS_KEYWORD",
            "DS_RESUMO",
            "DT_TITULACAO",
            "NM_ENTIDADE_ENSINO",
            "NM_PROGRAMA",
            "NM_DISCENTE",
            "NM_IDIOMA",
            "DS_URL_TEXTO_COMPLETO",
        }
        values = {
            "source_record_id": _find_value(row, "ID_PRODUCAO_INTELECTUAL"),
            "document_type_original": _find_value(row, "NM_SUBTIPO_PRODUCAO"),
            "title": _find_value(row, "NM_PRODUCAO"),
            "authors": _split_list([_find_value(row, "NM_DISCENTE")]),
            "publication_year_raw": "",
            "defense_year_raw": year_raw,
            "abstract": _find_value(row, "DS_RESUMO"),
            "keywords": keywords,
            "language": _find_value(row, "NM_IDIOMA"),
            "institution_original": _find_value(row, "NM_ENTIDADE_ENSINO"),
            "author_affiliations": [],
            "program": _find_value(row, "NM_PROGRAMA"),
            "venue": "",
            "volume": _find_value(row, "NR_VOLUME"),
            "issue": "",
            "pages": _find_value(row, "NR_PAGINAS"),
            "doi": "",
            "url": _find_value(row, "DS_URL_TEXTO_COMPLETO"),
            "source_metadata": _source_metadata(row, mapped, extra),
            "_quality_issues": [],
        }
        return values, year_raw, "DT_TITULACAO"

    raise ValueError(f"CSV source does not have a supported mapping: {item.source}")


def _csv_delimiter(item: RawInput) -> str:
    return ";" if item.source == "catalogo-capes" else ","


def _expected_csv_fields(source: str) -> tuple[set[str], set[str]]:
    if source == "bdtd":
        return {"titulo", "ano de defesa"}, {
            "Autor(a)",
            "Título",
            "Ano de defesa",
            "Instituição de defesa",
            "Sigla da instituição de defesa",
            "Programa de Pós-Graduação da instituição de defesa",
            "Tipo de documento",
            "Assuntos em português",
            "Assuntos em inglês",
            "Idioma",
            "Resumo",
            "Resumo em Português",
            "Resumo em Inglês",
            "Link de acesso",
            "Identificador persistente ARK",
        }
    return {"nm producao", "dt titulacao"}, {
        "ID_PRODUCAO_INTELECTUAL",
        "NM_SUBTIPO_PRODUCAO",
        "NM_PRODUCAO",
        "DS_PALAVRA_CHAVE",
        "DS_KEYWORD",
        "DS_RESUMO",
        "DT_TITULACAO",
        "NM_ENTIDADE_ENSINO",
        "NM_PROGRAMA",
        "NM_DISCENTE",
        "NM_IDIOMA",
        "DS_URL_TEXTO_COMPLETO",
    }


def _input_stream(item: RawInput, member: str = "") -> tuple[TextIO, str, object | None]:
    if member:
        archive = ZipFile(item.path)
        binary_stream = archive.open(member)
        data = binary_stream.read()
        binary_stream.close()
        try:
            text = data.decode("utf-8-sig")
            encoding = "utf-8-sig"
        except UnicodeDecodeError:
            try:
                text = data.decode("cp1252")
                encoding = "cp1252"
            except UnicodeDecodeError:
                text = data.decode("cp1252", errors="replace")
                encoding = "cp1252-replace"
        return io.StringIO(text, newline=""), encoding, archive
    encoding = _detect_encoding(item.path)
    return (
        item.path.open(
            encoding=_base_encoding(encoding), errors=_encoding_errors(encoding), newline=""
        ),
        encoding,
        None,
    )


def _iter_csv_members(item: RawInput) -> Iterator[tuple[str, str]]:
    if item.path.suffix.lower() != ".zip":
        yield "", _detect_encoding(item.path)
        return
    with ZipFile(item.path) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if not members:
        raise ValueError(f"ZIP has no CSV member: {item.raw_file}")
    for member in members:
        with ZipFile(item.path) as archive:
            data = archive.read(member)
        try:
            data.decode("utf-8-sig")
            encoding = "utf-8-sig"
        except UnicodeDecodeError:
            try:
                data.decode("cp1252")
                encoding = "cp1252"
            except UnicodeDecodeError:
                encoding = "cp1252-replace"
        yield member, encoding


def _update_quality(
    record: dict[str, str],
    values: dict[str, object],
    quality: FileQuality,
    issue_writer: csv.DictWriter,
    item: RawInput,
    member: str,
    position: int,
    record_id: str,
    parser_issues: list[str] | None = None,
) -> None:
    quality.records += 1
    year_field = ""
    if record["publication_year"]:
        year_field = "publication_year"
    elif record["defense_year"]:
        year_field = "defense_year"
    elif item.source in {"bdtd", "catalogo-capes"}:
        year_field = "defense_year"
    else:
        year_field = "publication_year"

    issue_rows = list(values.get("_quality_issues", []))
    if parser_issues:
        issue_rows.extend((issue, "RIS", "") for issue in parser_issues)
    for issue, field_name, raw_value in issue_rows:
        if issue == "missing_title":
            quality.missing_title += 1
        elif issue in {"missing_year", "invalid_year"}:
            if issue == "missing_year":
                quality.missing_year += 1
            else:
                quality.invalid_year += 1
        elif issue == "out_of_period":
            quality.out_of_period += 1
        elif issue == "missing_author":
            quality.missing_author += 1
        elif issue == "missing_source_record_id":
            quality.missing_source_id += 1
        elif issue == "c1_control_character":
            quality.c1_control_records += 1
        elif issue == "decode_replacement_character":
            quality.replacement_records += 1
        issue_writer.writerow(
            {
                "source": item.source,
                "source_run_id": item.source_run_id,
                "raw_file": item.raw_file,
                "archive_member": member,
                "record_position": position,
                "record_id": record_id,
                "issue": issue,
                "field": field_name or year_field,
                "raw_value": raw_value,
            }
        )


def _character_diagnostics(value: object) -> tuple[dict[str, int], dict[str, int]]:
    if isinstance(value, dict):
        c1_counts: Counter[str] = Counter()
        replacement_counts: Counter[str] = Counter()
        for key, item in value.items():
            key_c1, key_replacements = _character_diagnostics(key)
            item_c1, item_replacements = _character_diagnostics(item)
            c1_counts.update(key_c1)
            c1_counts.update(item_c1)
            replacement_counts.update(key_replacements)
            replacement_counts.update(item_replacements)
        return dict(c1_counts), dict(replacement_counts)
    if isinstance(value, list):
        c1_counts = Counter()
        replacement_counts = Counter()
        for item in value:
            item_c1, item_replacements = _character_diagnostics(item)
            c1_counts.update(item_c1)
            replacement_counts.update(item_replacements)
        return dict(c1_counts), dict(replacement_counts)
    if isinstance(value, str):
        c1_counts = Counter()
        replacement_counts = Counter()
        for char in value:
            if 0x80 <= ord(char) <= 0x9F:
                c1_counts[f"U+{ord(char):04X}"] += 1
            elif char == "\ufffd":
                replacement_counts["U+FFFD"] += 1
        return dict(c1_counts), dict(replacement_counts)
    return {}, {}


def _write_record(
    record_writer: csv.DictWriter,
    issue_writer: csv.DictWriter,
    record: dict[str, str],
    values: dict[str, object],
    quality: FileQuality,
    item: RawInput,
    member: str,
    position: int,
    institution_counts: Counter[tuple[str, str]],
    parser_issues: list[str] | None = None,
) -> None:
    c1_counts, replacement_counts = _character_diagnostics(values)
    if c1_counts:
        values["_quality_issues"].append(
            ("c1_control_character", "decoded_source_values", json.dumps(c1_counts))
        )
    if replacement_counts:
        values["_quality_issues"].append(
            (
                "decode_replacement_character",
                "decoded_source_values",
                json.dumps(replacement_counts),
            )
        )
    record_writer.writerow(record)
    if record["institution_original"]:
        institution_counts[(item.source, record["institution_original"])] += 1
    _update_quality(
        record,
        values,
        quality,
        issue_writer,
        item,
        member,
        position,
        record["record_id"],
        parser_issues,
    )
    quality.c1_controls += sum(c1_counts.values())
    quality.replacement_characters += sum(replacement_counts.values())


def _process_ris(
    item: RawInput,
    record_writer: csv.DictWriter,
    issue_writer: csv.DictWriter,
    institution_counts: Counter[tuple[str, str]],
) -> FileQuality:
    quality = FileQuality(
        item.source, item.raw_file, item.source_run_id, "utf-8-sig/UTF-8", item.expected_records
    )
    for position, (tags, parser_issues) in enumerate(_parse_ris(item.path), start=1):
        values, year_raw, year_field = _ris_record(tags)
        record = _make_record(
            item=item,
            position=position,
            values=values,
            year_raw=year_raw,
            year_field=year_field,
        )
        _write_record(
            record_writer,
            issue_writer,
            record,
            values,
            quality,
            item,
            "",
            position,
            institution_counts,
            parser_issues,
        )
    return quality


def _process_csv(
    item: RawInput,
    member: str,
    encoding: str,
    record_writer: csv.DictWriter,
    issue_writer: csv.DictWriter,
    institution_counts: Counter[tuple[str, str]],
) -> FileQuality:
    quality = FileQuality(
        item.source, item.raw_file, item.source_run_id, encoding, item.expected_records
    )
    stream: TextIO
    archive: object | None = None
    if member:
        stream, actual_encoding, archive = _input_stream(item, member)
        quality.encoding = actual_encoding
    else:
        stream = item.path.open(
            encoding=_base_encoding(encoding),
            errors=_encoding_errors(encoding),
            newline="",
        )
    try:
        reader = csv.DictReader(stream, delimiter=_csv_delimiter(item), strict=True)
        headers = reader.fieldnames or []
        expected, mapped_headers = _expected_csv_fields(item.source)
        header_keys = {_header_key(header) for header in headers}
        quality.missing_expected_fields = sorted(expected - header_keys)
        quality.unmapped_source_fields = sorted(
            header for header in headers if _header_key(header) not in {
                _header_key(mapped) for mapped in mapped_headers
            }
        )
        position = 0
        for row in reader:
            if row is None:
                continue
            position += 1
            extra = row.pop(None, None)
            values, year_raw, year_field = _csv_record(
                row,
                item,
                position,
                extra if isinstance(extra, list) else None,
                member,
            )
            record = _make_record(
                item=item,
                position=position,
                values=values,
                year_raw=year_raw,
                year_field=year_field,
                member=member,
            )
            _write_record(
                record_writer,
                issue_writer,
                record,
                values,
                quality,
                item,
                member,
                position,
                institution_counts,
            )
    finally:
        stream.close()
        if archive is not None:
            archive.close()
    return quality


def _quality_row(quality: FileQuality) -> dict[str, object]:
    expected_match = (
        ""
        if quality.expected_records is None
        else str(quality.expected_records == quality.records).lower()
    )
    return {
        "source": quality.source,
        "raw_file": quality.raw_file,
        "source_run_id": quality.source_run_id,
        "encoding": quality.encoding,
        "records_normalized": quality.records,
        "expected_records": (
            "" if quality.expected_records is None else quality.expected_records
        ),
        "record_count_matches_expected": expected_match,
        "missing_title_records": quality.missing_title,
        "missing_year_records": quality.missing_year,
        "invalid_year_records": quality.invalid_year,
        "out_of_period_records": quality.out_of_period,
        "missing_author_records": quality.missing_author,
        "missing_source_record_id_records": quality.missing_source_id,
        "c1_control_characters": quality.c1_controls,
        "c1_control_records": quality.c1_control_records,
        "decode_replacement_characters": quality.replacement_characters,
        "decode_replacement_records": quality.replacement_records,
        "missing_expected_fields_json": _metadata_json(
            {"fields": quality.missing_expected_fields}
        ),
        "unmapped_source_fields_json": _metadata_json(
            {"fields": quality.unmapped_source_fields}
        ),
    }


def normalize_project(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    started = datetime.now().astimezone()
    run_id = str(uuid.uuid4())
    started_at = started.isoformat(timespec="seconds")
    normalized_dir = root / "dados" / "normalizados"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    suffix = started.strftime("%Y%m%dT%H%M%S%z") + "__" + run_id[:8]
    outputs = {
        "records": normalized_dir / f"registros_normalizados__{suffix}.csv",
        "quality": normalized_dir / f"relatorio_qualidade__{suffix}.csv",
        "issues": normalized_dir / f"inconsistencias__{suffix}.csv",
        "institutions": normalized_dir / f"mapeamento_instituicoes__{suffix}.csv",
    }
    temporary = {key: path.with_suffix(path.suffix + ".tmp") for key, path in outputs.items()}
    input_files: list[str] = []
    total_records = 0
    status = "failed"
    notes = ""
    try:
        items = _read_inventory(root)
        if not items:
            raise ValueError("raw-file inventory has no registered files")
        input_files = [item.raw_file for item in items]
        qualities: list[FileQuality] = []
        institution_counts: Counter[tuple[str, str]] = Counter()
        with (
            temporary["records"].open("w", encoding="utf-8", newline="") as records_stream,
            temporary["quality"].open("w", encoding="utf-8", newline="") as quality_stream,
            temporary["issues"].open("w", encoding="utf-8", newline="") as issues_stream,
            temporary["institutions"].open(
                "w", encoding="utf-8", newline=""
            ) as institutions_stream,
        ):
            record_writer = csv.DictWriter(
                records_stream, fieldnames=NORMALIZED_FIELDS, extrasaction="raise"
            )
            quality_writer = csv.DictWriter(
                quality_stream, fieldnames=QUALITY_FIELDS, extrasaction="raise"
            )
            issue_writer = csv.DictWriter(
                issues_stream, fieldnames=ISSUE_FIELDS, extrasaction="raise"
            )
            institution_writer = csv.DictWriter(
                institutions_stream, fieldnames=INSTITUTION_FIELDS, extrasaction="raise"
            )
            record_writer.writeheader()
            quality_writer.writeheader()
            issue_writer.writeheader()
            institution_writer.writeheader()

            for item in items:
                suffix_ext = item.path.suffix.lower()
                if suffix_ext == ".ris":
                    quality = _process_ris(
                        item, record_writer, issue_writer, institution_counts
                    )
                    qualities.append(quality)
                elif suffix_ext == ".csv":
                    quality = _process_csv(
                        item,
                        "",
                        _detect_encoding(item.path),
                        record_writer,
                        issue_writer,
                        institution_counts,
                    )
                    qualities.append(quality)
                elif suffix_ext == ".zip":
                    for member, encoding in _iter_csv_members(item):
                        quality = _process_csv(
                            item,
                            member,
                            encoding,
                            record_writer,
                            issue_writer,
                            institution_counts,
                        )
                        qualities.append(quality)
                else:
                    raise ValueError(f"unsupported registered file type: {item.raw_file}")

            for quality in qualities:
                quality_writer.writerow(_quality_row(quality))
                total_records += quality.records
            grouped_institutions: dict[str, Counter[str]] = {}
            for (source, institution), count in institution_counts.items():
                grouped_institutions.setdefault(institution, Counter())[source] += count
            for institution in sorted(grouped_institutions, key=str.casefold):
                source_counts = grouped_institutions[institution]
                institution_writer.writerow(
                    {
                        "institution_original": institution,
                        "sources_json": json.dumps(
                            dict(sorted(source_counts.items())), ensure_ascii=False
                        ),
                        "occurrences": sum(source_counts.values()),
                        "institution_normalized": "",
                        "status": "pending",
                        "notes": "",
                    }
                )
        for key, path in temporary.items():
            path.replace(outputs[key])
        status = "completed"
        notes = (
            f"Streaming normalization; period check {PERIOD_START}-{PERIOD_END}; "
            "raw files were read only."
        )
        return {
            "normalization_run_id": run_id,
            "records_normalized": total_records,
            "input_files": input_files,
            "output_files": [path.relative_to(root).as_posix() for path in outputs.values()],
            "paths": outputs,
        }
    finally:
        for path in temporary.values():
            path.unlink(missing_ok=True)
        _append_csv(
            root / "dados" / "logs" / "normalizacoes.csv",
            NORMALIZATION_LOG_FIELDS,
            {
                "normalization_run_id": run_id,
                "started_at": started_at,
                "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "status": status,
                "records_normalized": total_records,
                "input_files": json.dumps(input_files, ensure_ascii=False),
                "output_files": json.dumps(
                    [path.relative_to(root).as_posix() for path in outputs.values()]
                    if status == "completed"
                    else [],
                    ensure_ascii=False,
                ),
                "notes": notes,
            },
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize registered collection exports and report data quality."
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser


def main(argv: list[str] | None = None, output: TextIO = sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = normalize_project(args.root)
    except (OSError, ValueError, UnicodeError, csv.Error) as error:
        print(f"Normalization failed: {error}", file=sys.stderr)
        return 1
    print(
        f"completed: {result['records_normalized']} records; "
        + "; ".join(result["output_files"]),
        file=output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
