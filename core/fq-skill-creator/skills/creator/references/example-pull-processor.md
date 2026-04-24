# Example: Pull-Based Document Processing Plugin

This file shows how to assemble a FlashQuery plugin that watches vault folders
and processes documents dropped in from outside a conversation. Use it as a
concrete reference when writing a new plugin's schema YAML and skills.

The example plugin is a **Research Notes** tracker — it watches an inbox folder,
auto-tracks dropped files, classifies each one as a `research_note` or
`reference_doc`, applies the appropriate template, and routes it to the right
subfolder. The pattern applies to any plugin that needs to discover and act on
documents the user drops in independently.

---

## Part 1: Schema YAML — Complete Annotated Reference

Every field is shown with inline comments explaining its purpose, valid values,
and defaults. In a real plugin you'd remove the comments and trim to only the
fields you need.

```yaml
# ── Plugin identity ─────────────────────────────────────────────────────────
# All three fields are required. version must be a quoted string.
id: research-notes                   # Unique plugin identifier — used as plugin_id in all MCP calls
name: Research Notes                 # Display name shown in get_plugin_info responses
version: "1.0"                       # Semantic version; bumping minor/patch triggers safe additive migration
description: >                       # Optional. Human-readable purpose statement.
  Tracks research notes and reference documents dropped into the vault.
  Classifies, templates, and routes them to the right project folder.

# ── Document Types (folder watching + reconciliation policies) ───────────────
# documents.types declares which vault folders this plugin watches and what
# FlashQuery should do mechanically when files appear, move, or change.
#
# Each entry in the types array is one watched folder with its own policies.
# A plugin can watch any number of folders — add one entry per folder.
#
# IMPORTANT: "Folders discover, frontmatter remembers."
# The folder is only how a file is *first* associated. Once FlashQuery writes
# fqc_owner and fqc_type into the file's frontmatter, the frontmatter is the
# source of truth for the association — even if the file later moves.

documents:
  types:

    # ── Inbox: catch-all staging area ───────────────────────────────────────
    - id: research-inbox             # Required. Unique type ID. Becomes the fqc_type written to frontmatter.
                                     # Also used as the key in the global type registry for frontmatter-based discovery.
      folder: Research/Inbox         # Required. Vault-relative path (no leading slash).
                                     # All files in this folder (not subfolders) are candidates.
      description: "Incoming files for classification"  # Optional. Documentation only.

      access: read-write             # Optional. Default: read-write.
                                     # read-write: plugin may modify documents in this folder.
                                     # read-only: FlashQuery warns if the skill tries to write.
                                     # NOTE: auto-track's frontmatter writes (fqc_owner, fqc_type)
                                     # are always permitted regardless of access level.

      on_added: auto-track           # What to do when a genuinely new file lands here.
                                     # "New" means no plugin row (active or archived) for this fqc_id.
                                     # auto-track: FlashQuery creates a row in `track_as` table,
                                     #   writes fqc_owner/fqc_type to frontmatter, populates field_map
                                     #   columns, and inserts a fqc_pending_plugin_review row if
                                     #   `template` is declared.
                                     # ignore (default): file is in fqc_documents but plugin ignores it.
                                     #   Use for passively monitored folders or folders where the skill
                                     #   decides explicitly which files to track via create_record.

      track_as: inbox_items          # Required when on_added: auto-track.
                                     # Must match a table name in the tables: section below.
                                     # This is the short name (e.g., "inbox_items"), not the full
                                     # DB table name (fqcp_research-notes_default_inbox_items).

      template: inbox_triage.md      # Optional. Filename of a template for this document type.
                                     # When provided, FlashQuery inserts a fqc_pending_plugin_review
                                     # row with review_type: 'template_available' and
                                     # context: { template: "inbox_triage.md", type_id: "research-inbox" }.
                                     # FlashQuery never reads or applies the template — it stores the
                                     # filename as a routing hint. The skill reads the template from
                                     # wherever the skill says it lives (typically references/ or assets/).

      field_map:                     # Optional. Maps frontmatter fields → plugin table columns.
        title: name                  # frontmatter key: plugin table column name
        tags: tags                   # Applied during auto-track, sync-fields, and resurrection.
                                     # If a frontmatter field is absent, the column is set to NULL.

      on_moved: untrack              # What to do when a tracked document moves outside this folder.
                                     # keep-tracking (default): update stored path, keep tracking.
                                     #   Use when the relationship matters more than location
                                     #   (e.g., a contact is still a contact wherever the file lives).
                                     # untrack (alias: stop-tracking): archive the plugin row.
                                     #   Resurrectable later if the file returns or is re-discovered.
                                     #   Use for staging areas where moving out means "dealt with".
                                     # NOTE: 'ignore' is NOT valid here. Both options produce a
                                     # stable end state; ignore would leave a stale path forever.

      on_modified: ignore            # What to do when the document's updated_at or content_hash
                                     # differs from the plugin row's last_seen_updated_at.
                                     # ignore (default): note the change but take no action.
                                     #   Still updates last_seen_updated_at so the same modification
                                     #   isn't re-flagged every reconciliation cycle.
                                     # sync-fields: re-read frontmatter, re-apply field_map,
                                     #   update last_seen_updated_at. Pure metadata sync —
                                     #   FlashQuery does not read document body content.

    # ── Research Notes: final destination ───────────────────────────────────
    - id: research-notes-docs
      folder: Research/Notes
      access: read-write
      on_added: auto-track           # Files dropped directly here (bypassing inbox) also auto-track
      track_as: documents
      template: research_note.md
      field_map:
        title: name
        tags: tags
        type: document_type          # Frontmatter `type` field → document_type column
        status: status
      on_moved: keep-tracking
      on_modified: sync-fields

    # ── References: read-only monitoring ────────────────────────────────────
    - id: research-refs
      folder: Research/References
      access: read-only              # Plugin reads but does not write to documents here
      on_added: ignore               # Don't auto-track — skill decides which refs to register explicitly
      on_moved: keep-tracking        # If a tracked reference moves, follow it
      on_modified: ignore

    # ── Internal plugin folders ──────────────────────────────────────────────
    # _plugin/ is the conventional prefix for plugin-internal vault folders.
    # These store templates and feedback that the plugin manages itself.
    - id: research-templates
      folder: _plugin/research-notes/templates
      access: read-write
      on_added: auto-track
      track_as: templates
      field_map:
        title: name
        type: document_type
      on_moved: keep-tracking
      on_modified: sync-fields


# ── Tables ───────────────────────────────────────────────────────────────────
# Define the database tables created when the plugin is registered.
# FlashQuery automatically adds these columns to every table — do NOT define them:
#   id (uuid PK), instance_id (text), status (text default 'active'),
#   created_at (timestamptz), updated_at (timestamptz)
#
# For document-tracking tables, always include:
#   fqc_id (uuid) — stable foreign key to fqc_documents
#   last_seen_updated_at (timestamptz) — enables efficient modified detection

tables:
  - name: inbox_items
    description: "Staging area for unclassified dropped files"
    # embed_fields: omitted — no semantic search needed on inbox items
    columns:
      - name: name
        type: text                   # Column types: text | integer | boolean | uuid | timestamptz
        required: true
        description: "Document title from frontmatter"
      - name: fqc_id
        type: uuid
        required: true
        description: "Stable reference to the fqc_documents row"
      - name: tags
        type: text
        description: "Tags from frontmatter, comma-separated"
      - name: last_seen_updated_at
        type: timestamptz
        description: "fqc_documents.updated_at at last reconciliation — used for modified detection"

  - name: documents
    description: "Classified research notes and reference documents"
    embed_fields:                    # Columns whose values are combined into a vector embedding.
      - name                         # Enables semantic search via search_records.
      - document_type                # List column names (not objects). Embedding is computed
      - tags                         # automatically — do NOT define an `embedding` column.
    columns:
      - name: name
        type: text
        required: true
      - name: fqc_id
        type: uuid
        required: true
      - name: document_type
        type: text
        description: "research_note or reference_doc — populated during pending review processing"
      - name: status
        type: text
        description: "active, archived — from frontmatter status field"
      - name: tags
        type: text
      - name: last_seen_updated_at
        type: timestamptz

  - name: templates
    description: "Template registry — one row per template file in the vault"
    embed_fields:
      - name
    columns:
      - name: name
        type: text
        required: true
      - name: fqc_id
        type: uuid
        required: true
      - name: document_type
        type: text
        description: "Which document type this template produces"
      - name: is_base
        type: boolean
        description: "True if shipped with the plugin; false if user-created"


# ── Memory ────────────────────────────────────────────────────────────────────
# Optional. Declares semantic categories for plugin-scoped memories.
# scope: plugin means memories are namespaced to this plugin_id.
# scope: global means memories go into the shared global namespace.

memory:
  scope: plugin
  categories:
    - name: plugin_config
      description: >
        User preferences for how this plugin operates — vault folder choices,
        default document types, processing preferences.
    - name: research_context
      description: >
        Ambient research intelligence — recurring themes, open questions,
        priorities that surface during conversations but don't belong in a document.
```

