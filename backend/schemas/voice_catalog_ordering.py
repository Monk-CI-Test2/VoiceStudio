"""Models for deterministic voice-catalog ordering previews."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


VOICE_ORDER_FIELDS = ("language", "engine", "quality", "name")
DEFAULT_VOICE_ORDER_FIELDS = ("language", "name")


class VoiceCatalogOrderOptions(BaseModel):
    fields: list[str] | None = None
    case_insensitive: bool = True

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, fields: list[str] | None) -> list[str] | None:
        if fields is None:
            return None
        unknown = [field for field in fields if field not in VOICE_ORDER_FIELDS]
        if unknown:
            raise ValueError(f"unknown voice ordering field: {unknown[0]}")
        if len(fields) != len(set(fields)):
            raise ValueError("voice ordering fields must not contain duplicates")
        return fields


class VoiceCatalogEntry(BaseModel):
    id: str
    name: str
    language: str
    engine: str
    quality: float = Field(ge=0, le=1)


class VoiceCatalogOrderRequest(BaseModel):
    voices: list[VoiceCatalogEntry]
    options: VoiceCatalogOrderOptions | None = None
    sort_by_name: bool = False


class VoiceCatalogOrderResponse(BaseModel):
    voices: list[VoiceCatalogEntry]
