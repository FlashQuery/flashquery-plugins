---
name: creator
description: Create new Claude skills that use FlashQuery MCP tools for document storage, search, memory, and data management. Use this skill whenever the user wants to create a skill that needs to save documents, search files, store memories, manage records, or interact with a FlashQuery vault in any way. Also trigger when the user says "create a FlashQuery skill", "make a skill that stores data", "build a skill with document management", "I need a skill that remembers things", "create an FQ skill", or wants to build any skill where the resulting skill should persist data, search content, or manage structured records through FlashQuery. Even casual mentions like "make a skill that saves stuff to the vault" or "I want a skill that can look things up" should trigger this skill.
---

# fq-skill-creator

A meta-skill for creating Claude skills that leverage FlashQuery MCP tools. When you need to build a skill that stores documents, searches content, manages memories, or works with structured records, this skill gives you everything you need to wire up FlashQuery tools correctly in the resulting skill.

## How this works

This skill wraps the standard `/skill-creator` workflow. The difference: when the skill being built needs to persist data, search content, manage memories, or work with structured records, it should use FlashQuery MCP tools instead of raw file I/O or ad-hoc storage. This skill provides the complete FlashQuery tool reference so the resulting skill's instructions can call the right tools with the right parameters.

## Workflow

### Step 1: Understand the skill requirements

Before writing anything, clarify with the user:

1. What the skill does and when it should trigger
2. What kind of data the skill needs to work with — documents, memories, structured records, or a mix
3. Whether the skill needs its own plugin schema (structured records with custom tables) or can use the core document and memory tools directly
4. What search patterns matter — keyword, semantic, tag-filtered, cross-resource
5. **Does the skill need to automatically discover and process files dropped into vault folders outside of a conversation?** If yes, the skill needs a `documents.types` entry with `on_added: auto-track` in its plugin schema, and a pull-based processing loop using `clear_pending_reviews` on a schedule. This is a distinct architecture from skills that only respond to in-conversation requests.

### Step 2: Identify which FlashQuery tools the skill needs

Map the skill's data requirements to FlashQuery tools using this decision guide:

**The skill needs to save/retrieve long-form content (notes, reports, logs, articles)?**
Use Document tools: `create_document`, `get_document`, `update_document`, `search_documents`, `list_vault`

**The skill needs to remember facts, preferences, or observations across sessions?**
Use Memory tools: `save_memory`, `search_memory`, `list_memories`, `update_memory`

**The skill needs structured data with custom fields (contacts, tasks, inventory, etc.)?**
Use Record tools with a plugin schema: `register_plugin`, `create_record`, `get_record`, `update_record`, `search_records`

**The skill needs to search across everything at once?**
Use `search_all` for unified document + memory search

**The skill needs to organize content (tagging, linking, archiving)?**
Use Compound tools: `apply_tags`, `insert_doc_link`, `archive_document`, `archive_memory`

**The skill needs to create vault directories for organizing output documents?**
Use `create_directory` — it accepts a single path string or an array of paths, creates intermediate directories automatically (`mkdir -p`), and is idempotent (calling on an existing directory succeeds without error).

**The skill needs to watch vault folders for new files and process them periodically (template application, classification, routing)?**
Use `clear_pending_reviews` on a `/loop` or scheduled cron. Set up the plugin schema with `documents.types` entries and `on_added: auto-track` so FlashQuery auto-discovers files mechanically. The skill then queries the pending review queue, processes each item, and clears it. See "Building a pull-based document processing skill" below, and read [references/example-pull-processor.md](references/example-pull-processor.md) for a complete annotated schema YAML and skill composition guide.

### Step 3: Write the skill using the FlashQuery tool reference

Read the full tool reference at [references/flashquery-tools.md](references/flashquery-tools.md) to get exact parameter names, types, and return values for every tool the skill needs.

When writing the skill body (the SKILL.md for the new skill), include:

1. **Tool surface** — list which `mcp__flashquery__*` tools the skill uses and why
2. **Tool call patterns** — show the exact parameter shapes for common operations so the model using the skill doesn't have to guess
3. **Error handling** — include recovery patterns for common failures (write locks, missing files, tag conflicts)
4. **Conventions** — always prefer `fqc_id` over paths for document references; parse `fqc_id` from `create_document` responses

### Step 4: Delegate to the skill-creator

Once you've drafted the skill with FlashQuery tools wired in, use the standard `/skill-creator` workflow for testing, evaluation, and iteration. The skill-creator handles the test harness, eval viewer, benchmarking, and description optimization — this skill handles the FlashQuery-specific content.