---

## Part 2: Plugin Skill Composition

A plugin that uses pull-based discovery typically needs these skills:

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `initialize-plugin` | Registers schema, creates vault folders, seeds templates | User runs `/initialize` or mentions setup |
| `document-processor` | The scheduled pull loop: scan → reconcile → process pending | `/loop` or scheduled cron |
| `search` / `query` | User-facing search across classified documents | User asks to find/recall research |
| `add-document` | In-conversation document creation (bypass inbox) | User asks to save/capture something |

The `document-processor` is the only skill driven by a schedule. All others are user-initiated.

---

## Part 3: Initialize Plugin Skill Pattern

The initialization skill registers the schema and creates the vault folder structure. It runs once (or when the user wants to re-initialize or migrate).

```markdown
## What this skill does

1. Register the plugin schema:
   Call `register_plugin({ schema_path: "references/schema.yaml" })`
   (or `schema_yaml` with inline content).
   On first run this creates all tables. On re-run with the same version it is a no-op.
   On re-run with a bumped version it applies safe additive migrations.

2. Create vault folder structure:
   Call `create_document` for placeholder files (or just note the folders) so
   the vault directories exist. FlashQuery creates the folder when a document
   is written there.

3. Confirm with get_plugin_info:
   Call `get_plugin_info({ plugin_id: "research-notes" })` and show the user
   what was created.

## On first run only

Seed base templates into `_plugin/research-notes/templates/`:
- Create `research_note.md` using `create_document`
- Create `inbox_triage.md` using `create_document`
These are auto-tracked into the `templates` table (on_added: auto-track on the
`_plugin/research-notes/templates` folder entry).
```

