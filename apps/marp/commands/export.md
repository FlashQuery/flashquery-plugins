---
description: Export a MARP presentation to PDF, PPTX, or HTML
argument-hint: <deck name or topic> [pdf|pptx|html]
---

Export a MARP presentation using the `marp-export` skill workflow.

## What to do

1. Parse `$ARGUMENTS` for the deck name/topic and optional format (pdf, pptx, html).

2. Immediately invoke the `marp-export` skill workflow — start at Step 1 (identify the deck) and proceed through all steps.
   - Use the deck name/topic from `$ARGUMENTS` as the search query in Step 1.
   - If a format was specified in `$ARGUMENTS`, skip the Step 2 format prompt.

3. If `$ARGUMENTS` is empty, ask: "Which presentation would you like to export, and in what format?" before beginning.

## Examples

User: `/marp:export Q3 roadmap`
Action: Find "Q3 roadmap" deck, ask for format (defaulting to PDF), then export

User: `/marp:export product demo pdf`
Action: Find "product demo" deck, export as PDF without prompting for format

User: `/marp:export investor pitch html`
Action: Find "investor pitch" deck, export as HTML (full fidelity — animations render)

User: `/marp:export`
Action: Ask which deck and format, then export
