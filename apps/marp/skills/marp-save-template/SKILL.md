---
name: marp-save-template
description: >
  Register a MARP template — either an existing vault document or a new one created from
  scratch. Saves a template memory so marp-create can automatically match it to the right
  presentation context. Triggers on "save marp template", "register marp template",
  "add marp template for X", "create marp template for X", "new marp template".
version: 1.0
updated: 2026-04-24
---

# MARP Save Template

Registers a MARP template so the `marp-create` skill can automatically select it when the presentation context matches. Each template gets a memory entry with a natural-language `use_for` description that drives semantic matching at creation time.

---

## Step 0 — Load configuration

Call `mcp__flashquery__search_memory` with `query: "marp_config presentations templates folder"` and `tags: ["marp-config"]`.

If no config memory is found, ask the user where their templates folder is. Suggest running `marp-configure` first if they haven't set things up yet.

---

## Step 1 — Template name

Ask the user:

> "What should this template be called? (e.g., FlashQuery, Planorama, Company All-Hands)"

This becomes the `name` field in the template memory.

---

## Step 2 — Template source

Ask:

> "Do you have an existing MARP file to register, or should I create one from scratch?"

**If existing file:**
- Ask for the vault path or name of the file
- Call `mcp__flashquery__search_documents({ query: "<name>", tags: ["#marp-template"], mode: "mixed" })` to find it
- Confirm the match with the user
- Use the returned `fqc_id` — do not create a new document

**If from scratch:**
- Ask: "Start from the minimal template (2 slides) or the full scaffold (title, agenda, sections, closing)?"
- Call `mcp__flashquery__search_memory({ query: "marp_template Default Minimal", tags: ["marp-template"] })` (or Scaffold) to get the bundled template's `fqc_id`
- Read it with `mcp__flashquery__get_document({ identifier: "<fqc_id>" })`
- Use that content as the base for the new template
- Save a new copy to the templates folder:
  ```
  mcp__flashquery__create_document({
    title: "MARP Template — <name>",
    content: "<base template content>",
    path: "<templates_folder>/<slugified-name>.md",
    tags: ["#marp", "#marp-template"],
    frontmatter: { marp: true }
  })
  ```
- Parse the `fqc_id` from the response

---

## Step 3 — Use-for description

This is the most important step — it determines which presentations this template will be auto-selected for.

Ask the user:

> "When should this template be used? Describe the topics, products, brands, events, or audience this template is for. Be specific — this is used for automatic matching."

**Examples of good descriptions:**
- `"FlashQuery product, data management, AI workflows, MCP tools, local-first software, vault, Obsidian"`
- `"Planorama, project planning, enterprise software, SaaS, roadmaps, stakeholder presentations"`
- `"company all-hands, internal team meeting, OKRs, quarterly review, HR announcements"`

If the user is vague, offer a few examples and ask them to expand. The quality of this description directly affects how well automatic matching works.

---

## Step 4 — Save template memory

Call `mcp__flashquery__save_memory`:
```
mcp__flashquery__save_memory({
  content: "[marp_template] name: <name> — fqc_id: <uuid> — path: <vault path> — use_for: <use-for description>",
  tags: ["marp-config", "marp-template"]
})
```

Check `isError`. Retry once on write lock. If it fails twice, report the error — the template won't be auto-matched until the memory is saved.

---

## Step 5 — Confirm

Tell the user:
- The template name and vault path
- That it will now be automatically offered when creating presentations about: `<use_for topics>`
- That they can update the matching description by running this skill again and choosing the same template name (which will save a new memory version)
- That they can open the template file in VS Code to customize the CSS, colors, and fonts — the memory tracks it by `fqc_id` so vault path changes won't break matching

---

## Light/dark mode reminder

Both bundled templates support light and dark mode via a single CSS file — no separate files needed. When the template is used to create a deck, `marp-create` will ask the user to choose light or dark, then set `class: dark` in the frontmatter (dark) or omit it (light). Remind the user of this if they're setting up a branded template so they know to use the same CSS variable pattern.

---

## Error handling

- **Template name already exists in memories**: search existing template memories before saving. If a match is found, ask whether to update the `use_for` description or replace the template entirely.
- **`create_document` path conflict**: offer to update the existing file or use a different filename.
- **FlashQuery unavailable**: inform the user — template registration requires FlashQuery to persist the memory.
