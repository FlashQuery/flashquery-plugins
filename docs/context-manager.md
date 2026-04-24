# Context Manager

**Version:** 1.0.0 · **Category:** App · **Author:** FlashQuery

Save and restore conversation context across Claude sessions — pick up exactly where you left off.

---

## Overview

Context Manager solves a fundamental problem with AI conversations: when a session ends, the context is lost. This plugin saves a structured snapshot of your current conversation — decisions made, open threads, files produced, and a ready-to-paste resumption prompt — as a vault document. In a future session, load the context and continue as if you never left.

Saved contexts are stored as searchable Markdown documents in your vault, tagged with `#ai-context` for easy retrieval. They're full vault documents, so they benefit from FlashQuery's search, tagging, and organization tools.

All interaction happens through conversation with your Claude assistant. There is no separate application or UI.

## Prerequisites

- **FlashQuery** MCP server installed and connected to your Claude assistant
- **Claude Code** (CLI) or **Cowork** (desktop)

## Installation

```
/plugin install context-manager@flashquery-plugins
```

No initialization step is required. Context Manager works immediately after installation.

---

## Skills & Workflows

### context-manager — Save and load conversation context

The primary skill handles both saving and loading context through natural conversation.

#### Saving Context

**When Claude activates this skill:** "save context," "save this conversation," "I want to continue this later," "save our progress," "bookmark this conversation," "export context"

**How it works:** Claude reconstructs the current conversation into a structured document with eight sections:

**Session Summary** — A 2–4 sentence handoff brief that captures the essence of what happened in the session.

**Key Decisions & Conclusions** — Numbered list of decisions made during the conversation, including the reasoning behind each one.

**Open Threads** — Bulleted list of unresolved questions, in-progress items, and things that need follow-up.

**Important Context & Constraints** — Background information, constraints, preferences, and assumptions that informed the work.

**Files & Artifacts Produced** — Filenames, locations, and brief descriptions of anything created during the session.

**Conversation Reconstruction** — Chronological reconstruction of the conversation with User/Claude labels. Early exchanges are summarized; recent exchanges are captured in detail.

**Resumption Prompt** — A ready-to-paste prompt for the next session that provides Claude with all the context needed to continue.

The document is saved to a `Contexts/` folder in your vault with the naming pattern `[topic-slug]-[YYYY-MM-DD].md`. If a context with the same name already exists for that day, Claude appends `-v2`, `-v3`, etc.

You can optionally provide a topic hint to influence the filename: "Save context — we were working on the API migration."

#### Loading Context

**When Claude activates this skill:** "pick up where we left off," "load context," "retrieve context," "continue from saved context," "load my last context," "continue from yesterday"

**How it works:** Claude asks what context you want to load (or uses a search term you provide), searches for matching contexts among `#ai-context`-tagged documents in your vault, and presents the results. If there's exactly one match, Claude confirms before loading. If there are multiple matches, you choose from a numbered list.

Once loaded, Claude uses the context document as active working context and proceeds naturally with whatever you want to do next. It doesn't summarize the loaded context unprompted — it just picks up where things left off and waits for your next direction.

---

## Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/context-manager:save` | `/context-manager:save api-migration` | Save current conversation context. Optionally pass a topic hint for the filename slug. |
| `/context-manager:load` | `/context-manager:load migration` | Search for and load a saved context. Optionally pass a search term to skip the browsing step. |

---

## Key Concepts

**Reconstruction fidelity.** Context documents are designed for handoff quality. Early conversation exchanges are summarized to save space, but recent exchanges — where the important decisions and nuances live — are captured in detail. The resumption prompt at the end is designed to give a fresh Claude session everything it needs to continue the work.

**UUID-based retrieval.** Context Manager uses FlashQuery's `fqc_id` (UUID) to retrieve documents, not file paths. This means you can reorganize your vault — move context files to different folders, rename them — without breaking the load workflow.

**Tag discipline.** All saved contexts are tagged with `#ai-context`. Both save and load operations use this tag for filtering, which keeps context documents separate from your other vault content. If you want to find contexts manually, searching for `#ai-context` in FlashQuery or Obsidian will surface them all.

**Session continuity vs. memories.** Context Manager is for restoring a full working session — the complete thread of a conversation including decisions, open items, and artifacts. It's different from FlashQuery memories, which store individual facts or observations. Use Context Manager when you want to pick up an interrupted work session. Use memories (via FQ-Base or a domain plugin) when you want to save a single piece of information for future reference.
