# Voice catalog ordering

`POST /voices/catalog/order-preview` returns a stable, configurable ordering of
voice entries without modifying the source catalog.

The documented default precedence is language, quality from highest to lowest,
then name. Callers may order by language, engine, quality, and name in any
non-duplicated sequence. Text comparison is case-insensitive by default.

Empty options use the documented defaults. Unknown and duplicate fields are
rejected. The deprecated `sort_by_name` flag remains an alias for the shared
default policy.
