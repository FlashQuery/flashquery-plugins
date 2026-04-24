---
name: marp-edit
description: Edit an existing MARP presentation deck — update slide content, swap visual components, or restructure slides. Triggers on 'edit my presentation', 'update my slides', 'change slide', 'fix my deck', 'add a slide', 'remove a slide', 'reorder slides', 'marp edit', 'update the deck'.
version: 1.0
updated: 2026-04-24
---

# MARP Edit

Edit an existing MARP presentation already saved in the FlashQuery vault or local filesystem.

---

## Three Edit Modes

**Content edit** — change text, bullets, data, or prose on specific slides without altering layout or structure.

**Component swap** — replace a chart type, card layout, or visual element (e.g., swap a bar chart for a donut, replace a two-column card with a single list).

**Structural edit** — add new slides, remove slides, or reorder the slide sequence.

You can perform multiple modes in a single edit session. Ask the user what they want to change, then determine which modes apply.

---

## Step 0 — Recall configuration

Call `mcp__flashquery__search_memory` to load saved configuration:
```
mcp__flashquery__search_memory({
  query: "marp_config presentations_folder templates_folder",
  tags: ["marp-config"]
})
```

If MCP is unavailable, skip to local filesystem fallback.

---

## Step 1 — Find the deck

If the user named a specific presentation, search for it:
```
mcp__flashquery__search_documents({
  query: "<user's presentation title or topic>",
  tags: ["#marp"],
  mode: "mixed",
  limit: 5
})
```

Show results and ask the user to confirm which deck. If multiple results, list them with titles and paths.

If the user provides an `fqc_id` or path directly, skip the search and use it.

Once confirmed, read the full deck content:
```
mcp__flashquery__get_document({
  identifier: "<fqc_id>"
})
```

---

## Step 2 — Understand the edit request

Ask if not already clear:
> "What would you like to change? (e.g., update the data on slide 3, add a new section after the agenda, swap the bar chart for a donut chart)"

Determine the edit mode(s) required. You can combine modes in one pass.

---

## Step 3 — Parse slides

Split the document content on `\n---\n` to get an array of slide blocks. The frontmatter block (before the first `---`) is always index 0. Slides are index 1 onward.

Count slides before editing so you can refer to specific ones by number in your output.

---

## Step 4 — Apply edits

### Content edit
Locate the target slide by its heading text or slide number. Replace only the text content — preserve the layout HTML, card structure, and CSS classes. Do not touch any other slides.

### Component swap
Read the existing component carefully before replacing. Match the new component's data fields and dimensions to the original. Apply the same CSS variables (`var(--accent)`, `var(--card)`, etc.) and respect the slide's font and color theme. Refer to the SVG Charts, Card Patterns, and Layout Components sections of the marp-create skill for available component types.

### Structural edit
- **Add slide**: Insert the new slide block at the correct index in the array. Use the same CSS theme and heading hierarchy as surrounding slides. One idea per slide.
- **Remove slide**: Delete the slide block at that index.
- **Reorder**: Move the block to the desired position.

After all edits, rejoin the array with `\n---\n`.

---

## Step 5 — Write back

```
mcp__flashquery__update_document({
  identifier: "<fqc_id>",
  content: "<full updated marp markdown>"
})
```

Check `isError`. Report what changed: which slides were affected, what mode was used. Remind the user to preview in VS Code.

---

## Local filesystem fallback

If FlashQuery MCP is unavailable, ask the user for the local file path. Read the file, apply edits, and write back. Confirm before overwriting.

---

## Design Constraints

- Always preserve the frontmatter block (index 0) unless the user explicitly asks to change it
- Keep `marp: true` in frontmatter — it is required for VS Code preview
- Match the existing font, color scheme, and CSS variables when adding new slides — do not introduce new design systems unless asked
- One idea per slide — if adding a slide with heavy content, flag it and offer to split
- After editing, remind the user to preview in VS Code before exporting
