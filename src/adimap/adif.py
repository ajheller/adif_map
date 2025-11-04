from __future__ import annotations

import re

_EOR_RE = re.compile(r"<eor>", re.IGNORECASE)


def parse_adif(content: str) -> list[dict[str, str]]:
    """Parse ADIF content into a list of dicts (field names uppercased)."""
    records: list[dict[str, str]] = []

    header_end = re.search(r"<eoh>", content, flags=re.IGNORECASE)
    data = content[header_end.end() :] if header_end else content

    raw_recs = re.split(_EOR_RE, data)
    field_pat = re.compile(r"<([A-Za-z0-9_]+):(\d+)(?::[^>]*)?>([^<]*)", re.DOTALL)

    for raw in raw_recs:
        raw = raw.strip()
        if not raw:
            continue

        entry: dict[str, str] = {}
        for match in field_pat.finditer(raw):
            name = match.group(1).upper()
            length = int(match.group(2))
            value = match.group(3)[:length]
            entry[name] = value.strip()

        if entry:
            records.append(entry)

    return records
