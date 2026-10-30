"""Build portable, collision-free names for batch audio exports."""

from __future__ import annotations

import re
import unicodedata

from schemas.export_naming import (
    DEFAULT_EXPORT_NAME_FIELDS,
    ExportNameRecord,
    ExportNamingOptions,
)


_UNSAFE_FILENAME_CHARS = re.compile(r"[^\w.-]+", flags=re.UNICODE)


def _safe_component(value: object, *, case_insensitive: bool) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = _UNSAFE_FILENAME_CHARS.sub("-", text).strip("-._") or "untitled"
    return text.casefold() if case_insensitive else text


def build_export_names(
    records: list[ExportNameRecord],
    options: ExportNamingOptions | None = None,
    *,
    audio_format: str = "wav",
) -> list[str]:
    """Return filenames in input order, suffixing collisions stably."""

    if options is None:
        options = ExportNamingOptions(fields=list(DEFAULT_EXPORT_NAME_FIELDS))

    # An explicitly supplied options object is treated as authoritative.
    fields = options.fields or []
    separator = options.separator
    seen: dict[str, int] = {}
    filenames: list[str] = []

    for record in records:
        components = [
            _safe_component(
                getattr(record, field),
                case_insensitive=options.case_insensitive,
            )
            for field in fields
        ]
        stem = separator.join(components) or "export"
        collision_key = stem.casefold()
        occurrence = seen.get(collision_key, 0) + 1
        seen[collision_key] = occurrence
        if occurrence > 1:
            stem = f"{stem}{separator}{occurrence}"
        filenames.append(f"{stem}.{audio_format}")

    return filenames
