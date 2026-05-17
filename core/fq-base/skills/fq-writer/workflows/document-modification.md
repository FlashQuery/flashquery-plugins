# Document Modification Workflow

Use this workflow when the user wants to change an existing document — adding content, updating the body, changing tags, modifying metadata, inserting links, or archiving.

## Decision tree

```
What kind of change does the user want?
  ├── Add a new section / append content → insert_in_doc
  ├── Replace or rewrite the body → write_document(mode: "update")
  ├── Change tags only → apply_tags
  ├── Change other frontmatter (custom fields, title) → write_document(mode: "update")
  ├── Add a link between documents → insert_doc_link
  └── Archive / retire the document → archive_document
```

---

## Appending content

**Tool:** `insert_in_doc`

Use when the user wants to add a section, log entry, or block of content to an existing document **without replacing what's already there**.

1. Identify the document (use `fq_id`, path, or filename — prefer `fq_id` or full path to avoid ambiguity).
2. If you're not sure of the document's structure, call `get_document` with `include: ["frontmatter", "headings"]` first to understand headings before appending.
3. Call `insert_in_doc`:
   - `identifier` — the document
   - `position` — `"bottom"` for whole-document append, or `"end_of_section"` with `heading` when appending inside a section
   - `content` — the full markdown to append, including any headings (e.g., `"## New Section\n\nBody text here."`)
   - `heading`, `occurrence`, `heading_match`, `heading_level`, and `include_nested` — optional section placement controls

**When to read headings first:** If the user says "add a section after X" or "continue the existing notes," call `get_document` with `include: ["frontmatter", "headings"]` to understand where things sit before writing the appended content.

---

## Replacing/rewriting the body

**Tool:** `write_document`

Use when the user wants to replace the document's body entirely, or change both body and metadata together.

1. If you need to see the current content first (to preserve parts of it), call `get_document` to read it.
2. Call `write_document`:
   - `mode` — `"update"`
   - `identifier` — the document
   - `content` — the new body (omit to leave body unchanged)
   - `title` — new title (omit to preserve existing)
   - `tags` — **replaces the entire tag list**; use `apply_tags` instead for incremental changes
   - `frontmatter` — additional fields to merge in; use `null` to delete a custom field. FlashQuery rejects managed frontmatter fields.

**Important:** `write_document(mode: "update")` re-embeds the document after body, title, tag, or frontmatter changes. For incremental tag changes, prefer `apply_tags`.

**Untracked file recovery:** If the tool reports that the document has no `fq_id`/FlashQuery frontmatter metadata, call `get_document` first (which auto-provisions the metadata), then retry.

---

## Changing tags

**Tool:** `apply_tags`

Use for any incremental tag add/remove. This is the preferred tool for tag mutations — it handles validation, normalization, and conflict detection.

1. Call `apply_tags`:
   - `identifiers` — the document(s); can be a single identifier or an array for batch operations
   - `add_tags` — tags to add (idempotent — adding an existing tag is safe)
   - `remove_tags` — tags to remove (silent no-op if not present)

**Status tag conventions:** FlashQuery no longer enforces one `#status/*` tag; it only rejects duplicate tags after normalization. If this workflow treats status as single-valued, pass the old status in `remove_tags` and the new one in `add_tags` in the same call.

**Batch tagging:** To tag many documents at once, pass an array of identifiers to `identifiers`. All documents get the same add/remove applied. (For large batch operations based on a search, use fq-organizer instead.)

---

## Changing frontmatter metadata

**Tool:** `write_document`

Use when the user wants to change non-tag frontmatter fields (custom fields like `client`, `project`, `due-date`, etc.) without replacing the body.

1. Call `write_document`:
   - `mode` — `"update"`
   - `identifier` — the document
   - `frontmatter` — a map of custom fields to set; pass `null` as a value to delete a custom field

**Note:** Do not include `tags` or managed FlashQuery data in `frontmatter`; use the top-level `tags` replacement field or `apply_tags` for tag changes.

---

## Linking documents

**Tool:** `insert_doc_link`

Use when the user wants to create a relationship between two existing documents.

1. Call `insert_doc_link`:
   - `identifiers` — the source document or documents (the ones that get the link added)
   - `target_identifier` — the document to link to
   - `property` — optional; defaults to `"links"`; use `"related"`, `"parent"`, `"child"`, etc. for specific relationship types

The tool resolves both identifiers and adds a `[[Target Title]]` wikilink to the source's frontmatter. Duplicate links are silently ignored.

---

## Archiving documents

**Tool:** `archive_document`

Use when the user wants to retire one or more documents. Archived documents are excluded from search results but remain on disk.

1. Call `archive_document`:
   - `identifiers` — accepts a single string identifier or an array. In the writer workflow you're almost always archiving one document at a time, so pass a single string.

Single-document form (the common case here):
```
archive_document(identifiers: "clients/acme/pricing-old.md")
```

Batch form (used from fq-organizer sweeps, shown for completeness):
```
archive_document(identifiers: ["path1.md", "path2.md"])
```

The tool updates both the vault frontmatter and the database. It's idempotent — archiving an already-archived document is safe. For large-scale archive sweeps based on search criteria, use fq-organizer.

---

## Example patterns

**"Add the pricing section to the proposal doc"**
→ `get_document` with `include: ["frontmatter", "headings"]` (understand structure) → `insert_in_doc(position: "bottom", content: "## Pricing\n\n...")`

**"Update the Acme meeting notes with what we just discussed"**
→ `get_document` (read current content) → `write_document(mode: "update")` (with revised/extended body) OR `insert_in_doc` (if it's an additive update)

**"Tag all the Q1 deliverables as complete"**
→ For a single doc: `apply_tags` (add: `#status/complete`, remove: `#status/draft`)
→ For bulk: use fq-organizer

**"Archive the old pricing brief"**
→ `archive_document` (identifiers: "clients/acme/pricing-brief.md")

**"Set the client field on the proposal to 'Acme'"**
→ `write_document(mode: "update", frontmatter: { client: "Acme" })`
