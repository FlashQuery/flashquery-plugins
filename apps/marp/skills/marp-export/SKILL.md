---
name: marp-export
description: Export a MARP presentation to PDF, PPTX, or HTML using the Marp CLI. Triggers on 'export my presentation', 'export slides', 'export to pdf', 'export to pptx', 'convert to pdf', 'save as pdf', 'marp export', 'generate pdf from slides'.
version: 1.0
updated: 2026-04-24
---

# MARP Export

Export a MARP deck to PDF, PPTX, or HTML using the Marp CLI.

---

## Prerequisites

- Node.js must be available (`npx` handles the rest — no global install needed)
- For PPTX with editable shapes: LibreOffice must be installed (`--pptx-editable` flag)
- Internet access at export time if the deck uses Google Fonts (font download happens during export)
- VS Code preview is NOT required for export — this runs via CLI

---

## Step 1 — Identify the deck

If FlashQuery MCP is available, search for the deck by title or topic:
```
mcp__flashquery__search_documents({
  query: "<user's presentation title or topic>",
  tags: ["#marp"],
  mode: "mixed",
  limit: 5
})
```

Confirm with the user which deck to export. Get the `path` field from the result — this is the vault-relative path.

If the user provides a file path directly, use it as-is.

If FlashQuery is unavailable, ask the user for the full file path to the `.md` file.

---

## Step 2 — Choose format

Ask if not already specified:
> "Which format? PDF, PPTX, or HTML? (default: PDF)"

| Format | Flag | Notes |
|---|---|---|
| PDF | `--pdf` | Best for sharing. Preserves layout exactly. |
| PPTX | `--pptx` | Editable in PowerPoint/Keynote. Some CSS features lost. |
| HTML | `--html` | Full fidelity — animations, glassmorphism, `<details>` all render. |

---

## Step 3 — Run export

Always include `--html` (enables inline SVG, cards, charts) and `--allow-local-files` (enables local images).

**PDF:**
```bash
npx @marp-team/marp-cli "<file-path>" --pdf --html --allow-local-files
```

**PPTX:**
```bash
npx @marp-team/marp-cli "<file-path>" --pptx --html --allow-local-files
```

**HTML:**
```bash
npx @marp-team/marp-cli "<file-path>" --html --allow-local-files
```

The output file is written next to the source by default (same directory, different extension).

To specify a custom output path, add `-o "<output-path>"` to any command.

---

## Step 4 — Report result

Tell the user:
- The output file path
- The format exported
- Any warnings from the CLI (missing local files, font fallbacks)

If the export fails, show the CLI error and suggest:
- Check the file path is correct and the file exists
- Font errors: Google Fonts require internet access at export time
- Local image errors: `--allow-local-files` is already included — check that image paths use `./` relative syntax
- `npx` download failure: check internet connection or install marp-cli globally with `npm install -g @marp-team/marp-cli`

---

## Notes

- Animations, glassmorphism, and `<details>` only fully render in HTML export and VS Code preview — PDF/PPTX show static versions
- PPTX editable mode (`--pptx-editable`) requires LibreOffice to be installed
- On first run, `npx` downloads marp-cli automatically (~30 seconds)
- For repeated exports, install globally to skip the download: `npm install -g @marp-team/marp-cli`
