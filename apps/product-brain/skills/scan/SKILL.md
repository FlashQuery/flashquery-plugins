---
name: scan
description: >
  Use this skill when the user wants to pick up documents added to the vault
  outside of a conversation — files dropped into project folders from Finder,
  a terminal, or another tool. Trigger on "scan for new files", "check for new
  documents", "pick up files I added", "process pending documents", "I dropped
  some files in", or any indication the user has added files to the vault
  manually and wants them registered. Also trigger on a periodic /loop schedule
  to ensure externally-added documents are always picked up and processed.
  This skill updates FlashQuery's file index, triggers the reconciliation engine,
  and processes any auto-tracked documents that need project attribution and
  template application.
---

# Scan

Picks up documents added to the vault outside of a conversation and completes
their registration in the Product Brain database. FlashQuery's reconciler
auto-tracks new files mechanically — this skill handles the follow-up work
that requires judgment: inferring project ownership from the file path,
determining document type from the folder, and applying the correct template
structure.

Designed to run periodically via `/loop` or on demand when the user mentions
dropping files into the vault.

## Steps

### 1. Update the file index

Call `force_file_scan` to update FlashQuery's document index with any files
added, moved, or deleted outside the conversation:

```
mcp__flashquery__force_file_scan({})
```

This ensures `fqc_documents` reflects the current state of the vault before
reconciliation runs.

### 2. Trigger reconciliation

Call `search_records` to trigger the reconciliation engine. This is a cheap
call whose side effect is running the reconciler, which auto-tracks any new
files found in the plugin's declared folders:

```
mcp__flashquery__search_records({
  plugin_id: "product-brain",
  table: "documents",
  filters: { status: "active" },
  limit: 1
})
```

Note any reconciliation summary in the tool response — it may mention newly
auto-tracked documents. The tool response will also indicate if pending review
items exist.

### 3. Retrieve configuration

Call `search_memory` to get the vault root and project list:

```
mcp__flashquery__search_memory({
  query: "product-brain-config",
  tags: ["product-brain-config"]
})
```

Then call `search_records` on `projects` to get all active projects with their
`project_path` and record IDs:

```
mcp__flashquery__search_records({
  plugin_id: "product-brain",
  table: "projects",
  filters: { status: "active" }
})
```

Keep this list — you'll use it to infer `project_id` from file paths.

### 4. Query pending review items

Call `clear_pending_reviews` with an empty `fqc_ids` array to see what's pending:

```
mcp__flashquery__clear_pending_reviews({
  plugin_id: "product-brain",
  fqc_ids: []
})
```

If nothing is pending, tell the user the vault is up to date and stop here.

### 5. Process each pending item

For each item in the pending list, perform the following steps. Track the
`fqc_id` of each item you successfully process — you'll clear them in bulk
at the end.

#### 5a. Inspect the document

Call `get_doc_outline` to read the document's frontmatter and structure without
loading the full body:

```
mcp__flashquery__get_doc_outline({
  identifiers: "<fqc_id>"
})
```

This gives you the document's path, current frontmatter fields, and section
headings.

#### 5b. Infer project_id from path

Match the document's path against the active projects list from step 3. Find
the project whose `project_path` is a prefix of the document path.

Example: a document at `product-brain/flashquery/research/my-note.md` matches
the project with `project_path: "product-brain/flashquery/"`.

If no project matches (the file is outside all known project folders), note it
in the summary as "unrouted" and skip updating `project_id`. The user will
need to move it or create the appropriate project first.

#### 5c. Determine document type

Check the document's frontmatter for a `type` field (e.g., `type: spark`).
If present, use it.

If the `type` field is absent, infer from the folder segment:
- `.../inbox/...` → `spark`
- `.../research/...` → `research_note`
- `.../specs/...` → `feature_spec`
- `.../work/...` → `work_item`
- `_plugin/templates/...` → use the `document_type` field if present, otherwise `custom`

For documents in a templates folder, also set `is_base: false` (user-defined
template, not a base template shipped with the plugin).

#### 5d. Check for open questions (research notes only)

For documents whose type is `research_note`, read the Open Questions section:

```
mcp__flashquery__get_document({
  identifier: "<fqc_id>",
  sections: ["Open Questions"]
})
```

Set `has_open_questions: true` if the section has non-placeholder content;
`false` if it's empty or only contains the template placeholder.

#### 5e. Apply template structure (if needed)

Check `item.review_type` to decide whether to apply a template:

- **`template_available`** — The watched folder has a declared template. FlashQuery
  has signaled that this document needs template application. Proceed with the
  template lookup below, preserving any content already written.
- **`new_document`** or **`resurrected`** — No template hint was declared for this
  folder. Apply a template only if the document body is blank or minimal (no headings,
  placeholder content only).

For all cases where template application is warranted, look up the template by the
inferred document type from step 5c:

```
mcp__flashquery__search_records({
  plugin_id: "product-brain",
  table: "templates",
  filters: { document_type: "<inferred_type>" }
})
```

Read the template via `get_document`, then apply its structure to the document
via `update_document` (full body replace) or `insert_in_doc` for targeted
section insertion, preserving any content the user has already written.

If the document already has headings and content, skip template application —
do not overwrite the user's work.

#### 5f. Update the database record

For document-type pending items, find the existing `prodbrain_documents` record
via `search_records` with `filters: { fqc_id: "<fqc_id>" }`, then call
`update_record` with the inferred fields:

```
mcp__flashquery__update_record({
  plugin_id: "product-brain",
  table: "documents",
  id: "<record_id>",
  fields: {
    project_id: "<inferred project UUID>",
    document_type: "<inferred type>",
    status: "<from frontmatter, or 'active' if absent>",
    has_open_questions: <true|false>
  }
})
```

For template-type pending items, update the `prodbrain_templates` record:

```
mcp__flashquery__update_record({
  plugin_id: "product-brain",
  table: "templates",
  id: "<record_id>",
  fields: {
    document_type: "<inferred type>",
    is_base: false,
    updated_at: "<current ISO timestamp>"
  }
})
```

### 6. Clear processed items

Call `clear_pending_reviews` with the `fqc_ids` of all successfully processed
documents to remove them from the pending queue:

```
mcp__flashquery__clear_pending_reviews({
  plugin_id: "product-brain",
  fqc_ids: ["<fqc_id_1>", "<fqc_id_2>", ...]
})
```

The response confirms the current pending count. If items remain (e.g., ones
you skipped due to unrouted paths), they'll persist for the next run.

### 7. Report

Tell the user:
- How many files were newly auto-tracked
- How many pending items were processed (documents registered, templates registered)
- Any items that couldn't be routed (files outside known project folders) — give
  the path and suggest either creating a project for them or moving them into
  an existing project folder

Keep it brief. The user wants confirmation, not a breakdown of every file.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- This skill is designed for periodic use via `/loop`. A reasonable cadence is
  every 30–60 minutes when actively using the vault, or on-demand when the user
  mentions adding files.
- If `force_file_scan` reports no new, updated, or moved files AND
  `clear_pending_reviews` returns nothing pending, the run is a no-op —
  confirm the vault is up to date and exit.
- Documents the user drops without a `type` frontmatter field are handled
  gracefully via folder-based inference. The scan skill does not reject them.
- Template application is best-effort. If a document already has structured
  content, the skill preserves it rather than overwriting. The user can always
  ask Capture to enrich a document after the fact.
- The Review Loop already calls `force_file_scan` at the start of its run.
  Running Scan and Review Loop together is fine — the file scan is idempotent.
