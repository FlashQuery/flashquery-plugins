---
description: Set up MARP folder structure and install default templates into the vault
argument-hint: ""
---

Run the `marp-configure` skill workflow to initialize or update MARP settings.

## What to do

1. Immediately invoke the `marp-configure` skill workflow — start at Step 1 (presentations folder).

2. If a config memory already exists (found via `search_memory` with tags `["marp-config"]`), show the current values as defaults at each prompt so the user can keep or change them.

3. Complete all steps: folder setup, template installation, memory registration.

## Notes

- This command is safe to run multiple times — it is idempotent.
- No arguments are needed. Ignore `$ARGUMENTS` if provided.

## Example

User: `/marp:configure`
Action: Run the full configure workflow — ask about folders, install bundled templates, save config memory
