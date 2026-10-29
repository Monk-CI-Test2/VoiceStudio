"""Preview audiobook chapters derived from Markdown headings."""

from fastapi import APIRouter

from schemas.chapter_splitting import (
    ChapterSplitOptions,
    ChapterSplitRequest,
    ChapterSplitResponse,
)
from services.chapter_splitting import split_markdown_chapters


router = APIRouter(prefix="/audiobook/chapters", tags=["audiobook"])


@router.post("/preview", response_model=ChapterSplitResponse)
def preview_chapters(request: ChapterSplitRequest) -> ChapterSplitResponse:
    options = request.options
    if request.split_on_headings and options is None:
        # Compatibility with the boolean used before structured options.
        options = ChapterSplitOptions()

    return ChapterSplitResponse(
        chapters=split_markdown_chapters(request.markdown, options)
    )
