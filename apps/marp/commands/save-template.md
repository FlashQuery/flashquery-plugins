---
description: Register a MARP template for automatic selection when creating decks
argument-hint: <template name>
---

Run the `marp-save-template` skill workflow to register a new or existing MARP template.

## What to do

1. Parse `$ARGUMENTS` as the template name (e.g., "FlashQuery", "Planorama", "Company All-Hands").
   - If provided, pre-fill the template name in Step 1 of the workflow and skip asking for it.
   - If empty, ask: "What should this template be called?" before proceeding.

2. Invoke the `marp-save-template` skill workflow starting at Step 0 (load configuration).

3. Pass the template name from `$ARGUMENTS` into Step 1 so the user doesn't have to type it again.

## Examples

User: `/marp:save-template FlashQuery`
Action: Run save-template workflow with name "FlashQuery" pre-filled

User: `/marp:save-template`
Action: Ask for the template name, then run the workflow

User: `/marp:save-template Planorama deck`
Action: Run save-template workflow with name "Planorama deck" pre-filled
