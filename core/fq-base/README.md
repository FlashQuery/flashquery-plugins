---
version: 1.0.0
---

# fq-base

Core FlashQuery skills for writing, finding, and organizing vault documents and memories, plus vault maintenance slash commands.

This plugin provides the foundational AI workflows for day-to-day use of FlashQuery. Install it alongside any FlashQuery instance to give Claude the tool sequences it needs to work with your vault naturally.

---

## Skills

Skills are auto-invoked by Claude based on what you say. You don't call them directly.

### fq-writer
**Triggers on:** "write this up," "create a document about," "draft a note on," "add a section to," "log this under Interactions," "rewrite the Pricing section," "remember that," "save this for later," "update that memory," "forget that," and similar phrases.

Orchestrates document creation, modification, and memory management:
- Creates new vault documents with appropriate tags, optional linking, and custom frontmatter
- Modifies existing documents (append content, update body, change tags, update metadata)
- Section-scoped edits: insert at a specific heading/position (`insert_in_doc`) or replace a specific section (`replace_doc_section`)
- Saves, updates, and archives memories

### fq-finder
**Triggers on:** "find documents about," "what do we know about," "show me the notes from," "give me a briefing on," "what did I save about," "pull up that memory about," and similar phrases.

Orchestrates search and retrieval across your vault:
- Unified search across documents and memories (`search_all`)
- Document-focused search with tag/keyword/semantic modes
- File and directory browsing by folder path and recency (`list_vault`)
- Memory recall (semantic search + tag browsing)
- Briefings: structured overview of a topic using tags

### fq-organizer
**Triggers on:** "clean up," "organize," "archive old documents," "bulk tag," "tag everything in this project as," "archive anything older than," and similar phrases.

Orchestrates bulk operations and vault maintenance with a confirm-before-execute workflow:
- Bulk tagging of documents matching search criteria
- Archive sweeps (find candidates → show → confirm → archive)
- Bulk memory cleanup
- Vault maintenance: move/rename documents, copy docs as starting points, remove empty directories, reconcile the database after external file changes, force file scans

---

## Commands

Commands are slash commands you invoke explicitly.

| Command | Description |
|---------|-------------|
| `/fq-base:vault-scan` | Scan the vault to discover new, moved, and deleted files. Accepts optional `background` argument. |
| `/fq-base:reconcile` | Reconcile the database against the filesystem — fixes stale paths, archives truly missing files. Accepts optional `dry-run` argument. |
| `/fq-base:vault-health` | Full health check: scan + reconcile + hygiene audit in one comprehensive report. |

### When to use each

**`/fq-base:vault-scan`** — after importing files into your vault outside the conversation. Walks the filesystem to update the database.

**`/fq-base:reconcile`** — after moving or deleting files outside FlashQuery. Walks the database to verify each file still exists, fixes moved paths, and permanently archives truly deleted files.

**`/fq-base:vault-health`** — periodic maintenance or when something feels off. Runs both of the above plus a hygiene audit in one go.

---

## MCP Tools Required

This plugin's skills call the following FlashQuery MCP tools. Your FlashQuery instance must be running and connected for this plugin to work:

**Document tools:** `create_document`, `get_document`, `update_document`, `archive_document`, `search_documents`, `move_document`, `copy_document`, `reconcile_documents`

**Compound document tools:** `append_to_doc`, `insert_in_doc`, `replace_doc_section`, `update_doc_header`, `insert_doc_link`, `apply_tags`, `get_doc_outline`, `get_briefing`, `list_vault`, `search_all`

**Directory tools:** `create_directory`, `remove_directory`

**Memory tools:** `save_memory`, `search_memory`, `update_memory`, `get_memory`, `list_memories`, `archive_memory`

**Maintenance tools:** `force_file_scan`

---

## Plugin Composition

`fq-base` is designed to be the foundation layer. Plugin-specific skills (like `fq-crm`) can delegate to these core skills for vault and memory operations, then layer their own record tool orchestration on top.

For example, an `fq-crm` skill that needs to create a contact note would use `fq-writer`'s document creation logic, then use its own plugin-specific record tools to link the plugin record.
