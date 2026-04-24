# FQ-Base

**Version:** 1.0.0 · **Category:** Core · **Author:** FlashQuery

Core skills for writing, finding, and organizing vault documents and memories, plus vault maintenance commands.

---

## Overview

FQ-Base is the foundation layer of the FlashQuery plugin ecosystem. It provides three general-purpose skills — one for creating and editing content, one for searching and retrieving it, and one for bulk organization and maintenance. If you're storing any kind of information in your FlashQuery vault and don't need the specialized workflows of a domain plugin (CRM, Product Brain, etc.), FQ-Base handles the day-to-day reading, writing, and organizing.

All interaction happens through conversation with your Claude assistant. There is no separate application or UI — you describe what you want in natural language, and Claude calls the appropriate FlashQuery tools.

## Prerequisites

- **FlashQuery** MCP server installed and connected to your Claude assistant
- **Claude Code** (CLI) or **Cowork** (desktop) — plugins are managed through Claude

## Installation

```
/plugin install fq-base@flashquery-plugins
```

No initialization step is required. FQ-Base works immediately with FlashQuery's built-in document and memory tools.

---

## Skills & Workflows

### fq-writer — Create and modify documents and memories

The writing skill handles everything that creates or changes content in your vault.

**When Claude activates this skill:** "write this up," "create a document about," "draft a note on," "add a section to," "log this under the Interactions heading," "rewrite the Pricing section," "insert this after the Background heading," "tag this document," "link these two docs," "remember that," "save this for later," "update that memory," "forget that," "jot this down"

**What it handles:**

**Document creation** — Creating new Markdown documents in the vault with frontmatter, tags, and content. Claude generates the document, saves it via FlashQuery, and returns the document's `fqc_id` (a UUID that stays stable even if you rename or move the file).

**Document modification** — Appending content to an existing document, rewriting its body, or updating its frontmatter and tags. Claude picks the right editing approach based on your request: a full body rewrite when you want to overhaul the document, an append when you're adding to the end, or a targeted section edit when you want to change one part without touching the rest.

**Section-scoped editing** — Inserting content at a specific heading or position ("add this after the Background section"), replacing the content of a named section ("rewrite the Pricing section"), or inserting content at the top or bottom of the document. This is the precision tool — it changes exactly the section you specify and leaves everything else intact.

**Tag and link management** — Adding or removing tags on documents, and inserting wikilinks between documents to create cross-references.

**Memory management** — Saving new memories ("remember that Sarah prefers email"), updating existing memories with corrected information, and archiving memories you no longer need ("forget the note about the old pricing").

---

### fq-finder — Search, recall, and surface content

The search skill handles everything that retrieves existing content from your vault or memories.

**When Claude activates this skill:** "find documents about," "what do we know about," "show me the notes from," "give me an overview of," "search for anything related to," "what did I save about," "pull up that memory about," "do I have any notes on," "give me a briefing on," "show me everything on," "what's in this folder," "what changed in the last week"

**What it handles:**

**Unified search** — When you're not sure whether the information you need is in a document or a memory, Claude searches both simultaneously and synthesizes the results into a coherent answer. This is the default behavior when your question is open-ended ("what do we know about the onboarding redesign?").

**Document search** — Targeted search across vault documents using keywords, semantic similarity, or tag filters. Claude can search by content meaning (semantic), by exact terms (keyword), or browse by folder and recency (filesystem mode).

**File browsing** — Navigating the vault by folder structure, seeing what's in a directory, or finding recently changed files. Useful for spatial orientation ("what's in the Research folder?" or "show me what changed this week").

**Memory recall** — Searching saved memories by topic or browsing them by tag. Claude uses semantic search to find contextually relevant memories even if the exact words don't match.

**Briefings** — Synthesized overviews that pull from multiple documents and memories on a topic. When you ask for a briefing, Claude gathers everything relevant and presents a coherent narrative rather than a list of search results.

