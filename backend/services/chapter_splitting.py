"""Split Markdown manuscripts into stable audiobook chapters."""

from __future__ import annotations

import re

from schemas.chapter_splitting import (
    DEFAULT_MAX_HEADING_LEVEL,
    Chapter,
    ChapterSplitOptions,
)


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _chapter_text(lines: list[str]) -> str:
    return "\n".join(lines).strip()


def _append_chapter(
    chapters: list[tuple[str, str]],
    *,
    title: str,
    lines: list[str],
    minimum_characters: int,
) -> None:
    text = _chapter_text(lines)
    if not text:
        return
    if chapters and len(text) < minimum_characters:
        previous_title, previous_text = chapters[-1]
        chapters[-1] = (previous_title, f"{previous_text}\n\n{text}")
        return
    chapters.append((title, text))


def split_markdown_chapters(
    markdown: str,
    options: ChapterSplitOptions | None = None,
) -> list[Chapter]:
    """Split a manuscript without reordering or renumbering its content."""

    if options is None:
        options = ChapterSplitOptions(
            max_heading_level=DEFAULT_MAX_HEADING_LEVEL,
        )

    # Explicit options are authoritative, including an omitted heading level.
    max_heading_level = options.max_heading_level or 6
    raw_chapters: list[tuple[str, str]] = []
    current_title = "Preface"
    current_lines: list[str] = []
    has_seen_heading = False

    for line in markdown.splitlines():
        match = _HEADING.match(line)
        if match is None or len(match.group(1)) > max_heading_level:
            current_lines.append(line)
            continue

        if has_seen_heading or options.preserve_preface:
            _append_chapter(
                raw_chapters,
                title=current_title,
                lines=current_lines,
                minimum_characters=options.minimum_characters,
            )

        has_seen_heading = True
        current_title = match.group(2).strip()
        current_lines = [line] if options.include_heading else []

    if has_seen_heading or options.preserve_preface:
        _append_chapter(
            raw_chapters,
            title=current_title,
            lines=current_lines,
            minimum_characters=options.minimum_characters,
        )

    return [
        Chapter(id=f"chapter-{index:03d}", title=title, text=text)
        for index, (title, text) in enumerate(raw_chapters, start=1)
    ]
