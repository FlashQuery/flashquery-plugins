# Vault Maintenance Workflow

Use this workflow for operational hygiene on the vault: reconciling the database after bulk file moves outside the chat, emptying folders, duplicating docs as starting points, moving or renaming with identity preserved, and re-indexing when the scanner falls behind.

These tools all preserve data in one way or another — moves keep the fqc_id, copies keep the source untouched, maintenance repair reconciles document state, and `manage_directory(action: "remove")` refuses to clear anything non-empty. The skill's job is to choose the right tool for the user's intent and relay the critical warnings the tools emit.

## When to use

- "I moved a bunch of files in Finder — can you resync the database?"
- "Rename `inbox/acme-notes.md` to `clients/acme/notes.md`"
- "Make a copy of this proposal for the Beta client"
- "Delete the empty `archive/2024-old-projects` folder"
- "I just added files outside the chat — can the system see them?"

## When NOT to use

- Bulk tag changes → [Bulk Tagging](bulk-tagging.md)
- Archive sweeps based on search criteria → [Archive Sweep](archive-sweep.md)
- Single-document body edits → fq-writer workflows
- Creating a brand-new document → fq-writer's document-creation workflow

---

## Tool overview

| Tool | Purpose | Preserves fqc_id? |
|------|---------|-------------------|
| `move_document` | Rename/relocate a document | Yes — identity preserved |
| `copy_document` | Duplicate a document as a starting point | No — copy gets a new fqc_id |
| `manage_directory` | Create directories or safely remove **empty** directories | n/a |
| `maintain_vault` | Sync external file changes, repair tracked document state, or inspect background jobs | Yes — maintenance preserves document identity where possible |

---

## `move_document` — rename or relocate while preserving identity

Use to rename a document, move it to a new directory, or both — without changing its `fqc_id`, history, or plugin associations. Intermediate directories are created automatically.

```
move_document(
  identifier: "inbox/note.md",              // required
  destination: "clients/acme/notes.md"      // required — vault-relative path, including filename
)
```

### Key behaviors to relay to the user

- **Identity is preserved.** fqc_id, creation date, tags, and all custom frontmatter carry over.
- **Wikilinks in other documents are NOT auto-updated.** If another file has `[[Old Title]]` pointing at the moved document, that link will still resolve by title in most setups but may break if you renamed the title. The tool's response includes a reminder — surface it to the user so they know whether to do a find-and-replace sweep.
- **Plugin-owned documents produce a warning.** If the moved document is owned by a plugin (e.g., a CRM contact doc), the plugin may be hard-wired to look at the old path. The response includes a warning — pass it along so the user can update the plugin's reference.
- **Missing extension is filled in.** If `destination` doesn't include a file extension, the source's extension is used (`"projects/q2/brief"` → `"projects/q2/brief.md"`).

### Examples

**Rename in the same folder:**
```
move_document(
  identifier: "inbox/note.md",
  destination: "inbox/meeting-notes.md"
)
```

**Move from inbox into a client folder:**
```
move_document(
  identifier: "inbox/acme-notes.md",
  destination: "clients/acme/notes.md"
)
```

**Move into a folder that doesn't exist yet (auto-created):**
```
move_document(
  identifier: "inbox/q2-kickoff.md",
  destination: "projects/q2/kickoff.md"
)
```

**Extension inferred from source:**
```
move_document(
  identifier: "inbox/rough-draft",
  destination: "projects/q2/brief"     // → "projects/q2/brief.md"
)
```

---

## `copy_document` — duplicate as a starting point

Use when the user wants to treat an existing document as a template — e.g., "copy the proposal template for the Acme deal." The source is not modified. The copy gets a **new fqc_id**, fresh `created` timestamp, and its own status lifecycle.

```
copy_document(
  identifier: "templates/proposal.md",          // required
  destination: "clients/acme/proposal.md"       // optional — defaults to vault root
)
```

### Key behaviors to relay to the user

- **Metadata is copied immutably.** Title, tags, and all custom frontmatter fields (e.g., `client`, `priority`) are copied as-is from the source. There is no way to customize the copy's metadata at creation time.
- **To change title, tags, custom fields, or body on the copy,** call `write_document(mode: "update")` after copying. Set that expectation with the user up front — they usually want a modified copy, not a carbon copy.
- **Destination defaults to vault root.** Omitting `destination` lands the copy at the vault root, with the filename derived from the source title.

### Examples

**Copy a proposal template into a client folder:**
```
copy_document(
  identifier: "templates/proposal.md",
  destination: "clients/acme/proposal.md"
)
```

**Copy without a destination — lands at vault root:**
```
copy_document(identifier: "templates/contact.md")
```

