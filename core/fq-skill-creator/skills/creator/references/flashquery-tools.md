# FlashQuery MCP Tool Reference

Current reference for FlashQuery MCP tools. The FlashQuery source repo is the source of truth; this file reflects the current consolidated tool surface. FlashQuery does not alias removed legacy tool names.

All MCP tool responses use the standard envelope `{ content: [{ type: "text", text: "..." }] }`. Most FlashQuery tools put JSON in `content[0].text`. Expected domain errors usually return a JSON error payload in that text; runtime errors may set `isError: true`.

## Current Tools

### Documents

#### `write_document`

Create or update one markdown document.

Required patterns:
- Create: `mode: "create"`, `path`, `title`; optional `content`, `frontmatter`, `tags`.
- Update: `mode: "update"`, `identifier`; at least one of `content`, `title`, `frontmatter`, or `tags`.
- `tags` replaces the full tag list. Use `apply_tags` for additive/removal tag edits.
- `frontmatter` accepts custom fields only. Managed data such as `fq_id`, `fqc_id`, `status`, `created`, `updated`, tags, and instance identifiers are rejected.

Example:
```js
mcp__flashquery__write_document({
  mode: "create",
  path: "projects/acme/brief.md",
  title: "Acme Brief",
  content: "# Acme Brief\n\n...",
  tags: ["#project/acme"]
})
```

#### `get_document`

Read one or more documents by path, `fq_id`, or filename.

Parameters:
- `identifiers`: string or string array.
- `include`: any of `["body", "frontmatter", "headings"]`; default `["body"]`.
- `sections`: heading names to extract; requires `"body"` in `include`.
- `include_nested`: section extraction option, default `true`.
- `occurrence`: 1-indexed heading occurrence when `sections` has exactly one item.
- `max_depth`: heading depth 1-6.
- `follow_ref`: dot path into frontmatter whose string value resolves to another document.

#### `archive_document`

Archive one or more documents without deleting the file. Parameters: `identifiers` as string or string array.

#### `remove_document`

Archive then remove documents from their current path. If a trash folder is configured, files move there; otherwise they are deleted. Parameters: `identifiers` as string or string array. Use `archive_document` for reversible archive-only workflows.

#### `copy_document`

Copy one source document to a new path. Parameters: `identifier`, optional `destination`. The copy gets a new `fq_id`; source metadata is copied as-is.

#### `move_document`

Move or rename one document while preserving its `fq_id`. Parameters: `identifier`, `destination`. Existing links are not rewritten automatically.

#### `insert_in_doc`

Insert markdown at `top`, `bottom`, `after_heading`, `before_heading`, or `end_of_section`.

Parameters: `identifier`, `position`, `content`, optional `heading`, `occurrence`, `include_nested`, `heading_match` (`"contains"` or `"exact"`), and `heading_level`.

#### `replace_doc_section`

Replace or delete a heading section. Parameters: `identifier`, `heading`, `content`, optional `include_nested`, `heading_match`, `heading_level`, `occurrence`. Passing `content: ""` deletes the heading and section.

#### `apply_tags`

Add or remove tags on ordered document and memory targets.

Preferred parameters:
```js
mcp__flashquery__apply_tags({
  targets: [{ entity_type: "document", identifier: "projects/acme/brief.md" }],
  add_tags: ["#status/review"],
  remove_tags: ["#status/draft"]
})
```

Compatibility parameters `identifiers` and `memory_id` are still accepted, but new skills should use `targets`.

#### `insert_doc_link`

Transitional helper that adds a wiki-style link to one or more source documents. Parameters: `identifiers`, `target_identifier`, optional `property`. This is transitional and may eventually be replaced by macro tooling.

#### `list_vault`

Browse vault files and directories.

Parameters:
- `path`: optional directory path, default `/`.
- `show`: `"files"`, `"directories"`, or `"all"`.
- `include`: optional `["metadata", "tracking"]`.
- `recursive`: boolean.
- `extensions`: string array such as `[".md"]`.
- `after`, `before`: relative (`7d`, `24h`, `1w`) or ISO dates.
- `date_field`: `"updated"` or `"created"`.
- `limit`: positive integer, default 200.

The response is structured JSON with `path`, counts, truncation flag, and `entries`.

### Search and Briefing

#### `search`

Unified document and memory search.

Parameters:
- `query`: optional. Empty query requires filters or `list_all: true`.
- `mode`: `"filesystem"`, `"semantic"`, or `"mixed"`; default mixed.
- `entity_types`: any of `["documents", "memories"]`.
- `tags`, `tag_match`, `limit`, `path_filter`, `include_archived`, `list_all`.

Use this instead of removed `search_documents`, `search_memory`, `list_memories`, and `search_all`.

#### `get_briefing`

Transitional tagged briefing helper. Parameters: `tags`, optional `tag_match`, `limit`, `entity_types` (`documents`, `memories`, `records`), and `plugin_id`.

