# File Browse Workflow

Use this workflow when the user wants to browse vault files and folders by path — the "what's in this folder" or "what changed recently" type of question. It's the natural complement to `search_documents`: filesystem-shaped navigation rather than content-shaped discovery.

## When to use

- "What's in the clients folder?"
- "Show me what's in `clients/acme`"
- "What's changed in the last week?"
- "What did I add to `inbox` yesterday?"
- Inventorying a subtree by date window rather than by topic
- Sanity-checking that a newly saved file is actually present

## When NOT to use

- Content-based discovery ("find notes about X") → [Document Search](document-search.md)
- Reading the structure of a specific file (headings, links) → `get_doc_outline`
- Cross-type search spanning documents + memories → [Unified Search](unified-search.md)
- Browsing plugin records → out of scope for fq-base; use the plugin's own skill

## Tool: `list_vault`

```
list_vault(
  path: "clients/acme",          // optional — vault-relative directory; default "/" (vault root)
  show: "all",                   // optional — "files", "directories", or "all" (default)
  format: "table",               // optional — "table" (default, compact) or "detailed" (key-value blocks)
  recursive: true,               // optional; default false — walk the entire subtree
  extensions: [".md"],           // optional — array; case-insensitive; all file types supported
  after: "7d",                   // optional — modified/created ≥ this; relative ("7d", "24h", "1w") or ISO
  before: "2026-04-15",          // optional — modified/created ≤ this; relative or ISO
  date_field: "updated",         // optional — "updated" (default) or "created"
  limit: 200                     // optional — max entries returned; default 200
)
```

### Parameters in detail

- **`path`** (string, optional, default `"/"`) — vault-relative directory to list. Examples: `"clients/acme"`, `"inbox"`, `"projects/q2"`. Omit or pass `""` / `"."` to list the vault root.
- **`show`** (string, optional, default `"all"`) — what to include: `"files"` (files only), `"directories"` (directories only), or `"all"` (both). When `"directories"`, the `extensions` filter is silently ignored.
- **`format`** (string, optional, default `"table"`) — output format. `"table"` produces a compact markdown table; `"detailed"` produces key-value blocks separated by `---`, including title, tags, and fqc_id for tracked files.
- **`recursive`** (boolean, optional, default `false`) — when `true`, walks the entire subtree under `path`. Leave off for a flat listing of just the immediate children.
- **`extensions`** (string[], optional) — case-insensitive filter on file extension (e.g., `[".md", ".txt"]`). **This is an array, not a string.** All file types are supported (not just `.md`). Ignored when `show` is `"directories"`.
- **`after`** (string, optional) — include entries modified/created on or after this moment. Accepts relative formats (`"7d"`, `"24h"`, `"1w"`) or ISO (`"2026-04-01"`, `"2026-04-01T15:30:00Z"`).
- **`before`** (string, optional) — include entries modified/created on or before this moment. Both relative and ISO formats work.
- **`date_field`** (string, optional, default `"updated"`) — which timestamp `after`/`before` filter against: `"updated"` (default) or `"created"`. Use `"created"` to filter by when a file was first added to the vault.
- **`limit`** (integer, optional, default `200`) — maximum number of entries to return. A truncation notice is appended if results exceed the limit.

### Response formats

**`format: "table"` (default)** — a compact markdown table with Name, Type, Size, Modified, and (for tracked files) fqc_id columns. Good for presenting vault contents to users.

**`format: "detailed"`** — one key-value block per entry, blocks separated by `---`. Includes title, tags, fqc_id, size, and both created and updated timestamps for tracked files. Use this when you need fqc_id or tags for follow-up tool calls.

Both formats end with a summary line: `Showing {N} of {total} entries in {path}/.`

Untracked files (not in fqc_documents) appear with filesystem metadata only — no title, tags, or fqc_id. Both formats note this with an "untracked" marker.

## Examples

**"What's in the Acme folder?"**
```
list_vault(path: "clients/acme")
```

**"Show me everything under clients/acme, all subfolders included"**
```
list_vault(path: "clients/acme", recursive: true)
```

**"What did I add to the inbox in the last week?"**
```
list_vault(path: "inbox", after: "7d")
```

**"What was added to projects/q2 between April 1 and April 15?"**
```
list_vault(
  path: "projects/q2",
  after: "2026-04-01",
  before: "2026-04-15",
  date_field: "created"
)
```

**"Show me only the subdirectories under projects"**
```
list_vault(path: "projects", show: "directories")
```

**"Show recent markdown files across the whole vault with full metadata"**
```
list_vault(
  path: "",
  recursive: true,
  extensions: [".md"],
  after: "7d",
  format: "detailed"
)
```

## When results look suspiciously empty

If the folder should contain files the user just added outside the chat, the scanner may not have picked them up yet. Run `force_file_scan()` to reindex, then retry `list_vault`. Pass `background: true` if the user doesn't need to see the scan summary inline — results appear in server logs.

```
force_file_scan()          // synchronous; returns { status: "complete", new_files, updated_files, moved_files, deleted_files, status_mismatches }
force_file_scan(background: true)   // fire-and-forget; returns immediately
```

See [vault-maintenance](../../fq-organizer/workflows/vault-maintenance.md) in fq-organizer for the fuller picture of when scanning fits into a session.

## Synthesis guidance

`list_vault` returns a filesystem view. When presenting results:

1. **Group by subfolder** if `recursive: true` returned a wide tree — readable summaries beat flat lists once there are more than ~15 files.
2. **Lead with dates** if the user asked a recency question — put the `updated` timestamp up front.
3. **Offer a drill-in.** After showing what's in a folder, a natural next step is "want me to read any of these?" — answer via `get_document` or `get_doc_outline`.
4. **Choose format wisely.** Use `format: "detailed"` when you need `fqc_id` or tags for a follow-up tool call (e.g., `apply_tags`, `get_document` by UUID, `update_record`). Use `format: "table"` (default) when presenting results to the user — it's more readable.
