---
name: marp
version: 1.0.0
---

# MARP Plugin

Create and manage beautiful MARP presentation decks — SVG charts, dashboard components, dark/light themes, stored in your FlashQuery vault.

## Overview

This plugin integrates MARP (Markdown Presentation Ecosystem) with your FlashQuery vault. It auto-selects templates based on your presentation topic, saves decks to the vault, and persists your folder preferences and custom templates across sessions.

## Prerequisites

- VS Code extension: **Marp for VS Code**
- VS Code settings: `markdown.marp.enableHtml: true` and `markdown.marp.allowLocalFiles: true`
- FlashQuery MCP server running (for vault storage and template memory)

## Commands

| Command | Description |
|---------|-------------|
| `/marp:slides <topic>` | Create a new presentation deck |
| `/marp:configure` | Set up folder structure and install default templates |
| `/marp:save-template <name>` | Register a template for automatic selection |

## Skills

The following skills auto-trigger on relevant keywords — you don't need to use slash commands if you prefer natural language.

| Skill | Triggers on |
|-------|------------|
| `marp-slides` | "marp", "slides", "presentation", "deck", "create a presentation" |
| `marp-configure` | "configure marp", "set up marp", "marp setup", "initialize marp" |
| `marp-save-template` | "save marp template", "register marp template", "add marp template for X" |

## Bundled Templates

Two starter templates are installed when you run `/marp:configure`:

- **Default Minimal** — Clean 2-slide start, good for quick decks
- **Default Scaffold** — Full structure: title, agenda, three sections, closing slide

Both templates support dark and light mode via CSS custom properties — no separate files needed.

## Example Decks

The `examples/` folder contains 11 reference decks covering a range of visual styles:

- Dark data/dashboard decks (facebook-ads, coffee, home-gym)
- Light editorial decks (apartment, wardrobe, walking-tour)
- Luxury/premium decks (cocktail, wine-tasting)
- Nature/earthy decks (garden)
- Multi-script typography (language)
- General-purpose (sample)

Read 2–3 examples before generating to match visual quality and composition.

## Export

```bash
# PDF
npx @marp-team/marp-cli slides.md --pdf --allow-local-files

# PowerPoint
npx @marp-team/marp-cli slides.md --pptx --allow-local-files

# HTML (required for animations, glassmorphism, collapsibles)
npx @marp-team/marp-cli slides.md --html --allow-local-files
```