## Key conventions for FlashQuery-powered skills

These conventions should be embedded in any skill that uses FlashQuery tools:

1. **Use `fqc_id` (UUID), not file paths** — paths change when users move files; UUIDs are stable. After `create_document`, parse the `fqc_id` from the response and store it for later reference.

2. **Check `isError` on every tool response** — FlashQuery tools return structured responses. Always check for errors before proceeding.

3. **Write lock recovery** — if a tool returns a write lock error, retry once after a brief pause. If it fails again, tell the user.

4. **Tag conventions** — status tags use the `#status/*` prefix (e.g., `#status/draft`, `#status/published`). Only one status tag per document. Use `apply_tags` with `add_tags`/`remove_tags` for incremental changes. `apply_tags` also supports tagging memories via `memory_id` and batch-tagging multiple documents via array `identifiers`.

5. **Semantic search latency** — documents just created may not appear in semantic search immediately because embedding is asynchronous. This is normal behavior.

6. **Plugin registration for structured data** — if the skill needs custom tables (beyond documents and memories), it must register a plugin schema first via `register_plugin`. Define the schema in YAML and include it in the skill's bundled resources.

7. **Section editing over full rewrites** — when modifying part of a document, prefer `replace_doc_section` or `insert_in_doc` over `update_document`. Targeted edits preserve surrounding content and avoid unnecessary re-embedding.

## FlashQuery tool reference (summary)

The complete reference with all parameters and return values is in [references/flashquery-tools.md](references/flashquery-tools.md). Here's a quick overview organized by category:

### Document tools
| Tool | Purpose |
|------|---------|
| `create_document` | Create a new markdown document in the vault |
| `get_document` | Read document content by path, fqc_id, or filename (supports section extraction) |
| `update_document` | Overwrite document body and/or frontmatter (full body replace) |
| `archive_document` | Soft-delete one or more documents (accepts single or array) |
| `search_documents` | Search by keyword, semantic similarity, or tags |
| `copy_document` | Duplicate a document to a new destination |
| `move_document` | Move or rename a document to a new vault path |
| `list_vault` | Browse vault files and directories by path with filtering by extension, date, and type |

### Section and metadata editing tools
| Tool | Purpose |
|------|---------|
| `append_to_doc` | Append content to end of document |
| `insert_in_doc` | Insert content at a specific position (top, bottom, after/before heading, end of section) |
| `replace_doc_section` | Replace content of a named section |
| `update_doc_header` | Update frontmatter fields without touching body |
| `apply_tags` | Add or remove tags on documents or memories (supports batch) |
| `insert_doc_link` | Add a wiki-style link to another document in frontmatter |

### Memory tools
| Tool | Purpose |
|------|---------|
| `save_memory` | Store a persistent fact or observation |
| `search_memory` | Search memories by semantic similarity |
| `list_memories` | List memories with optional tag filtering (no query needed) |
| `get_memory` | Retrieve one or more memories by ID (supports batch) |
| `update_memory` | Create a new version of an existing memory |
| `archive_memory` | Soft-delete a memory |

### Record tools (for plugin-registered tables)
| Tool | Purpose |
|------|---------|
| `register_plugin` | Register or update a plugin schema (creates tables) |
| `get_plugin_info` | Get schema and table details for a plugin |
| `unregister_plugin` | Remove a plugin and its database resources |
| `create_record` | Create a new record in a plugin table |
| `get_record` | Retrieve a single record by ID |
| `update_record` | Update specific fields on a record |
| `archive_record` | Soft-delete a record |
| `search_records` | Search records by keyword or semantic similarity |

### Cross-resource tools
| Tool | Purpose |
|------|---------|
| `search_all` | Search documents and memories simultaneously (supports entity_types filter) |
| `get_briefing` | Get tag-scoped overview of documents, memories, and optionally plugin records |
| `get_doc_outline` | Get document structure and frontmatter without full body (supports batch) |

### Vault maintenance tools
| Tool | Purpose |
|------|---------|
| `force_file_scan` | Trigger vault scan for new/moved/deleted files |
| `reconcile_documents` | Fix database/filesystem inconsistencies |
| `create_directory` | Create one or more directories in the vault (mkdir -p, idempotent) |
| `remove_directory` | Remove an empty directory from the vault |
| `clear_pending_reviews` | Query or clear pending review items |

## Example: What a FlashQuery-powered skill looks like

