---
description: Search CRM memories for a contact, company, or topic
argument-hint: <contact, company, or topic to recall>
---

Search CRM memories in FlashQuery. This bypasses Claude's built-in memory and queries FlashQuery directly via `search_memory`, filtered to CRM-scoped memories only.

## What to do

1. Parse $ARGUMENTS to determine the search intent — a contact name, company name, deal topic, or general CRM query.

2. Call `mcp__flashquery__search_memory` with:
   - `query`: the user's search terms (entity name plus any relevant context, e.g., `"Sarah Chen communication preferences"` or `"Acme Corp deal signals"`)
   - `tags`: `["crm"]`
   - `limit`: `10`

3. Present the results grouped by relevance:
   - Show each memory's content (the category prefix makes it easy to scan)
   - Include the memory ID in parentheses after each entry so the user can reference it for updates
   - If no results are found, say so clearly — don't fall back to Claude's own memory

## Examples

User: `/crm:recall what do I know about Sarah Chen`
Action: search_memory with query `"Sarah Chen"`, tags `["crm"]`

User: `/crm:recall communication preferences for Acme contacts`
Action: search_memory with query `"Acme communication preferences"`, tags `["crm"]`

User: `/crm:recall any deal signals from this quarter`
Action: search_memory with query `"deal context pricing budget timeline"`, tags `["crm"]`