**Copy then customize the copy's title/tags:**
```
copy_document(identifier: "templates/proposal.md", destination: "clients/beta/proposal.md")
// then:
write_document(mode: "update", identifier: "clients/beta/proposal.md", title: "Beta Proposal", frontmatter: { client: "Beta" })
```

---

## `manage_directory` — create or remove directories in the vault

Creates or removes one or more vault directories. Creation uses recursive `mkdir` semantics, so `manage_directory(action: "create", paths: ["clients/acme/2026"])` creates all three levels in a single call even if none exist yet. Removal is empty-only; non-empty directories return a per-path conflict.

```
manage_directory(action: "create", paths: ["clients/acme/2026"])
```

**Batch creation with a shared root:**
```
manage_directory(action: "create", paths: ["CRM/contacts", "CRM/companies", "CRM/interactions"])
```

### Behavior to relay

- **Idempotent create.** Calling on a directory that already exists succeeds with `status: "unchanged"`, not as an error. No confirmation needed before executing.
- **`paths` is always an array** of vault-relative directory paths. Duplicate paths execute sequentially in input order.
- **Intermediate directories created automatically.** Deep paths like `"a/b/c/d"` create all missing levels.
- **Absolute paths rejected.** Paths starting with `/` are rejected — all paths are vault-relative.
- **Non-destructive create.** Creation cannot destroy data. No confirmation needed before running.

---

## `manage_directory(action: "remove")` — delete an empty directory

Safely removes an empty directory. No recursion, no force. If the directory contains any files or subfolders, the tool errors and lists the contents.

```
manage_directory(action: "remove", paths: ["archive/2024-old-projects"])
```

### Behavior to relay

- **Empty-only.** If the directory isn't empty, the error response shows what's in it — present that to the user and ask whether they want to move/archive the contents first. Don't loop in attempts to force-delete; that isn't supported.
- **Path is vault-relative**, same convention as every other vault path.

---

## `maintain_vault` — sync and repair after external vault changes

Runs administrative maintenance. Use `action: "sync"` to scan external filesystem changes. Use `action: "repair"` to reconcile tracked document state. Use `action: ["repair", "sync"]` when both are needed; repair runs before sync. Use `action: "status"` with `job_id` to inspect a background sync job.

```
maintain_vault(action: ["repair", "sync"])
maintain_vault(action: "repair", dry_run: true)
maintain_vault(action: "sync", background: true)
maintain_vault(action: "status", job_id: "...")
```

### When to run

- The user moved/renamed files outside the chat and wants the system to catch up.
- Semantic search starts returning stale paths or "file not found" errors on docs that clearly still exist.
- After a git pull that rearranged the vault.

### Recommended pattern

For repair, use `dry_run: true` first when the user is worried about changes. Present the proposed changes and confirm before running without `dry_run`.

### Combined maintenance

```
maintain_vault(action: ["repair", "sync"], dry_run: false)
```

---

## `maintain_vault(action: "sync")` — manually trigger the scanner

Re-indexes the vault. Useful when the user added files outside the chat and wants them visible immediately, or as a recovery step before reconciliation.

```
maintain_vault(action: "sync")                      // synchronous; waits for the scan to complete
maintain_vault(action: "sync", background: true)    // background job; returns job metadata
```

### Response format

- **Synchronous sync** returns a structured JSON maintenance payload.
- **Background sync** returns job metadata; inspect it later with `maintain_vault(action: "status", job_id: "...")`.
- Do not expect low-level scanner internals such as queue depth, hashes, or per-document sync versions in the response.

Pick synchronous when the user is about to do a search or browse that depends on the scan; background when the user is mid-conversation and the scan is a behind-the-scenes nicety.

---

## Confirm-before-executing

Most of these operations are reversible in principle but annoying in practice. Before running anything that moves, copies, removes, or reconciles in bulk, show the user what's about to happen:

- For `move_document` / `copy_document` — name the source and destination, and mention any warnings the tool will emit (wikilinks, plugin ownership).
- For `maintain_vault(action: "repair")` — run `dry_run: true` first when repair could be surprising and show the proposed changes.
- For `manage_directory(action: "remove")` — confirm the directory is empty and name the path.

## Error handling

- **Write lock timeout** — retry once after 3 seconds; if persistent, pause and tell the user something else is writing to the vault.
- **Destination already exists** (move/copy) — the tool errors rather than clobbering. Ask the user whether to pick a new name, archive the existing file first, or abort.
- **`manage_directory(action: "remove")` on a non-empty directory** — surface the conflict and ask the user whether to move/archive the contents first.
- **`maintain_vault(action: "repair")` reports missing files** — explain the proposed repair before applying it and give the user the option to restore files from backup first if any of them were deleted accidentally.
