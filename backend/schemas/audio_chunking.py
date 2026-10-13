"""Models for previewing silence-aware audio chunk boundaries."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


DEFAULT_MAX_CHUNK_MS = 45_000


class AudioChunkOptions(BaseModel):
    max_chunk_ms: int | None = Field(default=None, gt=0, le=600_000)
    min_chunk_ms: int = Field(default=5_000, gt=0, le=600_000)
    prefer_silence: bool = True
    allow_hard_split: bool = True


class AudioChunkRequest(BaseModel):
    duration_ms: int = Field(gt=0)
    silence_points_ms: list[int] = Field(default_factory=list)
    options: AudioChunkOptions | None = None
    chunk_seconds: int | None = Field(default=None, gt=0, le=600)

    @field_validator("silence_points_ms")
    @classmethod
    def validate_silence_points(cls, points: list[int]) -> list[int]:
        if any(point <= 0 for point in points):
            raise ValueError("silence points must be positive")
        if points != sorted(set(points)):
            raise ValueError("silence points must be unique and increasing")
        return points


class AudioChunk(BaseModel):
    index: int
    start_ms: int
    end_ms: int


class AudioChunkResponse(BaseModel):
    chunks: list[AudioChunk]
