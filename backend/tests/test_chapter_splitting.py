"""Unit and API contracts for Markdown audiobook chapter splitting."""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.routers.chapter_splitting import router
from schemas.chapter_splitting import DEFAULT_MAX_HEADING_LEVEL, ChapterSplitOptions
from services.chapter_splitting import split_markdown_chapters


MANUSCRIPT = """Opening note.

# Overview
First section.

## Details
Second section.

### Deep dive
Third section.
"""


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_default_chapter_heading_level() -> None:
    assert DEFAULT_MAX_HEADING_LEVEL == 2


def test_chapter_split_uses_documented_defaults() -> None:
    chapters = split_markdown_chapters(MANUSCRIPT)
    assert [chapter.title for chapter in chapters] == [
        "Preface",
        "Overview",
        "Details",
    ]


def test_empty_chapter_options_use_defaults() -> None:
    chapters = split_markdown_chapters(MANUSCRIPT, ChapterSplitOptions())
    assert [chapter.title for chapter in chapters] == [
        "Preface",
        "Overview",
        "Details",
    ]


def test_legacy_heading_splitting_uses_shared_defaults(client: TestClient) -> None:
    response = client.post(
        "/audiobook/chapters/preview",
        json={"markdown": MANUSCRIPT, "split_on_headings": True},
    )

    assert response.status_code == 200
    assert [chapter["title"] for chapter in response.json()["chapters"]] == [
        "Preface",
        "Overview",
        "Details",
    ]


def test_custom_heading_depth_is_respected() -> None:
    chapters = split_markdown_chapters(
        MANUSCRIPT,
        ChapterSplitOptions(max_heading_level=3),
    )
    assert [chapter.title for chapter in chapters] == [
        "Preface",
        "Overview",
        "Details",
        "Deep dive",
    ]


def test_headings_can_be_excluded_from_spoken_text() -> None:
    chapters = split_markdown_chapters(
        "# One\nWords\n## Two\nMore words",
        ChapterSplitOptions(max_heading_level=2, include_heading=False),
    )
    assert [chapter.text for chapter in chapters] == ["Words", "More words"]


def test_chapter_ids_and_order_are_stable() -> None:
    chapters = split_markdown_chapters(
        "# Same\nFirst\n# Same\nSecond",
        ChapterSplitOptions(max_heading_level=1),
    )
    assert [(chapter.id, chapter.title) for chapter in chapters] == [
        ("chapter-001", "Same"),
        ("chapter-002", "Same"),
    ]


def test_preface_can_be_discarded() -> None:
    chapters = split_markdown_chapters(
        "Discard me\n# Keep\nSpoken",
        ChapterSplitOptions(max_heading_level=1, preserve_preface=False),
    )
    assert [chapter.title for chapter in chapters] == ["Keep"]


@pytest.mark.parametrize(
    "values",
    [
        {"max_heading_level": 0},
        {"max_heading_level": 7},
        {"minimum_characters": 0},
    ],
)
def test_invalid_chapter_options_are_rejected(values: dict[str, int]) -> None:
    with pytest.raises(ValidationError):
        ChapterSplitOptions(**values)


def test_chapter_options_have_json_serialization_coverage() -> None:
    options = ChapterSplitOptions(
        max_heading_level=3,
        include_heading=False,
        preserve_preface=False,
        minimum_characters=20,
    )
    assert json.loads(options.model_dump_json()) == {
        "max_heading_level": 3,
        "include_heading": False,
        "preserve_preface": False,
        "minimum_characters": 20,
    }
