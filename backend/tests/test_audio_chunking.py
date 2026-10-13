"""Unit and API contracts for silence-aware audio chunk planning."""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.routers.audio_chunking import router
from schemas.audio_chunking import DEFAULT_MAX_CHUNK_MS, AudioChunkOptions
from services.audio_chunking import plan_audio_chunks


DURATION_MS = 70_000
SILENCE_POINTS_MS = [29_000, 40_000, 58_000]


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _ends(options: AudioChunkOptions | None = None) -> list[int]:
    return [
        chunk.end_ms
        for chunk in plan_audio_chunks(DURATION_MS, SILENCE_POINTS_MS, options)
    ]


def test_default_maximum_audio_chunk_duration() -> None:
    assert DEFAULT_MAX_CHUNK_MS == 30_000


def test_audio_chunking_uses_documented_defaults() -> None:
    assert _ends() == [29_000, 58_000, 70_000]


def test_empty_audio_chunk_options_use_defaults() -> None:
    assert _ends(AudioChunkOptions()) == [29_000, 58_000, 70_000]


def test_legacy_chunk_seconds_uses_equivalent_milliseconds(
    client: TestClient,
) -> None:
    response = client.post(
        "/audio/chunks/preview",
        json={
            "duration_ms": DURATION_MS,
            "silence_points_ms": SILENCE_POINTS_MS,
            "chunk_seconds": 30,
        },
    )

    assert response.status_code == 200
    assert [chunk["end_ms"] for chunk in response.json()["chunks"]] == [
        29_000,
        58_000,
        70_000,
    ]


def test_custom_maximum_duration_is_respected() -> None:
    assert _ends(AudioChunkOptions(max_chunk_ms=20_000)) == [
        20_000,
        40_000,
        58_000,
        70_000,
    ]


def test_hard_splits_can_be_disabled() -> None:
    chunks = plan_audio_chunks(
        25_000,
        [22_000],
        AudioChunkOptions(max_chunk_ms=10_000, allow_hard_split=False),
    )
    assert [(chunk.start_ms, chunk.end_ms) for chunk in chunks] == [
        (0, 22_000),
        (22_000, 25_000),
    ]


def test_silence_preference_can_be_disabled() -> None:
    chunks = plan_audio_chunks(
        25_000,
        [9_000, 19_000],
        AudioChunkOptions(max_chunk_ms=10_000, prefer_silence=False),
    )
    assert [chunk.end_ms for chunk in chunks] == [10_000, 20_000, 25_000]


def test_chunk_indexes_and_boundaries_are_stable() -> None:
    chunks = plan_audio_chunks(
        20_000,
        [8_000],
        AudioChunkOptions(max_chunk_ms=10_000),
    )
    assert [chunk.model_dump() for chunk in chunks] == [
        {"index": 1, "start_ms": 0, "end_ms": 8_000},
        {"index": 2, "start_ms": 8_000, "end_ms": 18_000},
        {"index": 3, "start_ms": 18_000, "end_ms": 20_000},
    ]


@pytest.mark.parametrize(
    "values",
    [
        {"max_chunk_ms": 0},
        {"min_chunk_ms": 0},
        {"max_chunk_ms": 600_001},
    ],
)
def test_invalid_audio_chunk_options_are_rejected(values: dict[str, int]) -> None:
    with pytest.raises(ValidationError):
        AudioChunkOptions(**values)


@pytest.mark.parametrize(
    "duration_ms, silence_points_ms",
    [(0, []), (1_000, [1_000]), (1_000, [1_500])],
)
def test_invalid_audio_timelines_are_rejected(
    duration_ms: int,
    silence_points_ms: list[int],
) -> None:
    with pytest.raises(ValueError):
        plan_audio_chunks(duration_ms, silence_points_ms)


def test_audio_chunk_options_have_json_serialization_coverage() -> None:
    options = AudioChunkOptions(
        max_chunk_ms=20_000,
        min_chunk_ms=2_000,
        prefer_silence=False,
        allow_hard_split=False,
    )
    assert json.loads(options.model_dump_json()) == {
        "max_chunk_ms": 20_000,
        "min_chunk_ms": 2_000,
        "prefer_silence": False,
        "allow_hard_split": False,
    }
