# FlashQuery MCP Tool Reference

Complete reference for all FlashQuery MCP tools. When writing skills that use FlashQuery, call these tools with the prefix `mcp__flashquery__` (e.g., `mcp__flashquery__create_document`).

All tools return JSON responses. Always check `isError` before processing results.

---

## Table of Contents

- [Document Management](#document-management)
- [Section and Metadata Editing](#section-and-metadata-editing)
- [Memory Management](#memory-management)
- [Record Management](#record-management)
- [Plugin Management](#plugin-management)
- [Cross-Resource Tools](#cross-resource-tools)
- [Vault Maintenance](#vault-maintenance)

---

## Document Management

### create_document

Create a new markdown document in the vault. Provide a title, optional body content, optional tags, and an optional vault-relative path to control where it's saved. Defaults to vault root if no path is given. Returns the new document's fqc_id, path, and metadata.

Use this when the user wants to start a new document, note, record, or page.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | yes | Document title |
| `content` | string | yes | Document body (markdown). Pass `""` to create an empty document. |
| `path` | string | no | Vault-relative path (e.g., "clients/acme/notes.md"). Defaults to vault root. |
| `tags` | string[] | no | Tags for categorization |
| `frontmatter` | object | no | Additional frontmatter fields. Cannot override fqc_id, status, created, or fqc_instance. |

**Returns:** Document `fqc_id` (UUID), path, title, tags, and status.

**Example:**
```
mcp__flashquery__create_document({
  title: "Intake: Acme Corp - 2026-04-21",
  content: "## Background\n\nAcme Corp reached out about...",
  path: "clients/acme/intake.md",
  tags: ["#type/intake", "#status/new"]
})
```

**Usage notes:**
- Parse `fqc_id` from the response — use it for all subsequent references to this document (not the path).
- If a file already exists at the path, the call will fail. Use `update_document` or `append_to_doc` instead.

---

### get_document

Read a document's body content by path, fqc_id, or filename. Returns the full markdown body without frontmatter. To read only specific sections instead of the full body, pass a `sections` array with heading names — this is far more token-efficient for large documents. For document structure and frontmatter without body content, use `get_doc_outline` instead.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `sections` | string[] | no | Heading names to extract (e.g., ["Configuration", "Examples"]). Omit to get full document. |
| `include_subheadings` | boolean | no | If true (default), include all nested content under heading until next same-or-higher heading. If false, stop at first subheading. |
| `occurrence` | number | no | Which occurrence of heading if multiple share the same name (1-indexed). Default: 1 |

**Returns:** Document body content (without frontmatter). Metadata includes path and change status.

**Example — full document:**
```
mcp__flashquery__get_document({
  identifier: "clients/acme/intake.md"
})
```

**Example — specific section only:**
```
mcp__flashquery__get_document({
  identifier: "a1b2c3d4-...",
  sections: ["Background", "Next Steps"],
  include_subheadings: true
})
```

**Usage notes:**
- The `identifier` is flexible: "clients/acme/notes.md", a UUID, or just "notes.md" all work. UUIDs are most reliable.
- Use `sections` to pull only what you need — avoids loading entire large documents into context.

---

### update_document

Overwrite an existing document's body content and/or frontmatter fields. Replaces the entire body when `content` is provided — use `replace_doc_section` or `insert_in_doc` for targeted section edits instead. Does not create a new document — use `create_document` for that.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `content` | string | no | New document body (markdown). Replaces entire body. If omitted, body is preserved unchanged. |
| `title` | string | no | New title. If omitted, existing title is preserved. |
| `tags` | string[] | no | Replacement tag list. Replaces all existing tags. If omitted, tags are preserved. |
| `frontmatter` | object | no | Additional frontmatter fields to merge. Cannot override fqc_id, fqc_instance, created, or status. |

**Returns:** Confirmation with updated metadata.

**Example:**
```
mcp__flashquery__update_document({
  identifier: "a1b2c3d4-...",
  content: "## Revised Background\n\nAfter our call...",
  title: "Intake: Acme Corp - Revised"
})
```

**Usage notes:**
- This replaces the entire body and triggers re-embedding. For targeted edits, prefer `replace_doc_section` or `insert_in_doc`.
- For tag changes, prefer `apply_tags` — it supports incremental add/remove without replacing the entire tag list.

---

### archive_document

Archive one or more documents by setting their status to "archived". The file remains in the vault and its fqc_id is preserved — nothing is deleted. Archived documents are excluded from search results. Use this when the user is done with a document but may want to reference it later.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifiers` | string or string[] | yes | One or more document identifiers — each can be a vault-relative path, fqc_id UUID, or filename. Pass a single string or an array for batch archival. |

**Returns:** Confirmation message.

**Example — single document:**
```
mcp__flashquery__archive_document({
  identifiers: "clients/acme/old-notes.md"
})
```

**Example — batch archival:**
```
mcp__flashquery__archive_document({
  identifiers: ["a1b2c3d4-...", "e5f6g7h8-..."]
})
```

**Usage notes:**
- The parameter is `identifiers` (plural), not `identifier`. It accepts a single string or an array.

---

### search_documents

Search vault documents by semantic query, tags, or text substring. Returns ranked results with title, path, fqc_id, tags, and match score. Excludes archived documents. Use this when the user asks to find, search for, or look up documents. For browsing by folder structure instead of searching, use `list_vault`.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | no | Substring search on title or path (case-insensitive). Optional when filtering by tags alone. |
| `tags` | string[] | no | Filter results by tags |
| `tag_match` | "any" or "all" | no | How to combine multiple tags. "any" (default): at least one tag matches. "all": every tag must be present. |
| `mode` | "filesystem" or "semantic" or "mixed" | no | Search strategy. "filesystem" (default): frontmatter scan. "semantic": vector similarity via pgvector. "mixed": both combined (semantic-ranked first, unindexed appended). |
| `limit` | number | no | Maximum results. Default: 20 |

**Returns:** List of documents with path, title, tags, fqc_id, and match scores.

**Example — keyword search:**
```
mcp__flashquery__search_documents({
  query: "acme",
  mode: "filesystem"
})
```

**Example — semantic search with tag filter:**
```
mcp__flashquery__search_documents({
  query: "client onboarding process",
  tags: ["#type/intake"],
  mode: "mixed",
  limit: 10
})
```

**Example — tag-only filter (no search query):**
```
mcp__flashquery__search_documents({
  tags: ["#status/draft"],
  tag_match: "all"
})
```

**Usage notes:**
- The parameter is `mode`, not `search_mode`.
- `query` is optional — you can search by tags alone.
- `"mixed"` combines keyword and semantic search for best coverage.
- `"semantic"` uses vector embeddings — good for conceptual similarity but won't find exact phrases.
- `"filesystem"` is keyword/path-based — fast and exact but no conceptual understanding.

---

### copy_document

Copy a vault document to a new location, creating a new document with its own fqc_id and fresh timestamps. The copy preserves the source title, tags, and all custom frontmatter fields. The original document is not modified.

Use this when the user wants to duplicate a document as a starting point — e.g., creating a new contact from a template.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Source document path, fqc_id UUID, or filename |
| `destination` | string | no | Vault-relative path for the copy. Defaults to vault root using source title as filename. |

**Returns:** New document's `fqc_id`, path, and metadata.

**Example:**
```
mcp__flashquery__copy_document({
  identifier: "templates/intake-template.md",
  destination: "clients/newcorp/intake.md"
})
```

**Usage notes:**
- The parameter is `destination`, not `new_path` or `new_title`.
- No title or tag customization at copy time — the copy inherits everything from the source. Modify afterwards with `update_document` or `apply_tags` if needed.

---

### move_document

Move or rename a document in the vault while preserving its fqc_id, history, and all plugin associations. Creates intermediate directories automatically. Renaming is a special case — move to the same directory with a different filename.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Source document path, fqc_id UUID, or filename |
| `destination` | string | yes | Vault-relative destination path including filename (extension optional — uses source extension if omitted) |

**Returns:** Confirmation with new path.

**Example — move to new folder:**
```
mcp__flashquery__move_document({
  identifier: "inbox/meeting-notes.md",
  destination: "clients/acme/meeting-notes.md"
})
```

**Example — rename in place:**
```
mcp__flashquery__move_document({
  identifier: "clients/acme/notes.md",
  destination: "clients/acme/intake-notes.md"
})
```

**Usage notes:**
- The parameter is `destination`, not `new_path`.
- The document's identity (fqc_id) is preserved — no data is lost.
- References to this document in other files are NOT automatically updated.

---

### list_vault

Browse vault files and directories by path. Returns file metadata (title, tags, fqc_id, size, timestamps) for tracked files, and filesystem metadata for untracked files. Supports recursive listing, multi-extension filtering, date filtering on updated or created timestamps, directory-only or file-only views, and table or detailed output formats.

Use this when the user asks "what's in this folder," "what changed recently," or "show me the subdirectories." For finding documents by content or tags, use `search_documents` instead.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | no | Vault-relative directory path. Use `""` or `"."` for vault root. Default: `"/"`. |
| `recursive` | boolean | no | If true, walk entire subtree. Default: false. |
| `show` | string | no | What to include: `"files"`, `"directories"`, or `"all"`. Default: `"all"`. |
| `format` | string | no | Output format: `"table"` (markdown table, default) or `"detailed"` (key-value blocks). |
| `extensions` | string[] | no | Filter by file extensions (e.g., `[".md", ".txt"]`). Case-insensitive. Ignored when `show` is `"directories"`. |
| `after` | string | no | Include entries modified/created >= this date. Relative (`"7d"`, `"24h"`, `"1w"`) or ISO (`"2026-04-01"`). |
| `before` | string | no | Include entries modified/created <= this date. Relative or ISO format. |
| `date_field` | string | no | Which timestamp `after`/`before` filter against: `"updated"` (default) or `"created"`. |
| `limit` | integer | no | Maximum entries to return. Default: 200. |

**Returns:** File and directory metadata with title, tags, fqc_id, size, and timestamps for tracked files. Untracked files show filesystem metadata only. Response ends with a summary line.

**Example — list a folder:**
```
mcp__flashquery__list_vault({
  path: "clients/acme"
})
```

**Example — recent markdown files across vault with full metadata:**
```
mcp__flashquery__list_vault({
  path: "",
  recursive: true,
  extensions: [".md"],
  after: "7d",
  format: "detailed"
})
```

**Example — directories only:**
```
mcp__flashquery__list_vault({
  path: "projects",
  show: "directories"
})
```

**Usage notes:**
- `path` is optional (default `"/"`). Use `""` or `"."` for the vault root.
- `extensions` is an array, not a single string. Use `[".md"]` not `".md"`.
- The old date range parameters are gone — use `after` and `before` instead.
- When `show` is `"directories"`, `extensions` is silently ignored.
- Default output is a markdown table. Use `format: "detailed"` when you need `fqc_id` or tags for follow-up tool calls.

---

## Section and Metadata Editing

These tools modify specific parts of a document without rewriting the whole thing. They preserve surrounding content and avoid unnecessary re-embedding.

### append_to_doc

Append markdown content to the end of a document. Use for adding new entries, log lines, or notes at the bottom of a file. For inserting content at a specific location, use `insert_in_doc` instead.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `content` | string | yes | Content to append (include any markdown structure such as headings) |

**Returns:** Confirmation with document path.

**Example:**
```
mcp__flashquery__append_to_doc({
  identifier: "a1b2c3d4-...",
  content: "\n## Follow-up Notes\n\nDiscussed timeline..."
})
```

---

### insert_in_doc

Insert markdown content at a specific position in a document: after a heading, before a heading, at the end of a section, at the top, or at the bottom. Use this for adding entries to a specific section (e.g., logging a new interaction under "## Interactions") or prepending content to a document.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `content` | string | yes | Markdown content to insert (not including the anchor heading itself) |
| `position` | "top" or "bottom" or "after_heading" or "before_heading" or "end_of_section" | yes | Where to insert content |
| `heading` | string | no | Anchor heading name. Required for `after_heading`, `before_heading`, and `end_of_section` positions. |
| `occurrence` | number | no | Which occurrence of heading if multiple match the same name (1-indexed). Default: 1 |

**Returns:** Confirmation message.

**Example — insert after a heading:**
```
mcp__flashquery__insert_in_doc({
  identifier: "a1b2c3d4-...",
  content: "\n- 2026-04-21: Called about renewal\n",
  position: "after_heading",
  heading: "Interactions"
})
```

**Example — prepend to top:**
```
mcp__flashquery__insert_in_doc({
  identifier: "a1b2c3d4-...",
  content: "> **Status:** Under review as of 2026-04-21\n",
  position: "top"
})
```

**Usage notes:**
- The parameter is `heading`, not `anchor_heading`.
- `position` is required — there is no default.
- Supports five positions: `top`, `bottom`, `after_heading`, `before_heading`, `end_of_section`.

---

### replace_doc_section

Replace the content of a specific heading section in a document, leaving all other sections untouched. The heading line is preserved; only the section body is replaced. Use `include_subheadings` to control whether child sections are included in the replacement.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `heading` | string | yes | Heading text to match (case-sensitive) |
| `content` | string | yes | New markdown content for section body (does not include the heading line) |
| `include_subheadings` | boolean | no | When true (default), replace full section including nested headings. When false, preserve child headings. |
| `occurrence` | number | no | Which occurrence if heading appears multiple times (1-indexed). Default: 1 |

**Returns:** Confirmation message. Includes the old section content for undo purposes.

**Example:**
```
mcp__flashquery__replace_doc_section({
  identifier: "a1b2c3d4-...",
  heading: "Pricing",
  content: "\nRevised pricing: $5,000/month for the base tier.\n"
})
```

**Usage notes:**
- The parameter is `content`, not `new_content`.
- Heading match is by text, not by heading level — "Configuration" matches `## Configuration` and `### Configuration`.

---

### update_doc_header

Update frontmatter fields on a document without touching the body content. Pass a map of field names to new values. Pass null as a value to remove a field. Syncs tags to the database automatically when the `tags` key is included.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Document path, fqc_id UUID, or filename |
| `updates` | object | yes | Map of frontmatter fields to set. Use null to remove a field. |

**Returns:** Confirmation message.

**Example:**
```
mcp__flashquery__update_doc_header({
  identifier: "a1b2c3d4-...",
  updates: {
    "client_stage": "active",
    "legacy_field": null
  }
})
```

---

### apply_tags

Add or remove tags on one or more vault documents or a memory in a single call. Supports batch operations — pass multiple identifiers to tag several documents at once. Adding a tag that already exists is a no-op; removing a tag that doesn't exist is a silent no-op.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifiers` | string or string[] | no | One or more document identifiers. Use this OR `memory_id`, not both. |
| `memory_id` | string | no | UUID of the memory to tag. Use this OR `identifiers`, not both. |
| `add_tags` | string[] | no | Tags to add (idempotent) |
| `remove_tags` | string[] | no | Tags to remove (silent no-op if not present) |

**Returns:** Updated tag list.

**Example — tag a single document:**
```
mcp__flashquery__apply_tags({
  identifiers: "a1b2c3d4-...",
  add_tags: ["#status/active"],
  remove_tags: ["#status/draft"]
})
```

**Example — batch tag multiple documents:**
```
mcp__flashquery__apply_tags({
  identifiers: ["a1b2c3d4-...", "e5f6g7h8-..."],
  add_tags: ["#project/alpha"]
})
```

**Example — tag a memory:**
```
mcp__flashquery__apply_tags({
  memory_id: "f9e8d7c6-...",
  add_tags: ["preference"]
})
```

**Usage notes:**
- The parameter is `identifiers` (plural), not `identifier`.
- There is no `set_tags` parameter — use `add_tags` and `remove_tags` for incremental changes.
- Can target documents OR a memory, but not both in the same call.
- Only one `#status/*` tag allowed per document — remove the old one before adding a new one.

---

### insert_doc_link

Add a wiki-style document link ([[Target Doc]]) to a document's frontmatter links array. Deduplicates automatically — adding the same link twice is a no-op. The display text is derived from the resolved target document's title.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifier` | string | yes | Source document path, fqc_id UUID, or filename |
| `target` | string | yes | Target document path, fqc_id UUID, or filename |
| `property` | string | no | Frontmatter property to add the link to. Default: "links". Alternatives: "related", "parent", etc. |

**Returns:** Confirmation message.

**Example:**
```
mcp__flashquery__insert_doc_link({
  identifier: "a1b2c3d4-...",
  target: "clients/acme/contract.md",
  property: "related"
})
```

**Usage notes:**
- The parameters are `target` and `property`, not `target_identifier`, `link_text`, or `anchor_heading`.
- Link text is derived automatically from the target document's title — you don't specify it.

---

## Memory Management

Memories are short persistent facts, preferences, or observations. They survive across sessions and are searchable by semantic similarity.

### save_memory

Store a persistent fact, preference, or observation that should be recalled in future conversations. Memories survive across sessions — use this for information the user wants remembered long-term, not for temporary notes. Tag memories for easy retrieval later.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | yes | The memory text to store |
| `tags` | string[] | no | Tags for categorization |
| `plugin_scope` | string | no | Plugin scope (e.g., "crm"). Auto-corrected via fuzzy match against registered plugins. Default: "global" |

**Returns:** Memory ID (UUID), tags, and scope information.

**Example:**
```
mcp__flashquery__save_memory({
  content: "Sarah at Acme prefers email over phone calls",
  tags: ["preference", "acme"],
  plugin_scope: "crm"
})
```

**Usage notes:**
- Keep memories concise and factual — they're retrieved by semantic search, so clear language improves recall.
- Use `plugin_scope` to namespace memories to a specific plugin domain.

---

### search_memory

Search memories by semantic similarity, optionally filtered by tags. Returns ranked results with match scores. Use this when the user asks "do I have a memory about X" or "what did I note about Y." For listing all memories without a search query, use `list_memories` instead.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Search query |
| `tags` | string[] | no | Filter by tags |
| `tag_match` | "any" or "all" | no | How to combine tag filters. Default: "any" |
| `threshold` | number | no | Minimum similarity score (0-1). Default: 0.4 |
| `limit` | number | no | Maximum results. Default: 10 |

**Returns:** List of memories with ID, content, tags, match score, and creation date.

**Example:**
```
mcp__flashquery__search_memory({
  query: "communication preferences",
  tags: ["acme"],
  limit: 5
})
```

---

### list_memories

List memories filtered by tags, without requiring a search query. Returns all matching memories with truncated content previews and memory IDs. Use this when the user wants to browse or review memories by category — e.g., "show me my CRM memories" or "list everything tagged preference."

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tags` | string[] | no | Filter by tags |
| `tag_match` | "any" or "all" | no | How to combine tag filters. Default: "any" |
| `limit` | number | no | Maximum results. Default: 50 |

**Returns:** List of memories with IDs, truncated content previews, tags, and metadata.

**Example:**
```
mcp__flashquery__list_memories({
  tags: ["preference"],
  limit: 20
})
```

---

### get_memory

Retrieve one or more memories by their memory ID. Returns full content and all metadata. Pass a single ID or an array of IDs for batch retrieval. Use this after finding memory IDs through `search_memory` or `list_memories` when you need the complete, untruncated content.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_ids` | string or string[] | yes | Single memory ID (UUID) or array of memory IDs for batch retrieval |

**Returns:** Full memory content, tags, version history, and metadata.

**Example — single memory:**
```
mcp__flashquery__get_memory({
  memory_ids: "f9e8d7c6-..."
})
```

**Example — batch retrieval:**
```
mcp__flashquery__get_memory({
  memory_ids: ["f9e8d7c6-...", "a1b2c3d4-..."]
})
```

**Usage notes:**
- The parameter is `memory_ids` (plural), not `memory_id`. It accepts a single string or an array.

---

### update_memory

Update an existing memory's content by ID. Creates a new version — the previous version is preserved for history. Use `search_memory` or `list_memories` to find the memory_id first.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_id` | string (UUID) | yes | UUID of the memory to update |
| `content` | string | yes | New content to replace the existing memory text |
| `tags` | string[] | no | New tags. If omitted, existing tags are preserved. |

**Returns:** New version ID, previous version ID, and version number.

**Example:**
```
mcp__flashquery__update_memory({
  memory_id: "f9e8d7c6-...",
  content: "Sarah at Acme now prefers Slack over email",
  tags: ["preference", "acme"]
})
```

---

### archive_memory

Archive a memory by marking it inactive. Archived memories no longer appear in `search_memory` or `list_memories` results. Use this when a memory is outdated, wrong, or the user asks to forget something.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memory_id` | string (UUID) | yes | UUID of the memory to archive |

**Returns:** Confirmation message.

**Example:**
```
mcp__flashquery__archive_memory({
  memory_id: "f9e8d7c6-..."
})
```

---

## Record Management

Records are structured data rows in plugin-registered tables. Use these when you need custom fields beyond what documents and memories provide (e.g., CRM contacts, task trackers, inventory items).

Records require a registered plugin with a defined schema. See [Plugin Management](#plugin-management).

### create_record

Create a new record in a plugin table — e.g., a CRM contact, a task, a log entry. The table must have been created by `register_plugin` first.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier. Omit for single-instance plugins. |
| `table` | string | yes | Table name as defined in plugin schema |
| `fields` | object | yes | Field values as key-value pairs |

**Returns:** New record's ID (UUID).

**Example:**
```
mcp__flashquery__create_record({
  plugin_id: "crm",
  table: "contacts",
  fields: {
    name: "Sarah Chen",
    company: "Acme Corp",
    role: "VP Engineering",
    email: "sarah@acme.com"
  }
})
```

---

### get_record

Retrieve a single record by its ID from a plugin table. Returns all fields for that record.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |
| `table` | string | yes | Table name as defined in plugin schema |
| `id` | string (UUID) | yes | Record UUID |

**Returns:** Full record as JSON with all fields.

**Example:**
```
mcp__flashquery__get_record({
  plugin_id: "crm",
  table: "contacts",
  id: "a1b2c3d4-..."
})
```

---

### update_record

Update specific fields on an existing record in a plugin table. Pass only the fields that need to change — other fields are preserved.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |
| `table` | string | yes | Table name as defined in plugin schema |
| `id` | string (UUID) | yes | Record UUID |
| `fields` | object | yes | Fields to update (key-value pairs) |

**Returns:** Confirmation of update.

**Example:**
```
mcp__flashquery__update_record({
  plugin_id: "crm",
  table: "contacts",
  id: "a1b2c3d4-...",
  fields: {
    role: "CTO",
    notes: "Promoted in Q1 2026"
  }
})
```

---

### archive_record

Soft-delete a record by setting its status to "archived." The record remains in the database but is excluded from search results. Use this when a record is no longer active but should be preserved for history.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |
| `table` | string | yes | Table name as defined in plugin schema |
| `id` | string (UUID) | yes | Record UUID |

**Returns:** Confirmation message.

**Example:**
```
mcp__flashquery__archive_record({
  plugin_id: "crm",
  table: "opportunities",
  id: "a1b2c3d4-..."
})
```

---

### search_records

Search records in a plugin table by field filters, text query, or semantic similarity. Automatically uses vector search (pgvector) for tables with embedding fields, or text matching (ILIKE) otherwise.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |
| `table` | string | yes | Table name as defined in plugin schema |
| `query` | string | no | Text search query (semantic if table has embed_fields, ILIKE otherwise) |
| `filters` | object | no | Key-value field equality filters (AND logic) |
| `limit` | number | no | Maximum results. Default: 10 |

**Returns:** List of records with match scores.

**Example — text search:**
```
mcp__flashquery__search_records({
  plugin_id: "crm",
  table: "contacts",
  query: "engineering"
})
```

**Example — field filter:**
```
mcp__flashquery__search_records({
  plugin_id: "crm",
  table: "opportunities",
  filters: { stage: "proposal" },
  limit: 20
})
```

**Example — combined:**
```
mcp__flashquery__search_records({
  plugin_id: "crm",
  table: "contacts",
  query: "renewal",
  filters: { relationship_type: "client" }
})
```

**Usage notes:**
- The parameter is `filters` (key-value object with AND logic), not `tags`, `tag_match`, or `status`.
- `query` is optional — you can search by `filters` alone.

---

## Plugin Management

Plugins define custom table schemas for structured data. Register a plugin to create tables, then use Record tools to manage data.

### register_plugin

Register or update a plugin from a YAML schema definition. Creates plugin tables in the database on first registration. On re-registration with a new schema version, automatically applies safe additive changes (new tables, new columns) and rejects unsafe changes (removed tables, type changes) with specific guidance.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `schema_path` | string | no | Path to YAML schema file on disk. Provide this OR `schema_yaml`, not both. |
| `schema_yaml` | string | no | Inline YAML schema string. Provide this OR `schema_path`, not both. |
| `plugin_instance` | string | no | Plugin instance identifier. Omit for single-instance plugins. |

**Returns:** Registration confirmation with created/migrated tables.

**Example YAML schema (tables and columns are arrays, not maps):**
```yaml
id: my-plugin
name: My Plugin
version: "1.0"

tables:
  - name: entries
    description: Main data entries
    embed_fields:
      - name
      - category
    columns:
      - name: name
        type: text
        required: true
        description: Entry name
      - name: category
        type: text
        description: Entry category
      - name: priority
        type: integer
        description: Priority level (1-5)
```

**Schema format rules:**
- `tables` is an **array** of objects (`- name: ...`), not a map. Map-style (`tables: { entries: { ... } }`) is not supported.
- `columns` is an **array** of objects (`- name: ...`), not a map.
- Column `type` must be one of: `text`, `integer`, `boolean`, `uuid`, `timestamptz`.
- Use `embed_fields` (array of column names) at the table level to enable semantic search. There is no separate `search:` block.
- When `embed_fields` is present, the system automatically adds `embedding` and `embedding_updated_at` columns — don't define them manually.
- Plugin metadata (`id`, `name`, `version`) can be at root level (shown above) or nested under `plugin:`.

**Example — register from inline YAML:**
```
mcp__flashquery__register_plugin({
  schema_yaml: "id: my-plugin\nname: My Plugin\nversion: \"1.0\"\ntables:\n  - name: entries\n    columns:\n      - name: title\n        type: text\n        required: true\n"
})
```

---

### get_plugin_info

Get the schema definition, table status, version, and registration details for an installed plugin. Use this to check if a plugin is registered, inspect its table structure, or verify its current schema version.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |

**Returns:** Plugin name, version, instance, table prefix, and detailed table/column structure.

**Example:**
```
mcp__flashquery__get_plugin_info({
  plugin_id: "crm"
})
```

---

### unregister_plugin

Unregister a plugin and tear down its database resources. Call without `confirm_destroy` (or with it set to false) for a dry-run preview showing what will be removed. Call with `confirm_destroy: true` to execute the teardown. Teardown drops plugin tables, clears document ownership claims, deletes plugin-scoped memories, and removes the registry entry. Vault files are never deleted.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier |
| `plugin_instance` | string | no | Plugin instance identifier |
| `confirm_destroy` | boolean | no | Must be true to execute teardown. Omit or false for dry-run preview only. |

**Returns:** Inventory of what will be removed (dry-run) or executed teardown summary.

**Example — dry run:**
```
mcp__flashquery__unregister_plugin({
  plugin_id: "my-plugin"
})
```

**Example — confirmed teardown:**
```
mcp__flashquery__unregister_plugin({
  plugin_id: "my-plugin",
  confirm_destroy: true
})
```

**Usage notes:**
- Always do a dry-run first to show the user what will be removed.

---

## Cross-Resource Tools

### search_all

Search across both documents and memories in a single semantic query. Returns unified, ranked results from both types. Use this when the user's search could match either documents or memories — e.g., "what do I know about Acme" or "find anything related to the Q2 launch." Falls back to filesystem search for documents when semantic search is unavailable.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Search query |
| `tags` | string[] | no | Filter results to items with these tags |
| `tag_match` | "any" or "all" | no | How to combine tags. Default: "any" |
| `limit` | number | no | Maximum results per entity type. Default: 10 |
| `entity_types` | string[] | no | Which types to search: ["documents"], ["memories"], or both (default). |

**Returns:** Ranked results from both documents and memories with match scores and source type.

**Example — search everything:**
```
mcp__flashquery__search_all({
  query: "Acme Corp renewal timeline",
  limit: 10
})
```

**Example — memories only with tag filter:**
```
mcp__flashquery__search_all({
  query: "communication preferences",
  tags: ["crm"],
  entity_types: ["memories"]
})
```

**Usage notes:**
- The parameter is `tags` (single array), not separate `doc_tags` and `mem_tags`.
- `limit` is per entity type, not total. So `limit: 10` returns up to 10 documents and 10 memories.
- Use `entity_types` to restrict to just documents or just memories if needed.

---

### get_briefing

Get a summary of documents and memories matching specified tags. Returns document metadata (title, path, tags, fqc_id) and memory content, grouped by type. Optionally includes plugin record counts when `plugin_id` is provided.

Use this when the user wants an overview of everything related to a topic — e.g., "brief me on the CRM" or "what do we have tagged project-alpha."

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tags` | string[] | yes | Tags to filter by. Documents and memories with any/all of these tags are included. |
| `tag_match` | "any" or "all" | no | Tag matching mode. Default: "any" |
| `limit` | number | no | Maximum results per section. Default: 20 |
| `plugin_id` | string | no | Include records from this plugin. Omit to exclude plugin records. |

**Returns:** Grouped results: document metadata, memory content, and optionally plugin record counts.

**Example:**
```
mcp__flashquery__get_briefing({
  tags: ["acme"],
  tag_match: "any",
  plugin_id: "crm"
})
```

**Usage notes:**
- This is NOT per-document briefing — it's a tag-scoped overview across all documents, memories, and optionally records.
- `tags` is required. For full-text search across everything, use `search_all` instead.

---

### get_doc_outline

Inspect one or more documents' structure without reading the full body. Returns frontmatter (all fields including user-defined), heading hierarchy, and linked files. Accepts a single identifier or an array for batch inspection. Use this when the user asks "what's in this document" or "show me the structure" — it's far cheaper than reading the full body.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `identifiers` | string or string[] | yes | One or more document identifiers. Single string = full structural outline (file-based). Array = DB metadata for batch triage. |
| `max_depth` | number | no | Maximum heading level to include (1-6). Default: 6 (all levels). |
| `exclude_headings` | boolean | no | If true, omit headings from response (metadata only). Default: false. |

**Returns:** Frontmatter fields, heading outline with hierarchy, and linked file references.

**Example — single document:**
```
mcp__flashquery__get_doc_outline({
  identifiers: "clients/acme/intake.md"
})
```

**Example — batch triage:**
```
mcp__flashquery__get_doc_outline({
  identifiers: ["a1b2c3d4-...", "e5f6g7h8-..."],
  max_depth: 2
})
```

**Usage notes:**
- The parameter is `identifiers` (plural), not `identifier`. Accepts a single string or array.
- Use this before `get_document` with `sections` to discover what headings exist.

---

## Vault Maintenance

### force_file_scan

Trigger an immediate vault scan to discover new files, detect moves, and track deletions. Updates the database index with current vault state. Use this before semantic search if you suspect files have been added or changed outside the AI chat, or after bulk file operations.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `background` | boolean | no | If true, scan runs in background and returns immediately. Default: false (synchronous, waits for results). |

**Returns:** Counts: new_files, updated_files, moved_files, deleted_files, status_mismatches.

**Example:**
```
mcp__flashquery__force_file_scan({})
```

---

### reconcile_documents

Scan the database for documents whose vault file is missing. Detects files that were moved (by matching fqc_id in frontmatter at the new location) and updates their path. Files that are permanently gone are marked archived. Use this after bulk file moves, vault reorganization, or when documents show stale path warnings.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `dry_run` | boolean | no | If true, report what would change without making any database updates. Default: false |

**Returns:** Summary of reconciliation actions: new, moved, missing, merged.

**Example — preview changes:**
```
mcp__flashquery__reconcile_documents({
  dry_run: true
})
```

**Example — apply fixes:**
```
mcp__flashquery__reconcile_documents({})
```

---

### create_directory

Create one or more directories in the vault. Creates intermediate directories automatically (mkdir -p semantics). Idempotent: calling on an existing directory succeeds and is noted in the response, not treated as an error. Use this when a skill needs to set up an organizational folder structure before saving documents.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `paths` | string or string[] | yes | One or more vault-relative directory paths to create. Accepts a single string or an array of strings. |
| `root_path` | string | no | Vault-relative base prefix applied to all entries in `paths`. Default: `"/"` (vault root). |

**Returns:** Confirmation with created paths; pre-existing directories are noted (not errored).

**Example — single path:**
```
mcp__flashquery__create_directory({
  paths: "clients/acme/2026"
})
```

**Example — batch with root_path:**
```
mcp__flashquery__create_directory({
  paths: ["contacts", "companies", "interactions"],
  root_path: "CRM"
})
```

**Usage notes:**
- `paths` is the parameter name for `create_directory` — never `path` (singular). It accepts a single string or an array.
- Idempotent: already-existing directories are reported in the response as "already exists," not errored.
- Illegal filesystem characters in directory name segments are sanitized (replaced with spaces) and reported.
- Absolute paths starting with `/` are rejected — all paths must be vault-relative.
- No write lock — pure filesystem operation. No confirmation needed before executing.

---

### remove_directory

Safely remove an empty directory from the vault. Returns an error listing contents if the directory is not empty — no recursive deletion, no force parameter. Use when cleaning up temporary or staging folders after moving or archiving their contents.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | yes | Vault-relative path of the directory to remove |

**Returns:** Confirmation that the directory was removed.

**Example:**
```
mcp__flashquery__remove_directory({
  path: "temp/staging"
})
```

**Usage notes:**
- Only works on empty directories. If the directory has contents, the error response lists everything inside it so you know what to move or remove first.
- Cannot remove the vault root directory.
- Use `move_document` or `archive_document` to clear out files before removing the directory.

---

### clear_pending_reviews

Query or clear pending review items from the `fqc_pending_plugin_review` table for a plugin. This is the primary mechanism for **pull-based document processing** — instead of push callbacks, FlashQuery populates a work queue when it auto-tracks new files or resurrects archived ones, and skills (typically run on a schedule via `/loop` or cron) query the queue, process the items, and clear them.

Call with empty `fqc_ids` to **query** what's pending without deleting anything. Call with `fqc_ids` populated to **clear** those items and return what remains. The response shape is always the same: the current pending list for the plugin after any clearing.

This tool replaces the old `on_document_discovered` push callback pattern. Skills are now triggered on a schedule and pull from this queue rather than being invoked reactively per-file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `plugin_id` | string | yes | Plugin identifier. Always required — queries are scoped to one plugin. |
| `plugin_instance` | string | no | Plugin instance identifier. Default: "default" |
| `fqc_ids` | string[] | no | Document IDs to clear. Empty array or omitted = query mode (list pending items without deleting). Non-empty = clear matching rows, then return what remains. |

**Returns:** The current list of pending review items for the plugin (after clearing, if any). Each item includes:
- `fqc_id` — the document's UUID (use with `get_document` to read content)
- `table_name` — which plugin table the auto-tracked row lives in (e.g., `'contacts'`)
- `review_type` — why this item was queued: `'template_available'`, `'new_document'`, `'resurrected'`, or `'custom'`
- `context` — JSONB metadata for the skill to act on (e.g., `{ "template": "contact_note.md", "type_id": "crm-contacts" }`)

**When items are queued (automatically by FlashQuery during reconciliation):**
- `on_added: auto-track` fires and the `documents.types` entry declares a `template` → `review_type: 'template_available'`
- `on_added: auto-track` fires with no template but the plugin opts into new-document review → `review_type: 'new_document'`
- An archived plugin row is resurrected (document reappeared in vault) → `review_type: 'resurrected'`

Pending items are also surfaced **passively** in every record tool response — so an in-conversation skill can see them too. But `clear_pending_reviews` is the dedicated entry point for scheduled skills that don't need to make a real record tool call just to check for work.

**Expected calling pattern for a scheduled skill:**

```
Step 1 — Query what's pending:
clear_pending_reviews({ plugin_id: "crm", fqc_ids: [] })
→ returns list of items with fqc_id, table_name, review_type, context

Step 2 — Process each item:
  - get_document({ identifier: item.fqc_id }) to read content
  - Apply template, classify, enrich, route, or take "no action needed"
  - Use move_document, update_document, apply_tags, etc. as needed

Step 3 — Clear what was processed:
clear_pending_reviews({ plugin_id: "crm", fqc_ids: [processed_id_1, processed_id_2, ...] })
→ returns remaining pending items (if any)

Step 4 — If items remain, the next scheduled invocation picks them up (incremental batching)
```

"No action needed" is a valid reason to clear — if a document doesn't need processing, clear it anyway so it doesn't pile up.

**Example — query what's pending for a plugin:**
```
mcp__flashquery__clear_pending_reviews({
  plugin_id: "crm"
})
```

**Example — clear processed items and confirm what remains:**
```
mcp__flashquery__clear_pending_reviews({
  plugin_id: "crm",
  fqc_ids: ["a1b2c3d4-...", "e5f6g7h8-..."]
})
```

**Usage notes:**
- Clearing an `fqc_id` that doesn't exist in the queue is a silent no-op — safe to pass all processed IDs.
- The response shape is always the current pending list, regardless of whether you're querying or clearing.
- Clearing with the full list of IDs you processed and getting back an empty list confirms all work is done.
