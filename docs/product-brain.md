# Product Brain

**Version:** 0.1.0 · **Category:** App · **Author:** FlashQuery

Product knowledge management through conversation — capture, organize, and synthesize product intelligence with daily workflow support.

---

## Overview

Product Brain turns your FlashQuery vault into a product knowledge base. Thoughts get captured as sparks, research gets structured into notes, features get specified, and work gets tracked — all through conversation with Claude. The plugin handles routing each piece of information to the right document type, the right folder, and the right database table.

It's designed around a daily workflow rhythm: orient in the morning to see where you left off, capture ideas throughout the day, and close at the end of the day to log what got done and set up tomorrow's starting point. Between those bookends, you can synthesize research into specs, process your inbox, and organize your vault.

All interaction happens through conversation with your Claude assistant. There is no separate application or UI.

## Prerequisites

- **FlashQuery** MCP server installed and connected to your Claude assistant
- **Claude Code** (CLI) or **Cowork** (desktop)

## Installation & Setup

First, make sure you've added the FlashQuery marketplace to Claude Code (one-time step — see [Getting Started](../README.md#getting-started) in the root README):

```
/plugin marketplace add https://github.com/FlashQuery/flashquery-plugins
```

Then install the plugin:

```
/plugin install product-brain@flashquery-plugins
```

Then tell Claude: **"Initialize Product Brain"**

The initialization conversation creates database tables, installs document templates (spark, research note, feature spec, work item, daily log), sets up the tag vocabulary, and walks you through creating your first project. This is a one-time setup.

---

## Skills & Workflows

### Getting Started

#### init — One-time setup

Set up the entire Product Brain infrastructure from scratch.

**When Claude activates this skill:** "initialize Product Brain," "set up Product Brain"

**How it works:** Creates the five database tables (projects, documents, templates, provenance, review_state), writes base templates to the vault, sets up the default tag vocabulary (workflow, handoff, classification, and source tag groups), and creates your first project. You'll choose a project name and folder structure during the conversation.

---

#### add-project — Manage projects

Create new projects, list existing ones, switch your active project context, or archive completed projects.

**When Claude activates this skill:** "add a project," "create a new project," "list my projects," "switch to the X project," "archive the Y project"

**How it works:** Each project gets its own folder structure in the vault with subfolders for inbox, research, specs, and work items. Claude updates both the database and the plugin schema to ensure new project folders are automatically tracked by FlashQuery. You can have multiple projects and switch between them.

---

#### menu — See what's available

A contextually-aware overview of Product Brain's skills, tailored to your current vault state.

**When Claude activates this skill:** "what can Product Brain do," "show me the menu," "help"

**How it works:** Not a static help page — it reflects your current vault state and suggests the most useful next action. If your vault is empty, it suggests capturing your first idea. If you have items in your inbox, it suggests running the review loop. If you have active research, it suggests drafting a spec.

---

### Daily Workflow

#### orient — Morning brief

Your daily starting point. See where you left off, what's in your inbox, what threads are open, and what's flagged.

**When Claude activates this skill:** "what's on my plate," "where did I leave off," "morning brief," "orient"

**How it works:** Claude reads your last daily log's "Tomorrow" section to anchor context, checks your inbox for unprocessed items, surfaces open threads with unresolved questions, and highlights flagged items. This is a read-only skill — it synthesizes and presents but doesn't modify anything.

---

#### capture — Save a thought, link, or observation

The primary input mechanism. Capture ideas with minimal friction — Claude handles routing and classification.

**When Claude activates this skill:** "capture this," "I had an idea," "save this thought," "log this," "I found an interesting article about X," "jot this down"

**How it works:** Uses a three-beat model: (1) save the thought immediately as the right document type, (2) pull the thread with follow-up questions to enrich the capture, and (3) surface related connections to existing vault content. Claude infers the document type — a quick idea becomes a spark (filed to inbox), a substantial finding becomes a research note, a task becomes a work item, a detailed feature description becomes a feature spec — and routes it to the correct project folder.

**Example:** "I just realized we could use the same wikilink pattern for cross-referencing specs and research notes — it would make provenance tracking trivial." Claude saves this as a spark in your inbox, asks a follow-up question or two, and checks if it relates to anything already in your vault.

---

#### update — Quick status changes

Lightweight status updates. Mark items as resolved, shipped, archived, or blocked.

**When Claude activates this skill:** "mark this as done," "this shipped," "block this on X," "resolve the Y issue," "archive this work item"

**How it works:** Changes a document's lifecycle state by updating both the database record and the vault document's frontmatter. This skill is specifically for status changes — not for editing content (use capture or the base fq-writer for that).

---

#### close — End-of-day wrap-up

Record what got done, surface unresolved threads, and set up tomorrow's starting point.

**When Claude activates this skill:** "wrap up for the day," "end of day," "close out," "daily close"

