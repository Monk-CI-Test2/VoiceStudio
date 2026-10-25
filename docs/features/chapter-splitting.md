# Markdown chapter splitting

Audiobook imports can preview deterministic chapters from Markdown headings at
`POST /audiobook/chapters/preview`.

Structured options control the deepest heading included, whether heading text
is spoken, whether text before the first heading is retained, and the minimum
chapter length. The default splits on level-one and level-two headings, includes
the heading text, and preserves a preface. Empty options use those same defaults.

Chapter IDs follow input order (`chapter-001`, `chapter-002`, and so on), so
repeated titles do not destabilize resume data. Heading levels and minimum
lengths are validated. The deprecated `split_on_headings` boolean remains an
alias for the shared defaults.
