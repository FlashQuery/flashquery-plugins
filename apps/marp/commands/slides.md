---
description: Create a new MARP presentation deck
argument-hint: <topic or description of the presentation>
---

Create a new MARP presentation deck using the `marp-slides` skill workflow.

## What to do

1. Parse `$ARGUMENTS` as the presentation topic and any additional context the user provided (audience, tone, number of slides, light/dark preference).

2. Immediately invoke the `marp-slides` skill workflow — start at Step 0 (recall configuration) and proceed through all steps.
   - Pass `$ARGUMENTS` as the topic context for template semantic matching in Step 1.
   - If the user already specified light or dark mode in `$ARGUMENTS`, skip the Step 1b prompt.

3. If `$ARGUMENTS` is empty, ask: "What's the presentation about?" before beginning.

## Examples

User: `/marp:slides quarterly stakeholder review`
Action: Run marp-slides workflow with topic "quarterly stakeholder review"

User: `/marp:slides product demo for investors — dark mode, 10 slides`
Action: Run marp-slides with topic "product demo for investors", dark mode pre-selected, targeting 10 slides

User: `/marp:slides`
Action: Ask the user for a topic, then begin
