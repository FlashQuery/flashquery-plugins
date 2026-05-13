# File Browse Workflow

Use this workflow when the user wants to browse vault files and folders by path — the "what's in this folder" or "what changed recently" type of question. It's the natural complement to `search`: filesystem-shaped navigation rather than content-shaped discovery.

## When to use

- "What's in the clients folder?"
- "Show me what's in `clients/acme`"
- "What's changed in the last week?"
- "What did I add to `inbox` yesterday?"
- Inventorying a subtree by date window rather than by topic
- Sanity-checking that a newly saved file is actually present

## When NOT to use

- Content-based discovery ("find notes about X") → [Document Search](document-search.md)
- Reading the structure of a specific file (frontmatter and headings) → `get_document` with `include: ["frontmatter", "headings"]`
- Cross-type search spanning documents + memories → [Unified Search](unified-search.md)
- Browsing plugin records → out of scope for fq-base; use the plugin's own skill

## Tool: `list_vault`

```
list_vault(
  path: "clients/acme",          // optional — vault-relative directory; default "/" (vault root)
  show: "all",                   // optional — "files", "directories", or "all" (default)
  include: ["tracking"],          // optional — "metadata" for directory details, "tracking" for tracked document data
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
- **`include`** (string[], optional, default `[]`) — optional payload sections. `"metadata"` adds directory created/children data. `"tracking"` adds tracked document title, tags, status, and fq_id.
- **`recursive`** (boolean, optional, default `false`) — when `true`, walks the entire subtree under `path`. Leave off for a flat listing of just the immediate children.
- **`extensions`** (string[], optional) — case-insensitive filter on file extension (e.g., `[".md", ".txt"]`). **This is an array, not a string.** All file types are supported (not just `.md`). Ignored when `show` is `"directories"`.
- **`after`** (string, optional) — include entries modified/created on or after this moment. Accepts relative formats (`"7d"`, `"24h"`, `"1w"`) or ISO (`"2026-04-01"`, `"2026-04-01T15:30:00Z"`).
- **`before`** (string, optional) — include entries modified/created on or before this moment. Both relative and ISO formats work.
- **`date_field`** (string, optional, default `"updated"`) — which timestamp `after`/`before` filter against: `"updated"` (default) or `"created"`. Use `"created"` to filter by when a file was first added to the vault.
- **`limit`** (integer, optional, default `200`) — maximum number of entries to return. A truncation notice is appended if results exceed the limit.

### Response format

`list_vault` returns a structured JSON envelope with `path`, `total`, `displayed`, `truncated`, and `entries`. Entries contain filesystem data, and include-gated tracking data when requested. Untracked files appear with filesystem metadata only.

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

**"Show recent markdown files across the whole vault with tracking metadata"**
```
list_vault(
  path: "",
  recursive: true,
  extensions: [".md"],
  after: "7d",
  include: ["tracking"]
)
```

## When results look suspiciously empty

If the folder should contain files the user just added outside the chat, the scanner may not have picked them up yet. Run `maintain_vault(action: "sync")` to reindex, then retry `list_vault`. Pass `background: true` if the user doesn't need inline sync results, then inspect later with `maintain_vault(action: "status", job_id: "...")`.

```
maintain_vault(action: "sync")
maintain_vault(action: "sync", background: true)
```

See [vault-maintenance](../../fq-organizer/workflows/vault-maintenance.md) in fq-organizer for the fuller picture of when scanning fits into a session.

## Synthesis guidance

`list_vault` returns a filesystem view. When presenting results:

1. **Group by subfolder** if `recursive: true` returned a wide tree — readable summaries beat flat lists once there are more than ~15 files.
2. **Lead with dates** if the user asked a recency question — put the `updated` timestamp up front.
3. **Offer a drill-in.** After showing what's in a folder, a natural next step is "want me to read any of these?" — answer via `get_document`, using `include: ["frontmatter", "headings"]` when structure is enough.
4. **Choose include data wisely.** Use `include: ["tracking"]` when you need `fq_id`, tags, or status for a follow-up tool call (e.g., `apply_tags`, `get_document` by UUID, `write_record`). Omit includes for a compact filesystem browse.