### Memory

#### `write_memory`

Create or update persistent memory.

Create:
```js
mcp__flashquery__write_memory({
  mode: "create",
  content: "Acme prefers async status updates.",
  tags: ["#client/acme"],
  plugin_scope: "crm"
})
```

Update:
```js
mcp__flashquery__write_memory({
  mode: "update",
  memory_id: "uuid",
  content: "Acme now prefers weekly syncs.",
  tags: ["#client/acme"]
})
```

`plugin_scope` is create-only. Updates create a new latest version; use the returned `memory_id` for future updates.

#### `get_memory`

Retrieve memories by ID. Parameters: `memory_ids` as string or string array, optional `include: ["content", "tags_full"]`.

#### `archive_memory`

Archive memory version chains. Parameters: `memory_ids` as string or string array. Legacy `memory_id` is accepted during migration, but use `memory_ids`.

### Plugin Records

#### `register_plugin`

Register or update a plugin schema. Parameters: `schema_path` or `schema_yaml`, optional `plugin_instance`.

Re-registering a higher schema version applies safe additive changes (new tables/columns) and rejects unsafe changes. Same-version re-registration is idempotent. Version downgrades update registry metadata without DDL migration.

#### `get_plugin_info`

Inspect a registered plugin. Parameters: `plugin_id`, optional `plugin_instance`, optional `include: ["schema", "tables", "status_detail"]`.

#### `unregister_plugin`

Remove plugin registry state. Parameters: `plugin_id`, optional `plugin_instance`, optional `force`. Without `force`, live records produce a conflict. With `force: true`, registry and pending review state are removed while existing plugin table rows are left orphaned. Vault files are not deleted.

#### `write_record`

Create or update one structured plugin record.

Parameters: `mode` (`"create"` or `"update"`), `plugin_id`, optional `plugin_instance`, `table`, optional `id` for update, `data`, optional `include: ["data", "schema_metadata"]`.

#### `get_record`

Retrieve one structured plugin record. Parameters: `plugin_id`, optional `plugin_instance`, `table`, `id`, optional `include`.

#### `archive_record`

Archive structured records. Parameters:
```js
mcp__flashquery__archive_record({
  targets: [{ plugin_id: "crm", table: "contacts", id: "uuid" }]
})
```

#### `search_records`

Search plugin records by filters, text query, semantic data, or taggable tables.

Parameters: optional `plugin_id`, optional `plugin_instance`, optional `table`, optional `filters`, optional `query`, optional `tag`, optional `taggable_tables_only`, optional `include`, optional `limit`.

When `taggable_tables_only` is not true, `plugin_id` and `table` are required.

#### `clear_pending_reviews`

List or clear pending plugin review rows. Parameters: `action` (`"list"` or `"clear"`), optional `plugin_id`, optional `ids` (pending review row IDs returned by `action: "list"`).

### Vault Maintenance

#### `maintain_vault`

Run administrative maintenance. Parameters:
- `action`: `"sync"`, `"repair"`, `"status"`, or an array containing `"sync"`/`"repair"`.
- `dry_run`: only valid for `action: "repair"`.
- `background`: only valid for `action: "sync"`.
- `job_id`: required for `action: "status"`.

Use this instead of removed `force_file_scan` and `reconcile_documents`.

#### `manage_directory`

Create or remove vault directories. Parameters: `action` (`"create"` or `"remove"`), `paths` (array of vault-relative directory paths). Create is recursive and idempotent. Remove is empty-only and returns per-path conflicts for non-empty directories.

### LLM

#### `call_model`

Call configured models or purposes, or perform discovery.

Parameters:
- `resolver`: `"model"`, `"purpose"`, `"list_models"`, `"list_purposes"`, `"search"`, or `"help"`.
- `name`: model alias or purpose name for model/purpose resolvers.
- `messages`: OpenAI-style messages for model/purpose resolvers.
- `parameters`, `template_params`, `return_messages`, `trace_id`.

Caller-provided provider tools are deferred; do not pass `tools` in `parameters`.

#### `get_llm_usage`

Query LLM usage. Parameters: `mode` (`"summary"`, `"by_purpose"`, `"by_model"`, `"recent"`), optional `period` (`"24h"`, `"7d"`, `"30d"`, `"all"`), optional `from_date`, `to_date`, `purpose_name`, `model_name`, `trace_id`, and `limit` for recent mode.

## Removed Tool Replacements

| Removed tool | Use instead |
|--------------|-------------|
| `create_document`, `update_document`, `update_doc_header` | `write_document` |
| `append_to_doc` | `insert_in_doc` |
| `search_documents`, `search_memory`, `list_memories`, `search_all` | `search` |
| `save_memory`, `update_memory` | `write_memory` |
| `create_record`, `update_record` | `write_record` |
| `force_file_scan`, `reconcile_documents` | `maintain_vault` |
| `create_directory`, `remove_directory` | `manage_directory` |