**How it works:** A conversational end-of-day skill that creates a daily log document. Claude asks about what you accomplished, how things went, any discoveries made, and what you want to focus on tomorrow. The daily log feeds directly into the next morning's Orient brief, creating continuity across days. Claude also captures any preferences you mention about how other skills should behave.

---

### Synthesis and Review

#### retrieve — Search the vault

Semantic search across all Product Brain content.

**When Claude activates this skill:** "search for," "find my notes about," "what do I have on X," "look up," "retrieve"

**How it works:** Translates natural language questions into scoped searches using structured filtering (by project, document type, status, tags) combined with semantic search. Returns relevant documents with summaries and offers follow-ups like "brief me on this in more depth" or "show full content."

---

#### brief — Deep synthesis

Produce coherent narratives by traversing provenance chains and pulling together related documents.

**When Claude activates this skill:** "brief me on X," "give me an overview of the Y feature," "how did we arrive at this decision," "what's the history of Z"

**How it works:** A read-only skill that walks backward from feature specs through research notes to original sparks, tracing how ideas evolved. Useful before starting work on a feature, for development handoffs, milestone planning, or understanding how a decision evolved. Claude pulls together documents spread across the vault into a coherent narrative.

---

#### draft — Turn research into a feature spec

Synthesize accumulated research, sparks, and notes into a structured feature spec.

**When Claude activates this skill:** "draft a spec for X," "turn this research into a feature spec," "write up the Y feature," "create a spec from my notes"

**How it works:** Claude gathers source documents — research notes, sparks, prior specs — and synthesizes them into a feature spec using the feature-spec template. It writes provenance records linking the new spec back to all contributing sources, so you can always trace how the spec was informed. The resulting spec is a handoff artifact ready for a development team.

---

#### review-loop — Process the inbox

Background processing that keeps the vault from becoming a dumping ground.

**When Claude activates this skill:** "process my inbox," "review loop," "triage my captures," "check for open questions"

**How it works:** Routes inbox sparks to the right document type or project, performs cursory research on inbound links, checks research notes for open questions, and surfaces connections between recent captures. Updates a pinned Review Loop Brief document that tracks what was processed and what needs attention.

---

#### organize — Periodic vault cleanup

Large-scale housekeeping for when the vault gets messy or files are imported from external systems.

**When Claude activates this skill:** "organize my vault," "triage the backlog," "clean up," "housekeeping"

**How it works:** Uses a three-phase workflow: (1) discovery and inventory — scan for what needs attention, (2) draft classification — propose where things should go, (3) batched decisions — confirm and execute. Handles consolidation, relocation, and archival of stale content. Designed to work across multiple sessions with progress tracking for large vaults.

---

#### scan — Pick up external files

Register documents added to the vault outside of conversation.

**When Claude activates this skill:** "scan for new files," "I dropped some files into the vault," "pick up external files"

**How it works:** For files you added via Obsidian, Finder, or the terminal rather than through conversation. Claude updates the file index, triggers reconciliation, infers project ownership from folder paths, determines document type from folder structure, applies the appropriate template, and creates database records. Handles orphaned files (files that don't clearly belong to a project) gracefully.

---

## Document Types

| Type | Purpose | Vault Location | Template |
|------|---------|----------------|----------|
| **Spark** | Quick captures — ideas, links, observations, bugs | `{project}/inbox/` | spark.md |
| **Research Note** | Structured research with sources and findings | `{project}/research/` | research-note.md |
| **Feature Spec** | Feature specifications with requirements and scope | `{project}/specs/` | feature-spec.md |
| **Work Item** | Trackable tasks with status and ownership | `{project}/work/` | work-item.md |
| **Daily Log** | End-of-day summary with progress and open threads | Project root | daily-log.md |

---

## Key Concepts

**Daily workflow rhythm.** Product Brain is built around a daily cycle: Orient (morning) → Capture (throughout the day) → Close (end of day). The Orient and Close skills create continuity across days by reading from and writing to daily log documents.

**Three-beat capture.** When you capture something, Claude follows three beats: save immediately (no friction), pull the thread (enrichment questions), and surface connections (related vault content). The goal is to never lose a thought while also building connections.

**Provenance tracking.** When Claude drafts a feature spec from research notes and sparks, it writes provenance records linking the spec back to all its source documents. This means you can always trace how a spec was informed — from the original spark through research to the final specification.

**Project scoping.** Everything in Product Brain is organized by project. Each project has its own folder tree, and Claude scopes searches and operations to your active project by default. You can have multiple projects and switch between them.

**Tag vocabulary.** The default tag vocabulary covers four groups: workflow tags (for lifecycle state), handoff tags (for cross-team coordination), classification tags (for content categorization), and source tags (for where information came from). The vocabulary is customizable during initialization.