---

## Part 4: Document Processor Skill Pattern

This is the scheduled skill. The full invocation sequence on every run:

```markdown
## Document Processor

Runs on a schedule (via /loop or cron). On each invocation:

### Step 1 — Sync the vault
Call `force_file_scan({})`.
This picks up any files dropped since the last run. Without this step,
fqc_documents won't know about new files and reconciliation won't find them.

### Step 2 — Trigger reconciliation
Call `search_records({ plugin_id: "research-notes", table: "inbox_items" })`.
This runs reconcilePluginDocuments() internally, which:
  - Detects new files in watched folders (compares fqc_documents against plugin tables)
  - Auto-tracks them (creates plugin rows, writes fqc_owner/fqc_type to frontmatter)
  - Inserts fqc_pending_plugin_review rows for any that have a template declared
The response includes a "Pending review" summary — use it as a quick check,
but proceed to step 3 for the structured list.

### Step 3 — Query the pending queue
Call `clear_pending_reviews({ plugin_id: "research-notes", fqc_ids: [] })`.
If the response shows no pending items, exit — nothing to do.

### Step 4 — Process pending items (batch of 5–10)

For each item:

**If review_type is 'template_available':**
  - The template filename is in item.context.template
    (e.g., "inbox_triage.md" or "research_note.md")
  - Look up that template's fqc_id via:
    search_records({ plugin_id: "research-notes", table: "templates",
                     filters: { name: item.context.template } })
  - Read the template: get_document({ identifier: template_fqc_id })
  - Read the document: get_document({ identifier: item.fqc_id })
  - Merge: preserve all user content; add template headings and sections
    that are missing. User's existing content takes precedence over template defaults.
  - Write back: update_document({ identifier: item.fqc_id, content: merged_content })

**If review_type is 'new_document' (no template was declared):**
  - Read the document: get_document({ identifier: item.fqc_id })
  - Classify: determine document_type (research_note or reference_doc) from content
  - Route: move_document({ identifier: item.fqc_id,
                            destination: "Research/Notes/{filename}" })
  - Update record: update_record({ plugin_id: "research-notes",
                                   table: "inbox_items",
                                   id: <row id from search_records>,
                                   fields: { document_type: "research_note" } })

**If review_type is 'resurrected':**
  - Document came back after going missing. Fields are already re-synced by FlashQuery.
  - Verify the document is still coherent (spot-check content if needed).
  - No template re-application — the document was already templated on first track
    and may have been edited. Don't overwrite user changes.
  - Clear it.

**If no action is needed** (document is already well-structured, or it's in a state
you don't need to act on): clear it anyway. Uncleared rows persist indefinitely.

### Step 5 — Clear processed items
Call `clear_pending_reviews({ plugin_id: "research-notes",
                               fqc_ids: [list of processed fqc_ids] })`.
The response shows what remains. If non-empty, the next scheduled run picks them up.
```

---

## Part 5: Frontmatter-Based Discovery (Path 2)

Files dropped outside watched folders can still be auto-tracked if their YAML
frontmatter includes `fqc_type: research-inbox` (or any type ID declared in the
schema). FlashQuery looks up the type in the global registry and applies the same
policies as if the file had landed in the declared folder.

This is useful for:
- Files created by other plugins that should also be tracked here
- Files in a shared inbox that multiple plugins watch
- Users who prefer to pre-declare types by editing frontmatter

The skill instructions can mention this as an alternative to dropping files into
the watched folder.

---

## Key things to get right

1. **`force_file_scan` before reconciliation** — a scheduled skill running cold will
   miss files dropped since the last scan unless it calls this first.

2. **Record tool call before `clear_pending_reviews`** — pending review rows are only
   inserted during reconciliation, which only runs inside record tools. `clear_pending_reviews`
   reads the queue but does not trigger reconciliation.

3. **`fqc_id` on every document-tracking table** — the reconciler links plugin rows to
   `fqc_documents` via this column. Without it, the row can't be reconciled.

4. **`last_seen_updated_at` for modification detection** — without this column,
   `on_modified: sync-fields` has nothing to compare against.

5. **Template files live in the skill, not in FlashQuery** — the `template` field in
   the schema YAML is a filename hint. The skill is responsible for finding the file
   (typically via a `templates` table lookup by name, as shown in Step 4).

6. **`untrack` for staging areas, `keep-tracking` for permanent associations** — an
   inbox pattern almost always wants `on_moved: untrack` because moving out of the
   inbox means the file was dealt with. A contact/document pattern wants
   `keep-tracking` because the relationship persists regardless of location.
