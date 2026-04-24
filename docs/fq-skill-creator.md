# FQ-Skill-Creator

**Version:** 2.0.0 · **Category:** Core · **Author:** FlashQuery

Meta-skill for creating new Claude skills that use FlashQuery MCP tools for document storage, search, memory, and data management.

---

## Overview

FQ-Skill-Creator is a developer-facing plugin. When you need to build a new skill that stores documents in the vault, manages memories, or works with structured database records, this plugin gives your Claude assistant a complete reference for all 35 FlashQuery MCP tools — so the resulting skill calls the right tools with the right parameters.

Think of it as the "teach Claude how to write FlashQuery-powered skills" plugin. You describe what your skill needs to do, and Claude uses this reference to generate properly structured SKILL.md files with correct tool calls, error handling, and FlashQuery conventions baked in.

## Prerequisites

- **FlashQuery** MCP server installed and connected
- **Claude Code** (CLI) or **Cowork** (desktop)
- Familiarity with the FlashQuery plugin structure (see [Building Your Own Plugin](../README.md#building-your-own-plugin) in the root README)

## Installation

First, make sure you've added the FlashQuery marketplace to Claude Code (one-time step — see [Getting Started](../README.md#getting-started) in the root README):

```
/plugin marketplace add https://github.com/FlashQuery/flashquery-plugins
```

Then install the plugin:

```
/plugin install fq-skill-creator@flashquery-plugins
```

No initialization step is required.

---

## Skills & Workflows

### creator (fq-skill-creator) — Build FlashQuery-powered skills

**When Claude activates this skill:** "create a FlashQuery skill," "make a skill that stores data," "build a skill with document management," "I need a skill that remembers things," "make a skill that saves stuff to the vault," "I want a skill that can look things up"

**What it handles:**

The skill walks through a four-step process:

**Step 1: Understand requirements.** Claude asks clarifying questions to determine what the skill does, when it should trigger, what kind of data it needs (documents, memories, structured records, or a mix), and what search patterns matter. A key question: does the skill need to automatically discover and process files dropped into vault folders outside of conversation? If so, the skill needs a pull-based processing loop.

**Step 2: Identify the right FlashQuery tools.** Based on the requirements, Claude maps data needs to tools:

- Long-form content (notes, reports, logs) → Document tools (`create_document`, `get_document`, `update_document`, `search_documents`)
- Facts, preferences, observations across sessions → Memory tools (`save_memory`, `search_memory`, `update_memory`)
- Structured data with custom fields (contacts, tasks, inventory) → Record tools with a plugin schema (`register_plugin`, `create_record`, `search_records`)
- Search across everything at once → `search_all`
- Organization (tagging, linking, archiving) → Compound tools (`apply_tags`, `insert_doc_link`, `archive_document`)
- Watch vault folders for new files → Pull-based processing with `clear_pending_reviews`

**Step 3: Write the skill.** Claude generates a SKILL.md file with the correct tool surface, parameter shapes, error handling (write lock recovery, missing file handling, tag conflict resolution), and FlashQuery conventions (using `fqc_id` over paths, checking `isError` on every response, handling semantic search latency).

**Step 4: Hand off.** The drafted skill is ready for testing and iteration, potentially using a skill-creator workflow.

---

## Bundled Reference

The plugin bundles a comprehensive reference covering all 35 active FlashQuery MCP tools, organized into seven categories:

**Document tools (9):** Create, read, update, archive, search, copy, move, list files, and remove directories in the vault.

**Section and metadata editing (6):** Append to documents, insert at specific positions, replace named sections, update frontmatter, apply tags, and insert wikilinks — precision editing tools that change one part without touching the rest.

**Memory tools (6):** Save, search, list, get, update, and archive semantic memories that persist across conversations.

**Record tools (5):** Create, get, update, archive, and search structured records in plugin-registered database tables.

**Plugin management (3):** Register plugin schemas (creating database tables), get plugin info, and unregister plugins.

**Cross-resource tools (3):** Search across documents and memories simultaneously, get tag-scoped briefings, and get document outlines without reading full content.

**Vault maintenance (3):** Force file scans, reconcile database against filesystem, and manage pending review queues.

The reference also includes a detailed guide to the `documents.types` schema for plugins that need to watch vault folders and automatically track new files — covering `on_added`, `on_moved`, `on_modified` policies, field mapping, and the pull-based processing architecture.

---

## Key Conventions

When building FlashQuery-powered skills, the reference enforces several conventions:

**Use `fqc_id` (UUID), not file paths.** Paths change when users move files; UUIDs are stable. Parse `fqc_id` from `create_document` responses and store it for later reference.

**Check `isError` on every tool response.** FlashQuery tools return structured responses. Always check for errors before proceeding.

**Write lock recovery.** If a tool returns a write lock error, retry once after a brief pause. If it fails again, tell the user.

**Section editing over full rewrites.** Prefer `replace_doc_section` or `insert_in_doc` over `update_document` when modifying part of a document. Targeted edits preserve surrounding content and avoid unnecessary re-embedding.

**Semantic search latency.** Documents just created may not appear in semantic search immediately because embedding is asynchronous. This is normal and expected.

**Tag conventions.** Status tags use `#status/*` prefix. Only one status tag per document. Use `apply_tags` with `add_tags`/`remove_tags` for incremental changes.

---

## How It Fits Into the Plugin Development Workflow

1. **Design your skills** — figure out what your plugin needs to do
2. **Write the skills** — use FQ-Skill-Creator if your skills use FlashQuery tools
3. **Bundle into a plugin** — use the [Plugin Creator](./plugin-creator-skill.md) standalone skill to assemble everything into a `.plugin` file
4. **Distribute** — publish to a marketplace or share the file directly