Here's a simplified example of how a skill body references FlashQuery tools. This shows the pattern — your actual skill will have more detail:

```markdown
## What this skill owns

- Creating and retrieving client intake documents
- Searching across existing intake records
- Saving follow-up reminders as memories

Tool surface: `create_document`, `get_document`, `search_documents`,
`apply_tags`, `save_memory`, `search_memory`

## Creating an intake document

Call `mcp__flashquery__create_document` with:
- `title`: "Intake: {client name} - {date}"
- `content`: the formatted intake notes (markdown)
- `path`: "clients/{client-slug}/intake.md"
- `tags`: ["#type/intake", "#status/new"]

Parse `fqc_id` from the response and use it for all subsequent references.

## Searching past intakes

Call `mcp__flashquery__search_documents` with:
- `query`: the user's search terms
- `tags`: ["#type/intake"]
- `mode`: "mixed" (combines keyword + semantic)
- `limit`: 10

Follow up on high-confidence results with `get_document` to pull full content.

## Saving a follow-up reminder

Call `mcp__flashquery__save_memory` with:
- `content`: "Follow up with {client} about {topic} by {date}"
- `tags`: ["follow-up", "client-intake"]
```

## When the skill needs a plugin schema

If the skill manages structured records (not just documents and memories), it needs a plugin schema. Here's the pattern:

1. Define the schema as YAML — include it in the skill's `references/` or `assets/` directory
2. The skill body should instruct the model to call `register_plugin` with either `schema_path` or `schema_yaml` on first use
3. After registration, the skill uses `create_record`, `get_record`, `update_record`, `search_records`, and `archive_record` with the `plugin_id` and `table` name

### Basic schema (records only)

For a plugin that manages structured records without watching folders:

```yaml
id: my-skill-plugin
name: My Skill Plugin
version: "1.0"

tables:
  - name: entries
    description: Main data entries
    embed_fields:
      - name
      - category
      - notes
    columns:
      - name: name
        type: text
        required: true
        description: Entry name
      - name: category
        type: text
        description: Entry category
      - name: notes
        type: text
        description: Additional notes
```

### Schema with document tracking (documents.types)

If the skill also watches vault folders and needs to track documents automatically, add a `documents.types` section alongside `tables`. This enables the **reconcile-on-read** pattern: FlashQuery discovers new files in declared folders and handles data integrity mechanically, while the skill processes pending items via `clear_pending_reviews`.

**Single-folder example:**

```yaml
id: my-skill-plugin
name: My Skill Plugin
version: "1.0"

documents:
  types:
    - id: my-plugin-items
      folder: MyPlugin/Items          # vault-relative folder to watch
      access: read-write              # read-write (default) or read-only
      on_added: auto-track            # auto-track or ignore (default)
      track_as: items                 # which plugin table to create a row in
      template: item_template.md      # optional: template filename for Claude to apply
      field_map:                      # frontmatter field → plugin table column
        title: name
        tags: tags
      on_moved: keep-tracking         # keep-tracking (default) or untrack
      on_modified: sync-fields        # sync-fields or ignore (default)

tables:
  - name: items
    embed_fields:
      - name
    columns:
      - name: name
        type: text
        required: true
        description: Item name (mapped from document title)
      - name: fqc_id
        type: uuid
        required: true
        description: Reference to the associated fqc_documents row
      - name: last_seen_updated_at
        type: timestamptz
        description: When reconciliation last saw this document (used for modified detection)
      - name: tags
        type: text
        description: Tags synced from document frontmatter
```

**Multi-folder example** (different folders routing to different tables — the common CRM-style pattern):

```yaml
id: crm
name: CRM Plugin
version: "1.0"

documents:
  types:
    - id: crm-contacts
      folder: CRM/Contacts
      on_added: auto-track
      track_as: contacts              # new files here → contacts table
      template: contact_note.md
      field_map:
        title: name
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields

    - id: crm-companies
      folder: CRM/Companies
      on_added: auto-track
      track_as: companies             # new files here → companies table
      template: company_profile.md
      field_map:
        title: name
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields

    - id: crm-inbox
      folder: CRM/Inbox
      on_added: auto-track
      track_as: inbox_items           # new files here → inbox_items table
      field_map:
        title: name
      on_moved: untrack               # if moved out of inbox, it was dealt with
      on_modified: ignore

tables:
  - name: contacts
    embed_fields: [name]
    columns:
      - name: name
        type: text
        required: true
      - name: fqc_id
        type: uuid
        required: true
      - name: last_seen_updated_at
        type: timestamptz
      - name: tags
        type: text

  - name: companies
    embed_fields: [name]
    columns:
      - name: name
        type: text
        required: true
      - name: fqc_id
        type: uuid
        required: true
      - name: last_seen_updated_at
        type: timestamptz

  - name: inbox_items
    columns:
      - name: name
        type: text
        required: true
      - name: fqc_id
        type: uuid
        required: true
```

