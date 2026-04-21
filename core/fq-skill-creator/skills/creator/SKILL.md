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

### Step 2: Identify which FlashQuery tools the skill needs

Map the skill's data requirements to FlashQuery tools using this decision guide:

**The skill needs to save/retrieve long-form content (notes, reports, logs, articles)?**
Use Document tools: `create_document`, `get_document`, `update_document`, `search_documents`, `list_files`

**The skill needs to remember facts, preferences, or observations across sessions?**
Use Memory tools: `save_memory`, `search_memory`, `list_memories`, `update_memory`

**The skill needs structured data with custom fields (contacts, tasks, inventory, etc.)?**
Use Record tools with a plugin schema: `register_plugin`, `create_record`, `get_record`, `update_record`, `search_records`

**The skill needs to search across everything at once?**
Use `search_all` for unified document + memory search

**The skill needs to organize content (tagging, linking, archiving)?**
Use Compound tools: `apply_tags`, `insert_doc_link`, `archive_document`, `archive_memory`

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
| `list_files` | Browse vault files by directory with date/extension filtering |

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

Example YAML schema structure:
```yaml
plugin:
  id: my-skill-plugin
  name: My Skill Plugin
  version: "1.0"

tables:
  entries:
    description: Main data entries
    columns:
      name:
        type: text
        required: true
        description: Entry name
      category:
        type: text
        description: Entry category
      notes:
        type: text
        description: Additional notes
    search:
      enabled: true
      fields: [name, category, notes]
```

## Completing the workflow

After drafting the skill with FlashQuery tools integrated, hand off to the `/skill-creator` for the standard test-evaluate-iterate loop. The skill-creator will:

1. Run test cases against the skill
2. Generate the eval viewer for human review
3. Run quantitative benchmarks
4. Iterate based on feedback
5. Optimize the description for triggering accuracy
6. Package the final skill

Your job here is to make sure the FlashQuery tool usage in the skill body is correct, complete, and follows the conventions above. The skill-creator handles everything else.
