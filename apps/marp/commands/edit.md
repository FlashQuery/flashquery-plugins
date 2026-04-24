---
description: Edit an existing MARP presentation deck
argument-hint: <deck name or topic, plus description of changes>
---

Edit an existing MARP presentation using the `marp-edit` skill workflow.

## What to do

1. Parse `$ARGUMENTS` for the deck name/topic and any description of the changes the user wants.

2. Immediately invoke the `marp-edit` skill workflow — start at Step 0 (recall configuration) and proceed through all steps.
   - Use the deck name/topic from `$ARGUMENTS` as the search query in Step 1.
   - Use the change description from `$ARGUMENTS` as context for Step 2 (understand the edit request).

3. If `$ARGUMENTS` is empty or only contains a deck name without a change description, ask: "What would you like to change?" before beginning.

## Examples

User: `/marp:edit Q3 roadmap — update the revenue numbers on slide 4`
Action: Find the "Q3 roadmap" deck, go to slide 4, update revenue data

User: `/marp:edit product demo — add a closing slide after the pricing section`
Action: Find "product demo" deck, add new closing slide in structural edit mode

User: `/marp:edit investor pitch — swap the bar chart for a donut chart`
Action: Find "investor pitch" deck, replace bar chart component with donut chart

User: `/marp:edit`
Action: Ask which deck to edit and what to change, then begin
