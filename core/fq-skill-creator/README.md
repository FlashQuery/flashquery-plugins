---
version: 1.0.0
---

# fq-skill-creator

A meta-skill for creating Claude skills that use FlashQuery MCP tools for document storage, search, memory, and data management.

When you need to build a skill that persists data, searches content, manages memories, or works with structured records, this plugin provides the complete FlashQuery tool reference and wiring guidance so the resulting skill calls the right tools with the right parameters.

---

## Skills

Skills are auto-invoked by Claude based on what you say. You don't call them directly.

### fq-skill-creator
**Triggers on:** "create a FlashQuery skill," "make a skill that stores data," "build a skill with document management," "I need a skill that remembers things," "make a skill that saves stuff to the vault," "I want a skill that can look things up," and similar phrases.

Guides skill creation with FlashQuery integration:
- Maps skill data requirements to the appropriate FlashQuery tool categories (documents, memories, records, cross-resource)
- Provides a complete MCP tool reference with exact parameter names, types, required/optional flags, and usage examples
- Documents key conventions for FlashQuery-powered skills (fqc_id usage, error handling, tag patterns, section editing)
- Covers plugin schema registration for skills that need custom structured data tables
- Delegates to the standard `/skill-creator` for the test-evaluate-iterate workflow

### Bundled reference

The skill includes `references/flashquery-tools.md` — a comprehensive reference covering all 35 active FlashQuery MCP tools organized by category:

- **Document tools** (9): create, get, update, archive, search, copy, move, list, remove_directory
- **Section and metadata editing** (6): append, insert, replace section, update header, apply tags, insert link
- **Memory tools** (6): save, search, list, get, update, archive
- **Record tools** (5): create, get, update, archive, search
- **Plugin management** (3): register, get info, unregister
- **Cross-resource tools** (3): search all, get briefing, get doc outline
- **Vault maintenance** (3): force file scan, reconcile, clear pending reviews

Each tool entry includes parameter tables, return value descriptions, concrete usage examples, and notes on common pitfalls.

---

## How it works

This plugin wraps the standard `/skill-creator` workflow. When the skill being built needs to persist or retrieve data, it references FlashQuery MCP tools instead of raw file I/O. The workflow is:

1. Understand skill requirements and data needs
2. Identify which FlashQuery tools the skill needs (using the decision guide)
3. Write the skill body with FlashQuery tool calls wired in correctly
4. Hand off to `/skill-creator` for testing, evaluation, and iteration

---

## MCP Tools Referenced

This plugin documents (but does not directly call) all FlashQuery MCP tools. The skills it helps create will call these tools. Your FlashQuery instance must be running and connected for the resulting skills to work.

---

## Plugin Composition

`fq-skill-creator` works alongside `fq-base`. While `fq-base` provides the day-to-day skills for working with vault documents and memories, `fq-skill-creator` provides the tooling knowledge needed to build new skills that use FlashQuery as their data layer.
