# MARP

**Version:** 1.1.0 · **Category:** App · **Author:** FlashQuery

Create and manage MARP presentation decks with SVG charts, dashboard components, and dark/light themes — stored in your FlashQuery vault.

---

## Overview

The MARP plugin lets you create, edit, and export presentation decks through conversation with Claude. Decks are written in MARP-flavored Markdown — compatible with the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension for live preview — and stored as vault documents so they're searchable and organized alongside the rest of your knowledge.

The plugin includes a template system that matches topics to pre-built styles using semantic memory, supports both dark and light themes via CSS custom properties, and can generate SVG charts, dashboard components, and rich visual elements inline.

All interaction happens through conversation with your Claude assistant. There is no separate application or UI.

## Prerequisites

- **FlashQuery** MCP server installed and connected to your Claude assistant
- **Claude Code** (CLI) or **Cowork** (desktop)
- **Marp for VS Code** extension installed for live preview in VS Code
- VS Code settings: `markdown.marp.enableHtml` set to `"all"` and `markdown.marp.allowLocalFiles` set to `true`
- **Node.js** (for export via Marp CLI — installed on demand via `npx`)

## Installation & Setup

Install the plugin:

```
/plugin install marp@flashquery-plugins
```

Then tell Claude: **"Configure MARP"** (or run `/marp:configure`)

The configuration conversation asks where you want to store presentations and templates in your vault (defaults to `Presentations/` and `Presentations/Templates/`), saves your preferences as a FlashQuery memory, and installs two bundled templates (Default Minimal and Default Scaffold). This setup is idempotent — safe to run again if you want to change your folder locations.

---

## Skills & Workflows

### marp-create — Create a new presentation

Build a new deck from a topic description. Claude selects or generates a template, builds the slide structure, and saves it to your vault.

**When Claude activates this skill:** "create a presentation about," "make slides for," "new deck on," "build a deck about," "marp create"

**How it works:** Claude recalls your folder configuration from FlashQuery memory, then uses semantic search to find the best matching template for your topic. If a registered template fits, Claude loads it and adapts it to your content. If not, Claude generates a fresh deck.

You can specify light or dark mode (or Claude will ask). The generated deck is saved to your vault as a searchable document tagged with `#marp` and `#status/draft`.

**What Claude can generate:** The plugin's component library includes tables, stat cards, glassmorphism effects, terminal and browser mockups, chat bubbles, SVG charts (line, pie, donut, multi-ring, gauge, sparklines, stacked bar, vertical bar, radar, funnel, Gantt timelines), connectors, flowcharts, timeline layouts, color palette grids, and interactive elements (collapsible details, tooltips, progress bars). Claude selects appropriate components based on your topic and content.

**Font pairings:** The plugin includes 15+ curated font pairings optimized for different presentation styles — dashboard, technical, editorial, luxury, playful, and more.

**Example:** "Create a presentation about Q2 product roadmap — dark mode, include a timeline chart and milestone cards"

---

### marp-edit — Edit an existing deck

Modify content, swap components, or restructure an existing presentation.

**When Claude activates this skill:** "edit my presentation," "update my slides," "change slide 3," "fix my deck," "add a slide about," "remove the pricing slide," "reorder slides"

**How it works:** Claude finds your deck in the vault (searching by title or topic among `#marp`-tagged documents), loads it, and parses slides using the `---` delimiter. Then Claude applies your requested changes using one of three edit modes:

**Content edit** — Change text, bullets, or data without altering the layout. Claude preserves the existing visual structure and only modifies the content.

**Component swap** — Replace a chart type, card layout, or visual element with a different one. Claude matches the existing font and color scheme when generating the replacement.

**Structural edit** — Add new slides, remove slides, or reorder the deck. When adding slides, Claude matches the existing theme and layout conventions.

After editing, Claude writes the updated deck back to the vault and reminds you to preview in VS Code.

**Example:** "Update the roadmap deck — change the Q3 milestones on slide 4 and add a budget slide after the timeline"

---

### marp-export — Export to PDF, PPTX, or HTML

Export a deck using the Marp CLI.

**When Claude activates this skill:** "export my presentation," "export to PDF," "convert to PowerPoint," "save as PDF," "generate HTML," "marp export"

**How it works:** Claude finds your deck in the vault, asks for the export format (PDF, PPTX, or HTML — defaults to PDF), and runs the Marp CLI:

```bash
npx @marp-team/marp-cli slides.md --pdf --html --allow-local-files
npx @marp-team/marp-cli slides.md --pptx --html --allow-local-files
npx @marp-team/marp-cli slides.md --html --allow-local-files
```

The first run downloads `@marp-team/marp-cli` via `npx` (about 30 seconds). Subsequent exports are faster.

**Format notes:** Animations, glassmorphism effects, and collapsible `<details>` elements only render fully in HTML export and VS Code preview. PDF captures the static state. PPTX produces editable slides (best opened in LibreOffice for full fidelity).

---

### marp-save-template — Register a custom template

Save a deck as a reusable template for future presentations.

**When Claude activates this skill:** "save marp template," "register marp template," "add marp template for X," "create marp template"

**How it works:** Claude asks for a template name, determines the source (an existing deck file or create from scratch), and asks for a "use-for" description — a natural language description of what topics this template fits. The use-for description powers semantic matching when creating future decks, so be descriptive.

The template is saved as a vault document in your templates folder and registered as a FlashQuery memory tagged with `marp-template` for semantic retrieval.

**Example use-for descriptions:** "FlashQuery product, data management, AI workflows, MCP tools, local-first software" or "quarterly stakeholder reviews, company all-hands, executive summaries"

---

### marp-configure — Set up folders and install defaults

One-time setup (or reconfiguration) for the MARP plugin.

**When Claude activates this skill:** "configure marp," "set up marp," "marp setup," "initialize marp," "install marp templates"

**How it works:** Asks for your presentations folder (default: `Presentations/`) and templates folder (default: `Presentations/Templates/`), saves the configuration as a FlashQuery memory, and installs two bundled templates:

**Default Minimal** — A clean two-slide start for quick decks. Title slide plus one content slide.

**Default Scaffold** — Full structure with title, agenda, three content sections, and a closing slide. Good starting point for substantive presentations.

Both templates support dark and light mode via CSS custom properties.

---

## Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/marp:configure` | `/marp:configure` | Set up folder structure and install default templates |
| `/marp:create` | `/marp:create quarterly review` | Create a new deck. Pass topic as argument or Claude will ask. |
| `/marp:edit` | `/marp:edit roadmap — update revenue numbers` | Edit a deck. Pass deck name and changes as argument. |
| `/marp:export` | `/marp:export roadmap pdf` | Export a deck. Pass deck name and optional format (pdf, pptx, html). |
| `/marp:save-template` | `/marp:save-template FlashQuery` | Register a template. Pass template name as argument. |

---

## Key Concepts

**Semantic template matching.** When you create a new deck, Claude searches your registered templates by semantic similarity to your topic. The "use-for" description you provide when saving a template determines how well it matches future topics. This means the more templates you register, the better Claude gets at picking the right starting point.

**Vault-stored presentations.** Decks are FlashQuery vault documents, which means they're searchable, taggable, and organized alongside your other knowledge. You can find presentations using FQ-Base's search skills, tag them with project or client tags, and they benefit from the same versioning and maintenance tools as any other vault document.

**Live preview workflow.** The intended workflow is: create or edit a deck through conversation with Claude, then preview it in VS Code with the Marp extension. The VS Code preview updates live as the file changes, so you get immediate visual feedback.
