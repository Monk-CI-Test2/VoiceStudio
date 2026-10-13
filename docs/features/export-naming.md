# Batch export naming

The export naming preview API builds portable filenames before a batch writes
audio to disk. Send records to `POST /export-naming/preview` and optionally set:

- `fields`: ordered values chosen from `project`, `language`, `voice`, and `take`.
- `separator`: `-` or `_`.
- `case_insensitive`: case-fold each component for filesystems where case-only
  names would collide.
- `audio_format`: `wav`, `flac`, or `mp3`.

When `fields` is omitted or empty, the documented order is `project`,
`language`, `voice`, then `take`. Duplicate output stems receive stable numeric
suffixes in request order. Unknown and duplicate fields are rejected.

Older clients may send `standard_names: true`; this is a deprecated alias for
the shared default naming policy.