The reconciler routes new files to the right table based on which folder they land in. A file moved between watched folders (e.g., from `CRM/Inbox` to `CRM/Contacts`) will untrack from `inbox_items` (per `on_moved: untrack`) and auto-track into `contacts` on the next reconciliation.

### documents.types policy reference

| Field | Values | Description |
|-------|--------|-------------|
| `id` | string | Unique type identifier (e.g., `crm-contacts`). Used in `fqc_type` frontmatter and the global type registry. |
| `folder` | string | Vault-relative folder path to watch (e.g., `CRM/Contacts`). The folder implies intent — once a document is associated, frontmatter (`fqc_owner`/`fqc_type`) is the source of truth, not the folder. |
| `access` | `read-write` (default), `read-only` | Whether the plugin intends to modify documents in this folder. `read-only` causes a warning if the skill tries to write. Does not affect mechanical FQC operations (frontmatter writes during auto-track are always permitted). |
| `on_added` | `ignore` (default), `auto-track` | What happens when a genuinely new file appears in the folder (no existing plugin row for its `fqc_id`). `auto-track`: FlashQuery creates the plugin table row, writes `fqc_owner`/`fqc_type` to the document's frontmatter, populates columns via `field_map`, and inserts a pending review row if `template` is declared. Requires `track_as`. `ignore`: file is visible in `fqc_documents` but the plugin doesn't track it. |
| `track_as` | plugin table name | Which plugin table to insert into when auto-tracking. Must match a `tables` entry. Required when `on_added: auto-track`. |
| `template` | filename string | A template hint for the plugin's skill. FlashQuery stores this as metadata and surfaces it in pending review rows (`review_type: 'template_available'`, `context.template` contains this filename). The skill (not FlashQuery) reads, applies, and merges the template with the document. The template file's location is entirely the skill's domain — put it in the skill's `references/` or `assets/` directory and reference it by path in the skill instructions. FlashQuery never reads the template file; it only stores the name as a routing hint. Optional. |
| `field_map` | object (frontmatter key → column name) | Maps frontmatter fields to plugin table columns. Applied during auto-track (initial population), sync-fields (on modification), and resurrection (re-sync after return). If a mapped field is absent from the document, the column is set to NULL. |
| `on_moved` | `keep-tracking` (default), `untrack` | What happens when a tracked document moves outside this folder (frontmatter association still intact). `keep-tracking`: update the stored path, keep tracking. `untrack` (also `stop-tracking`): archive the plugin row (resurrectable later). Note: `ignore` is not a valid value — both options produce a stable end state so the reconciler converges. |
| `on_modified` | `ignore` (default), `sync-fields` | What happens when a tracked document's `updated_at` or content hash changes. `sync-fields`: re-read frontmatter, re-apply `field_map`, update `last_seen_updated_at`. `ignore`: only updates `last_seen_updated_at` (prevents re-flagging on every cycle). |

**Always-mechanical responses** (no policy field needed — FlashQuery always handles these):
- `deleted`: document is `missing` or `archived` → plugin row is archived
- `disassociated`: user removed `fqc_owner`/`fqc_type` from frontmatter → plugin row is archived
- `resurrected`: archived plugin row's document came back to `active` → row is un-archived, path updated, `field_map` re-applied (template never re-applied)

### Key schema rules
- `tables` is an array of objects (`- name: ...`), not a map
- `columns` is an array of objects (`- name: ...`), not a map
- Column `type` must be one of: `text`, `integer`, `boolean`, `uuid`, `timestamptz`
- Use `embed_fields` (array of column names) at the table level to enable semantic search — there is no separate `search:` block
- Plugin metadata (`id`, `name`, `version`) can be at root level or nested under `plugin:`
- FlashQuery automatically adds `id`, `instance_id`, `status`, `created_at`, `updated_at` to every plugin table — do not redefine these
- Document-tracking tables should include `fqc_id` (uuid) as a foreign key to `fqc_documents`, and `last_seen_updated_at` (timestamptz) for modification detection

## Building a pull-based document processing skill

