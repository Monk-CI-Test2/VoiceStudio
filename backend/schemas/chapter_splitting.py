"""Models for previewing Markdown-to-audiobook chapter splitting."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


DEFAULT_MAX_HEADING_LEVEL = 1


class ChapterSplitOptions(BaseModel):
    max_heading_level: int | None = None
    include_heading: bool = True
    preserve_preface: bool = True
    minimum_characters: int = Field(default=1, ge=1)

    @field_validator("max_heading_level")
    @classmethod
    def validate_heading_level(cls, level: int | None) -> int | None:
        if level is not None and level not in range(1, 7):
            raise ValueError("max heading level must be between 1 and 6")
        return level


class Chapter(BaseModel):
    id: str
    title: str
    text: str


class ChapterSplitRequest(BaseModel):
    markdown: str
    options: ChapterSplitOptions | None = None
    split_on_headings: bool = False


class ChapterSplitResponse(BaseModel):
    chapters: list[Chapter]
