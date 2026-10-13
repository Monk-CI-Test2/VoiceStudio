"""Request and option models for deterministic batch-export filenames."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


EXPORT_NAME_FIELDS = ("project", "language", "voice", "take")

# Keep this definition in the schema layer so API, CLI, and service callers
# share one canonical default.
DEFAULT_EXPORT_NAME_FIELDS = ("project", "voice", "take")


class ExportNamingOptions(BaseModel):
    """Controls which metadata fields appear in an exported audio filename."""

    fields: list[str] | None = None
    separator: Literal["-", "_"] = "-"
    case_insensitive: bool = False

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, fields: list[str] | None) -> list[str] | None:
        if fields is None:
            return None
        unknown = [field for field in fields if field not in EXPORT_NAME_FIELDS]
        if unknown:
            raise ValueError(f"unknown export naming field: {unknown[0]}")
        if len(fields) != len(set(fields)):
            raise ValueError("export naming fields must not contain duplicates")
        return fields


class ExportNameRecord(BaseModel):
    project: str
    language: str
    voice: str
    take: int


class ExportNamingPreviewRequest(BaseModel):
    records: list[ExportNameRecord]
    options: ExportNamingOptions | None = None
    audio_format: Literal["wav", "flac", "mp3"] = "wav"
    standard_names: bool = False


class ExportNamingPreviewResponse(BaseModel):
    filenames: list[str]
