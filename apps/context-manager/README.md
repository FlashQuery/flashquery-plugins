---
name: context-manager
version: 1.0.0
---

# Context Manager

Save and restore conversation context across Claude sessions using FlashQuery's vault.

## What it does

When you're in the middle of a productive conversation and need to continue it later — in a new window, a new session, or on a different device — the Context Manager captures everything into a structured document and stores it in your FlashQuery vault. Load it back in any session to pick up right where you left off.

## Components

### Skill: `context-manager`
Auto-triggered by phrases like "save context", "pick up where we left off", "I want to continue this later", etc. Handles both save and load workflows conversationally.

### Command: `/context-manager:save [topic-hint]`
Explicitly save the current conversation context. Optionally pass a topic hint to influence the filename.

**Example:** `/context-manager:save flashquery plugin design`

### Command: `/context-manager:load [search term]`
Search for and load a previously saved context. Optionally pass a search term to skip the prompt.

**Example:** `/context-manager:load flashquery plugin`

## How saved contexts are stored

All context files are saved to the `Contexts/` folder in your FlashQuery vault with the `ai-context` tag. Filenames follow the format `[topic-slug]-[YYYY-MM-DD].md`.

## Requirements

Requires FlashQuery Core to be running and connected. The following MCP tools must be available:
- `mcp__flashquery__create_document`
- `mcp__flashquery__search_documents`
- `mcp__flashquery__get_document`
