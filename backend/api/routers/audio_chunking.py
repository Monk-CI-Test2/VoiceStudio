"""Preview silence-aware audio chunk plans."""

from fastapi import APIRouter

from schemas.audio_chunking import (
    AudioChunkOptions,
    AudioChunkRequest,
    AudioChunkResponse,
)
from services.audio_chunking import plan_audio_chunks


router = APIRouter(prefix="/audio/chunks", tags=["audio"])


@router.post("/preview", response_model=AudioChunkResponse)
def preview_audio_chunks(request: AudioChunkRequest) -> AudioChunkResponse:
    options = request.options
    if request.chunk_seconds is not None and options is None:
        # Compatibility with the former seconds-based request field.
        options = AudioChunkOptions(max_chunk_ms=request.chunk_seconds * 10_000)

    return AudioChunkResponse(
        chunks=plan_audio_chunks(
            request.duration_ms,
            request.silence_points_ms,
            options,
        )
    )