When a skill needs to watch folders and process new files (apply templates, classify documents, route to the right location), use the pull-based pattern rather than push callbacks:

**Architecture overview:**

1. The plugin schema declares `documents.types` entries with `on_added: auto-track`
2. The user drops a file into a watched folder (outside any conversation)
3. A **scanner run** (`force_file_scan`) picks up the file and registers it in `fqc_documents`
4. A **record tool call** (any of: `search_records`, `create_record`, `get_record`, `update_record`, `archive_record`) triggers `reconcilePluginDocuments()` internally — this detects the new `fqc_documents` entry, auto-tracks it (creates the plugin row, writes `fqc_owner`/`fqc_type` frontmatter), and inserts a pending review row into `fqc_pending_plugin_review`
5. The skill (running on `/loop` or scheduled cron) calls `clear_pending_reviews` to read the queue, processes each item (applies template, classifies, routes), then clears the processed IDs

**Critical dependency:** `clear_pending_reviews` reads the `fqc_pending_plugin_review` table but does **not** itself trigger a vault scan or reconciliation. Pending items only appear in that table after steps 3 and 4 have both run. A scheduled skill that calls `clear_pending_reviews` cold (without first scanning and reconciling) will find nothing if no in-conversation record tool call happened between the file drop and the scheduled run. The fix: always call `force_file_scan` and then a record tool before querying pending reviews.

This is the replacement for the old `on_document_discovered` push callback pattern. Data integrity (row creation, frontmatter writes, field sync) is always mechanical. The skill only handles the AI-requiring tasks: template application, content classification, and routing decisions.

**Also: frontmatter-based discovery.** If a file is dropped into a *non-watched* folder but its YAML frontmatter includes `fqc_type: my-plugin-items`, FlashQuery's reconciler will still auto-track it — it looks up the type in the global type registry and applies the matching policy. The skill instructions can mention this as a fallback for users who want to pre-declare types in their documents.

**Typical skill structure for a pull-based processor:**

```markdown
## Processing pending documents

This skill runs on a schedule (via /loop or cron). On each invocation:

1. Sync the vault — call `force_file_scan({})` to pick up any files dropped since the last run.

2. Trigger reconciliation — call `search_records({ plugin_id: "my-plugin", table: "items" })`
   with a minimal query (limit: 1 is fine). This causes FlashQuery to diff the watched folders
   against fqc_documents, auto-track any new files, and insert pending review rows.
   The response will also surface any pending items inline.

3. Query the pending queue — call `clear_pending_reviews({ plugin_id: "my-plugin", fqc_ids: [] })`.
   If the response lists no pending items, do nothing and exit.

4. For each pending item (process in batches of 5–10):
   - Call `get_document({ identifier: item.fqc_id })` to read the document content
   - Check `item.review_type`:
     - `template_available`: load the template from `item.context.template`
       (find it in the skill's references/ or assets/ directory), merge it with the
       document's existing content, write back with `update_document`
     - `new_document`: classify and route the document — move to appropriate folder,
       apply tags, update plugin record fields via `update_record`
     - `resurrected`: verify the document is still valid, update any stale fields
   - If no action is needed (document already structured), clear it anyway

5. Clear processed items — call `clear_pending_reviews({ plugin_id: "my-plugin", fqc_ids: [processed_ids] })`
   to remove them from the queue and confirm what remains.

6. If items remain, the next scheduled invocation picks them up (incremental batching).
```

**When to use `/loop` vs scheduled cron:**
- Use `/loop` during development and testing — triggers on demand within a session
- Use a scheduled cron (via `/schedule`) for production — runs even when no conversation is active, which is the key advantage of pull-based processing over push callbacks

**Pending review items are also surfaced passively:** Every time a record tool is called for the plugin, the response includes a "Pending review" note. An in-conversation skill can therefore act on pending items immediately, without a separate processing loop — step 2 above doubles as the reconcile-and-surface call. The `/loop` or cron is only needed when processing should happen independently of user-initiated conversations.

## Completing the workflow

After drafting the skill with FlashQuery tools integrated, hand off to the `/skill-creator` for the standard test-evaluate-iterate loop. The skill-creator will:

1. Run test cases against the skill
2. Generate the eval viewer for human review
3. Run quantitative benchmarks
4. Iterate based on feedback
5. Optimize the description for triggering accuracy
6. Package the final skill

Your job here is to make sure the FlashQuery tool usage in the skill body is correct, complete, and follows the conventions above. The skill-creator handles everything else.
