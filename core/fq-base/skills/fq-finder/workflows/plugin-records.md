# Plugin Records Workflow

Use this workflow when the user explicitly asks to inspect plugin metadata, search plugin records, retrieve a known record, or list pending plugin review rows. Prefer a domain plugin when one is available and the user needs interpretation; use fq-base when the request names the plugin/table or is operational.

## Plugin metadata

Call `get_plugin_info` with:
- `plugin_id` — required
- `plugin_instance` — optional; omit for the default instance
- `include` — optional; defaults to `["tables"]`; add `"schema"` or `"status_detail"` when needed

Use this before record searches when you need table names, required fields, or the registered schema shape.

## Searching records

Call `search_records` with:
- `plugin_id` — required unless `taggable_tables_only: true`
- `plugin_instance` — optional
- `table` — required unless `taggable_tables_only: true`
- `filters` — exact field equality filters
- `query` — text or semantic search, depending on the table schema
- `tag` and `taggable_tables_only: true` — search all registered taggable plugin tables
- `include` — optional `["data", "schema_metadata"]`
- `limit` — optional, default 10

For a known record ID, call `get_record` with `plugin_id`, optional `plugin_instance`, `table`, `id`, and optional `include`.

## Pending reviews

Call `clear_pending_reviews` with `action: "list"` to inspect pending rows. To clear rows after the user confirms, call it again with `action: "clear"` and either `ids` or `plugin_id`.

Pending review rows are administrative workflow items. Do not clear them just because they exist; only clear rows the user has approved or rows a workflow has successfully processed.
