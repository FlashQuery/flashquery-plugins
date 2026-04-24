---
name: marp-configure
description: >
  Configure the MARP skill — set up a presentations folder, templates folder, and install
  default templates into the vault. Triggers on "configure marp", "set up marp", "marp setup",
  "initialize marp", "install marp templates", "marp settings".
version: 1.0
updated: 2026-04-24
---

# MARP Configure

One-time (or re-runnable) setup that establishes folder structure, installs bundled templates, and saves configuration memories that all other MARP skills read on every invocation.

---

## Step 1 — Presentations folder

Ask the user:

> "Where should MARP presentations be saved in your vault? (default: `Presentations/`)"

Accept any vault-relative folder path. Strip trailing slash for storage, re-add when constructing paths. Save this as the `presentations_folder`.

---

## Step 2 — Templates folder

Ask the user:

> "Where should MARP templates live? (default: `<presentations_folder>/Templates/`)"

Default is one level inside the presentations folder. Accept any vault-relative path.

---

## Step 3 — Save configuration memory

Call `mcp__flashquery-core__save_memory` with:
```
mcp__flashquery-core__save_memory({
  content: "[marp_config] presentations_folder: <path> — templates_folder: <path>",
  tags: ["marp-config"]
})
```

Check `isError`. If it fails, tell the user and stop — the remaining steps depend on this.

---

## Step 4 — Install bundled templates

The plugin ships two starter templates at the plugin root (two levels up from this SKILL.md, e.g. `marp/templates/`):
- `marp-default-minimal.md` — minimal CSS + 2 slides, for quick starts
- `marp-default-scaffold.md` — full structure: title, agenda, 3 sections, closing

For each bundled template:

**4a.** Read the file content from the plugin's `templates/` folder.

**4b.** Call `mcp__flashquery-core__create_document`:
```
mcp__flashquery-core__create_document({
  title: "MARP Template — Default Minimal",   // or "Default Scaffold"
  content: "<file content>",
  path: "<templates_folder>/marp-default-minimal.md",  // or marp-default-scaffold.md
  tags: ["#marp", "#marp-template"],
  frontmatter: { marp: true }
})
```

**4c.** Check `isError`. If a document already exists at that path, ask the user whether to overwrite (use `mcp__flashquery-core__update_document`) or skip.

**4d.** Parse `fqc_id` from each successful response.

---

## Step 5 — Register template memories

For each installed template, call `mcp__flashquery-core__save_memory`:

**Minimal template:**
```
mcp__flashquery-core__save_memory({
  content: "[marp_template] name: Default Minimal — fqc_id: <uuid> — path: <templates_folder>/marp-default-minimal.md — use_for: general presentations, quick start, no specific brand, simple structure, minimal slides",
  tags: ["marp-config", "marp-template"]
})
```

**Scaffold template:**
```
mcp__flashquery-core__save_memory({
  content: "[marp_template] name: Default Scaffold — fqc_id: <uuid> — path: <templates_folder>/marp-default-scaffold.md — use_for: general presentations, full structure, agenda, multiple sections, title slide, closing slide, team presentations",
  tags: ["marp-config", "marp-template"]
})
```

---

## Step 6 — Confirm and guide next steps

Tell the user:
- The presentations folder and templates folder that were configured
- Which templates were installed and where
- That they can run `/marp-save-template` to register additional branded templates (e.g., for specific products, companies, or event types)
- That running `/marp-configure` again is safe — it will update the config memory and offer to overwrite or skip existing templates

---

## Re-running configure

This skill is idempotent. If a config memory already exists (found via `search_memory` with tags `["marp-config"]` before Step 1), show the current values as defaults in each prompt so the user can keep or change them.

If template memories already exist for the default templates, ask whether to reinstall (overwrite) or skip.

---

## Error handling

- **Write lock on `save_memory`**: retry once after a brief pause. If it fails again, tell the user and continue with the remaining steps — partial configuration is recoverable.
- **`create_document` path conflict**: offer overwrite via `update_document` or skip.
- **FlashQuery MCP unavailable**: inform the user that configure requires FlashQuery. Without it, folder preferences can be noted in the conversation but not persisted.
