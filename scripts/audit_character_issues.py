#!/usr/bin/env python3
"""Locate flagged characters in original CSV fields without changing the sources."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

try:
    from scripts.normalize_collection import _clean, _find_value, _read_inventory, _record_id
except ModuleNotFoundError as error:
    if error.name != "scripts":
        raise
    from normalize_collection import _clean, _find_value, _read_inventory, _record_id


FIELDS = [
    "normalization_run_id",
    "record_id",
    "source",
    "source_run_id",
    "raw_file",
    "raw_sha256",
    "record_position",
    "issue",
    "source_field",
    "character_position",
    "original_code",
    "context",
    "review_status",
    "review_decision",
    "review_note",
]
UNDEFINED_CP1252 = {0x81, 0x8D, 0x8F, 0x90, 0x9D}
SUPPORTED = {
    ("bdtd", "c1_control_character"),
    ("catalogo-capes", "decode_replacement_character"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _context(value: str, position: int, issue: str) -> str:
    start = max(position - 45, 0)
    end = min(position + 46, len(value))
    before, after = value[start:position], value[position + 1 : end]
    if issue == "decode_replacement_character":
        before = before.encode("latin-1").decode("cp1252", errors="replace")
        after = after.encode("latin-1").decode("cp1252", errors="replace")
        marker = f"[byte 0x{ord(value[position]):02X}]"
    else:
        before = "".join(
            f"[U+{ord(char):04X}]" if 0x80 <= ord(char) <= 0x9F else char
            for char in before
        )
        after = "".join(
            f"[U+{ord(char):04X}]" if 0x80 <= ord(char) <= 0x9F else char
            for char in after
        )
        marker = f"[U+{ord(value[position]):04X}]"
    return (before + marker + after).replace("\r", " ").replace("\n", " ")


def audit(root: Path, run_id: str) -> tuple[list[dict[str, str]], Path]:
    root = root.resolve()
    log_path = root / "dados" / "logs" / "normalizacoes.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        runs = [row for row in csv.DictReader(stream) if row["normalization_run_id"] == run_id]
    if len(runs) != 1 or runs[0]["status"] != "completed":
        raise ValueError(f"normalization run is not uniquely completed: {run_id}")
    output_paths = json.loads(runs[0]["output_files"])
    issue_paths = [p for p in output_paths if Path(p).name.startswith("inconsistencias__")]
    if len(issue_paths) != 1:
        raise ValueError("normalization run must identify exactly one issue report")
    issue_path = root / issue_paths[0]
    selected: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    with issue_path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["source"], row["issue"])
            if row["issue"] not in {"c1_control_character", "decode_replacement_character"}:
                continue
            if key not in SUPPORTED or row["archive_member"]:
                raise ValueError(f"unsupported character issue: {key}")
            position = int(row["record_position"])
            if position < 1 or position in selected[row["raw_file"]]:
                raise ValueError(f"invalid or duplicate issue position: {row['raw_file']} {position}")
            selected[row["raw_file"]][position] = row
    if not selected:
        raise ValueError("no character issues found in normalization report")

    inventory = {item.raw_file: item for item in _read_inventory(root)}
    with (root / "dados" / "logs" / "arquivos.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        hashes = {row["raw_file"]: row["sha256"] for row in csv.DictReader(stream)}

    occurrences: list[dict[str, str]] = []
    for raw_file, requested in selected.items():
        if raw_file not in inventory or raw_file not in hashes:
            raise ValueError(f"issue refers to unregistered file: {raw_file}")
        item = inventory[raw_file]
        digest = _sha256(item.path)
        if digest != hashes[raw_file]:
            raise ValueError(f"raw-file checksum mismatch: {raw_file}")
        encoding = "utf-8-sig" if item.source == "bdtd" else "latin-1"
        delimiter = "," if item.source == "bdtd" else ";"
        found: set[int] = set()
        with item.path.open(encoding=encoding, newline="") as stream:
            reader = csv.DictReader(stream, delimiter=delimiter, strict=True)
            for position, row in enumerate(reader, 1):
                if position not in requested:
                    continue
                issue = requested[position]
                if issue["source"] != item.source or issue["source_run_id"] != item.source_run_id:
                    raise ValueError(f"issue source does not match inventory: {raw_file} {position}")
                id_field = (
                    "Identificador persistente ARK"
                    if item.source == "bdtd"
                    else "ID_PRODUCAO_INTELECTUAL"
                )
                source_id = _clean(_find_value(row, id_field))
                if _record_id(item, position, source_id) != issue["record_id"]:
                    raise ValueError(f"record identifier mismatch: {raw_file} {position}")
                observed: Counter[str] = Counter()
                for field_name, value in row.items():
                    if field_name is None or value is None:
                        raise ValueError(f"malformed CSV record: {raw_file} {position}")
                    for offset, char in enumerate(value):
                        code = ord(char)
                        is_match = (
                            0x80 <= code <= 0x9F
                            if issue["issue"] == "c1_control_character"
                            else code in UNDEFINED_CP1252
                        )
                        if not is_match:
                            continue
                        report_code = (
                            f"U+{code:04X}"
                            if issue["issue"] == "c1_control_character"
                            else "U+FFFD"
                        )
                        observed[report_code] += 1
                        occurrences.append(
                            {
                                "normalization_run_id": run_id,
                                "record_id": issue["record_id"],
                                "source": item.source,
                                "source_run_id": item.source_run_id,
                                "raw_file": raw_file,
                                "raw_sha256": digest,
                                "record_position": str(position),
                                "issue": issue["issue"],
                                "source_field": field_name,
                                "character_position": str(offset + 1),
                                "original_code": (
                                    f"U+{code:04X}"
                                    if item.source == "bdtd"
                                    else f"0x{code:02X}"
                                ),
                                "context": _context(value, offset, issue["issue"]),
                                "review_status": "pending",
                                "review_decision": "",
                                "review_note": "",
                            }
                        )
                expected = json.loads(issue["raw_value"])
                if dict(observed) != expected:
                    raise ValueError(
                        f"character count mismatch in {raw_file} at record {position}: "
                        f"expected {expected}, found {dict(observed)}"
                    )
                found.add(position)
                if len(found) == len(requested):
                    break
        missing = set(requested) - found
        if missing:
            raise ValueError(f"records not found in {raw_file}: {sorted(missing)}")
    return occurrences, issue_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-id", required=True, help="completed normalization run UUID")
    args = parser.parse_args(argv)
    path: Path | None = None
    created = False
    try:
        rows, issue_path = audit(args.root, args.run_id)
        directory = args.root.resolve() / "dados" / "triagem"
        directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f%z")
        path = directory / f"auditoria_caracteres__{timestamp}__{uuid.uuid4().hex[:8]}.csv"
        with path.open("x", encoding="utf-8", newline="") as stream:
            created = True
            writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, ValueError, UnicodeError, csv.Error, KeyError) as error:
        if created and path is not None:
            path.unlink(missing_ok=True)
        print(f"Character audit failed: {error}", file=sys.stderr)
        return 1
    print(f"created: {path} ({len(rows)} occurrences; issues: {issue_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
