---
description: Save a CRM memory — impression, preference, or observation
argument-hint: <observation about a contact, company, or deal>
---

Save a CRM memory from the user's input. This bypasses Claude's built-in memory system and stores directly in FlashQuery via `save_memory`.

## What to do

1. Parse $ARGUMENTS to identify:
   - The **entity** (contact name, company name, or deal) the observation is about
   - The **category** that best fits — one of:
     - `communication_preferences` — how to reach them, response windows, preferred channels
     - `relationship_context` — rapport, sensitivities, personal details, who they trust
     - `deal_context` — pricing signals, budget hints, timelines, negotiation positions
     - `company_intelligence` — market moves, org changes, competitive signals

2. Call `mcp__flashquery__save_memory` with:
   - `content`: the observation prefixed with the category in brackets, e.g., `[relationship_context] Sarah Chen seems frustrated with her current vendor...`
   - `plugin_scope`: `"crm"`
   - `tags`: always include `"crm"` plus entity names mentioned, e.g., `["crm", "Sarah Chen", "Acme Corp"]`

3. Confirm to the user: "Saved. I'll surface this when you ask about [entity] next time."

## Examples

User: `/crm:remember Sarah at Acme prefers email over phone, mornings only`
Action: save_memory with content `[communication_preferences] Sarah Chen at Acme Corp prefers email over phone calls, and mornings are the best window to reach her.` and tags `["crm", "Sarah Chen", "Acme Corp"]`

User: `/crm:remember heard at the conference that Acme is expanding into Europe`
Action: save_memory with content `[company_intelligence] Heard at a conference that Acme Corp is expanding into the European market.` and tags `["crm", "Acme Corp", "expansion"]`
