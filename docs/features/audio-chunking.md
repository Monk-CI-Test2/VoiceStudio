# Silence-aware audio chunking

`POST /audio/chunks/preview` plans contiguous chunks for long recordings before
transcription or synthesis work starts. Plans keep source order and cover the
complete recording without gaps.

The documented maximum chunk duration is 30 seconds. The planner prefers the
latest detected silence inside each chunk, enforces a configurable minimum
duration, and can either make a hard split or wait for a later silence.

Empty options use the documented defaults. Invalid durations and silence points
are rejected. The deprecated `chunk_seconds` request field remains compatible
with the millisecond-based structured options.
