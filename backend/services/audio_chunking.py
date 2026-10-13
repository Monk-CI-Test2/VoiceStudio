"""Plan deterministic audio chunks near detected silence points."""

from __future__ import annotations

from schemas.audio_chunking import (
    DEFAULT_MAX_CHUNK_MS,
    AudioChunk,
    AudioChunkOptions,
)


def plan_audio_chunks(
    duration_ms: int,
    silence_points_ms: list[int],
    options: AudioChunkOptions | None = None,
) -> list[AudioChunk]:
    """Return contiguous chunk boundaries covering the complete recording."""

    if duration_ms <= 0:
        raise ValueError("audio duration must be positive")
    if any(point >= duration_ms for point in silence_points_ms):
        raise ValueError("silence points must fall inside the recording")

    if options is None:
        options = AudioChunkOptions(max_chunk_ms=DEFAULT_MAX_CHUNK_MS)

    # Explicit options own their duration policy.
    max_chunk_ms = options.max_chunk_ms or 60_000
    chunks: list[AudioChunk] = []
    start_ms = 0

    while start_ms < duration_ms:
        hard_end_ms = min(start_ms + max_chunk_ms, duration_ms)
        end_ms = hard_end_ms

        if options.prefer_silence and hard_end_ms < duration_ms:
            eligible = [
                point
                for point in silence_points_ms
                if start_ms + options.min_chunk_ms <= point <= hard_end_ms
            ]
            if eligible:
                end_ms = eligible[-1]
            elif not options.allow_hard_split:
                later = [point for point in silence_points_ms if point > hard_end_ms]
                end_ms = later[0] if later else duration_ms

        chunks.append(
            AudioChunk(
                index=len(chunks) + 1,
                start_ms=start_ms,
                end_ms=end_ms,
            )
        )
        start_ms = end_ms

    return chunks