After retrieving content, Claude synthesizes what it found into an answer to your actual question — it doesn't just list search results. If search results look promising, Claude reads the full documents before answering. If nothing is found, Claude tells you clearly rather than inventing content.

---

### fq-organizer — Bulk organization and vault maintenance

The organization skill handles operations that affect multiple documents at once, plus vault maintenance tasks.

**When Claude activates this skill:** "clean up," "organize," "archive old documents," "bulk tag," "tag everything in this project as," "archive anything older than," "clean up old memories," "move this file to," "rename this document," "copy this proposal for," "delete this empty folder," "resync the database," "the system can't see the files I just added," "tidy up my vault"

**What it handles:**

**Bulk tagging** — Find documents matching a search criteria and apply or remove tags across all of them. For example, "tag all documents in the Research folder as #project/alpha." Claude finds the matching documents, shows you the candidates, confirms before acting, and then applies the tags.

**Archive sweeps** — Find stale, outdated, or no-longer-needed documents and archive them. Claude searches based on your criteria (age, tags, folder), shows you what it found, and confirms before archiving. Nothing is permanently deleted — archived documents can be recovered.

**Memory cleanup** — Find and archive old or outdated memories. Same confirm-before-acting pattern as archive sweeps.

**Vault maintenance** — Moving or renaming documents, copying a document as a starting point for a new one, removing empty directories, reconciling the database against the filesystem, and forcing a file scan to pick up external changes. These are the plumbing operations that keep the vault in good shape.

**Important:** For bulk operations, Claude always follows a search → show candidates → confirm → execute pattern. It will never bulk-modify documents without showing you what will be affected and getting your confirmation first (unless you explicitly tell it to skip confirmation).

---

## Commands

Commands are explicit actions you invoke with a slash. Unlike skills (which Claude activates based on natural language), commands run a specific, scripted workflow.

### /fq-base:vault-scan

Trigger an immediate vault scan to discover new, moved, or deleted files.

**When to use:** You added, moved, or edited files outside of your Claude conversation (in Obsidian, Finder, terminal, etc.) and need FlashQuery to catch up.

**Usage:**
```
/fq-base:vault-scan              # Synchronous — waits for results
/fq-base:vault-scan background   # Runs in background
```

**What it reports:** New files indexed, moved files (paths updated), deleted/missing files, and externally edited files (hash mismatches that trigger re-embedding). Even zero counts are reported to confirm coverage.

### /fq-base:reconcile

Verify every database row against the current vault filesystem and fix drift.

**When to use:** You suspect the database has drifted from the vault — files were moved, renamed, or deleted outside FlashQuery, and search results feel wrong or incomplete.

**Usage:**
```
/fq-base:reconcile              # Applies fixes
/fq-base:reconcile dry-run      # Preview only — shows what would change
```

**What it does:** Scans all database rows, finds files that moved (updates their paths), and promotes truly missing files from "missing" to "archived" status (permanent removal from search). The key distinction from vault-scan: scan goes filesystem → database (finds new files), while reconcile goes database → filesystem (fixes stale records).

### /fq-base:vault-health

Full health check — scan, reconcile, and hygiene audit in one pass.

**When to use:** You want a complete status picture of your vault, or you're not sure whether to run scan or reconcile.

**Usage:**
```
/fq-base:vault-health
```

**What it does:** Runs three stages in sequence: (1) vault scan to pick up filesystem changes, (2) reconciliation to fix database drift, and (3) a hygiene audit that flags untagged documents and stale drafts. Produces a consolidated summary report.

---

## When to Use FQ-Base vs. a Domain Plugin

FQ-Base is general-purpose. If you're working within a specific domain — managing contacts (CRM), organizing product research (Product Brain), building presentations (MARP) — use the domain plugin instead. Those plugins call the same underlying FlashQuery tools but add domain-specific structure, templates, and workflows.

Use FQ-Base when you need to work with vault documents that don't belong to a specific domain plugin, or when you need vault-wide maintenance operations like scan, reconcile, or bulk tagging.
