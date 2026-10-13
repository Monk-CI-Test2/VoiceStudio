"""Unit and API contracts for deterministic voice-catalog ordering."""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.routers.voice_catalog_ordering import router
from schemas.voice_catalog_ordering import (
    DEFAULT_VOICE_ORDER_FIELDS,
    VoiceCatalogEntry,
    VoiceCatalogOrderOptions,
)
from services.voice_catalog_ordering import order_voice_catalog


@pytest.fixture
def voices() -> list[VoiceCatalogEntry]:
    return [
        VoiceCatalogEntry(
            id="beta",
            name="Beta",
            language="fr",
            engine="local-b",
            quality=0.95,
        ),
        VoiceCatalogEntry(
            id="alpha",
            name="Alpha",
            language="en",
            engine="local-a",
            quality=0.70,
        ),
        VoiceCatalogEntry(
            id="zulu",
            name="Zulu",
            language="en",
            engine="local-b",
            quality=0.90,
        ),
    ]


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _ids(
    voices: list[VoiceCatalogEntry],
    options: VoiceCatalogOrderOptions | None = None,
) -> list[str]:
    return [voice.id for voice in order_voice_catalog(voices, options)]


def test_default_voice_catalog_field_order() -> None:
    assert DEFAULT_VOICE_ORDER_FIELDS == ("language", "quality", "name")


def test_voice_catalog_uses_documented_defaults(
    voices: list[VoiceCatalogEntry],
) -> None:
    assert _ids(voices) == ["zulu", "alpha", "beta"]


def test_empty_voice_catalog_options_use_defaults(
    voices: list[VoiceCatalogEntry],
) -> None:
    assert _ids(voices, VoiceCatalogOrderOptions()) == ["zulu", "alpha", "beta"]


def test_legacy_name_sort_uses_shared_defaults(
    client: TestClient,
    voices: list[VoiceCatalogEntry],
) -> None:
    response = client.post(
        "/voices/catalog/order-preview",
        json={
            "voices": [voice.model_dump() for voice in voices],
            "sort_by_name": True,
        },
    )

    assert response.status_code == 200
    assert [voice["id"] for voice in response.json()["voices"]] == [
        "zulu",
        "alpha",
        "beta",
    ]


def test_configurable_field_precedence(voices: list[VoiceCatalogEntry]) -> None:
    options = VoiceCatalogOrderOptions(fields=["engine", "name"])
    assert _ids(voices, options) == ["alpha", "beta", "zulu"]


def test_quality_orders_highest_first(voices: list[VoiceCatalogEntry]) -> None:
    options = VoiceCatalogOrderOptions(fields=["quality"])
    assert _ids(voices, options) == ["beta", "zulu", "alpha"]


def test_case_insensitive_ties_remain_stable() -> None:
    voices = [
        VoiceCatalogEntry(
            id="first", name="ava", language="en", engine="local", quality=0.8
        ),
        VoiceCatalogEntry(
            id="second", name="Ava", language="en", engine="local", quality=0.8
        ),
    ]
    options = VoiceCatalogOrderOptions(fields=["name"], case_insensitive=True)
    assert _ids(voices, options) == ["first", "second"]


def test_ordering_does_not_mutate_input(voices: list[VoiceCatalogEntry]) -> None:
    original_ids = [voice.id for voice in voices]
    order_voice_catalog(voices, VoiceCatalogOrderOptions(fields=["quality"]))
    assert [voice.id for voice in voices] == original_ids


@pytest.mark.parametrize(
    "fields",
    [["language", "missing"], ["quality", "quality"]],
)
def test_unknown_or_duplicate_voice_fields_are_rejected(fields: list[str]) -> None:
    with pytest.raises(ValidationError):
        VoiceCatalogOrderOptions(fields=fields)


def test_voice_order_options_have_json_serialization_coverage() -> None:
    options = VoiceCatalogOrderOptions(
        fields=["engine", "quality", "name"],
        case_insensitive=False,
    )
    assert json.loads(options.model_dump_json()) == {
        "fields": ["engine", "quality", "name"],
        "case_insensitive": False,
    }
