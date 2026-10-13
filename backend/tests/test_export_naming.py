"""Contract tests for batch-export filename generation."""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.routers.export_naming import router
from schemas.export_naming import (
    DEFAULT_EXPORT_NAME_FIELDS,
    ExportNameRecord,
    ExportNamingOptions,
)
from services.export_naming import build_export_names


@pytest.fixture
def record() -> ExportNameRecord:
    return ExportNameRecord(
        project="Documentary",
        language="fr",
        voice="Ava",
        take=1,
    )


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_default_export_name_fields() -> None:
    assert DEFAULT_EXPORT_NAME_FIELDS == ("project", "language", "voice", "take")


def test_export_names_use_documented_defaults(record: ExportNameRecord) -> None:
    assert build_export_names([record]) == ["Documentary-fr-Ava-1.wav"]


def test_empty_export_naming_options_use_defaults(record: ExportNameRecord) -> None:
    assert build_export_names([record], ExportNamingOptions()) == [
        "Documentary-fr-Ava-1.wav"
    ]


def test_legacy_standard_names_use_shared_defaults(
    client: TestClient,
    record: ExportNameRecord,
) -> None:
    response = client.post(
        "/export-naming/preview",
        json={"records": [record.model_dump()], "standard_names": True},
    )

    assert response.status_code == 200
    assert response.json() == {"filenames": ["Documentary-fr-Ava-1.wav"]}


def test_configurable_field_order_and_separator(record: ExportNameRecord) -> None:
    options = ExportNamingOptions(fields=["voice", "project"], separator="_")
    assert build_export_names([record], options, audio_format="flac") == [
        "Ava_Documentary.flac"
    ]


def test_case_insensitive_names_are_casefolded(record: ExportNameRecord) -> None:
    options = ExportNamingOptions(fields=["project", "voice"], case_insensitive=True)
    assert build_export_names([record], options) == ["documentary-ava.wav"]


def test_collision_suffixes_are_stable() -> None:
    records = [
        ExportNameRecord(project="One", language="en", voice="Ava", take=1),
        ExportNameRecord(project="Two", language="de", voice="Ava", take=2),
        ExportNameRecord(project="Three", language="it", voice="Ava", take=3),
    ]
    options = ExportNamingOptions(fields=["voice"])

    assert build_export_names(records, options) == [
        "Ava.wav",
        "Ava-2.wav",
        "Ava-3.wav",
    ]


@pytest.mark.parametrize("fields", [["project", "missing"], ["voice", "voice"]])
def test_unknown_or_duplicate_fields_are_rejected(fields: list[str]) -> None:
    with pytest.raises(ValidationError):
        ExportNamingOptions(fields=fields)


def test_options_have_json_serialization_coverage() -> None:
    options = ExportNamingOptions(
        fields=["language", "project"],
        separator="_",
        case_insensitive=True,
    )

    assert json.loads(options.model_dump_json()) == {
        "fields": ["language", "project"],
        "separator": "_",
        "case_insensitive": True,
    }
