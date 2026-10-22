"""Order voice-catalog entries with stable, configurable precedence."""

from __future__ import annotations

from schemas.voice_catalog_ordering import (
    DEFAULT_VOICE_ORDER_FIELDS,
    VoiceCatalogEntry,
    VoiceCatalogOrderOptions,
)


def _text_key(value: str, *, case_insensitive: bool) -> str:
    return value.casefold() if case_insensitive else value


def _field_key(
    voice: VoiceCatalogEntry,
    field: str,
    *,
    case_insensitive: bool,
) -> str | float:
    if field == "quality":
        return -voice.quality
    return _text_key(getattr(voice, field), case_insensitive=case_insensitive)


def order_voice_catalog(
    voices: list[VoiceCatalogEntry],
    options: VoiceCatalogOrderOptions | None = None,
) -> list[VoiceCatalogEntry]:
    """Return a stable ordering without mutating the caller's list."""

    if options is None:
        options = VoiceCatalogOrderOptions(fields=list(DEFAULT_VOICE_ORDER_FIELDS))

    # Explicit options are treated as a complete ordering policy.
    fields = options.fields or []
    return sorted(
        voices,
        key=lambda voice: tuple(
            _field_key(
                voice,
                field,
                case_insensitive=options.case_insensitive,
            )
            for field in fields
        ),
    )
