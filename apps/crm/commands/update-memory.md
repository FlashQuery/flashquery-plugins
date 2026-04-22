---
description: Update an existing CRM memory with new information
argument-hint: <what changed — e.g., "Sarah now prefers Slack over email">
---

Update an existing CRM memory in FlashQuery when information has changed. This searches for the matching memory, confirms with the user, then creates a new version via `update_memory`. The old version is preserved in the version chain.

## What to do

1. Parse $ARGUMENTS to determine:
   - The **entity** the memory is about
   - What **changed** or needs updating

2. Search for the existing memory — call `mcp__flashquery__search_memory` with:
   - `query`: the entity name plus relevant context from the user's update description
   - `tags`: `["crm"]`
   - `limit`: `5`

3. Present the matching memories to the user and ask which one to update. Show each memory's content and ID. If there's a single clear match, confirm: "I found this memory — should I update it?"

4. Once the user confirms, call `mcp__flashquery__update_memory` with:
   - `memory_id`: the confirmed memory's UUID
   - `content`: the updated content, preserving the category prefix from the original (e.g., if the original started with `[communication_preferences]`, the update should too)
   - `tags`: updated tags if entities changed, otherwise omit to preserve existing tags

5. Confirm: "Updated. The previous version is preserved in the history."

## Important

- Do NOT call `update_memory` without showing the user what will be replaced first.
- `update_memory` does not accept `plugin_scope` — the scope is inherited from the original.
- If no matching memory is found, offer to save a new one instead (suggest `/crm:remember`).

## Examples

User: `/crm:update-memory Sarah now prefers Slack over email`
Action: search for `"Sarah communication preferences"` with tags `["crm"]`, show match, confirm, then update_memory with new content `[communication_preferences] Sarah Chen now prefers Slack over email for routine communication.`

User: `/crm:update-memory Acme's budget is confirmed at $50k, not estimated`
Action: search for `"Acme budget deal context"` with tags `["crm"]`, show match, confirm, then update with `[deal_context] Acme Corp budget confirmed at $50k (previously estimated).`
