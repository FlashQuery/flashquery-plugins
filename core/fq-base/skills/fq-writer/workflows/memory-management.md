# Memory Management Workflow

Use this workflow when the user wants to save, update, or archive a memory. Memories are persistent facts, preferences, observations, and key takeaways stored in FQC's database — not as vault files. They're designed to surface in future conversations so relevant context is always available without re-reading documents.

## Decision tree

```
What does the user want?
  ├── Save something new → write_memory(mode: "create")
  ├── Update/correct an existing memory → search(entity_types: ["memories"]) → get_memory → write_memory(mode: "update")
  └── Archive/forget a memory → search(entity_types: ["memories"]) → get_memory → archive_memory
```

---

## Saving a new memory

**Tool:** `write_memory`

Use when the user says "remember that," "save this for later," "keep track of," "note that," or when a workflow (like writing meeting notes) surfaces a key takeaway worth retaining across sessions.

1. Write a precise, self-contained memory:
   - Good: `"Acme Corp prefers async communication and dislikes back-to-back meetings."`
   - Bad: `"Acme communication preferences"` (too vague — won't match well in semantic search)
   - Include the relevant subject, context, and specifics. The richer the memory, the better it surfaces in future searches.

2. Call `write_memory` with `mode: "create"`:
   - `mode` — `"create"`
   - `content` — the memory text (precise and self-contained)
   - `tags` — categorize with relevant tags (e.g., `["#client/acme"]`, `["#project/website"]`)
   - `plugin_scope` — optional; use to scope the memory to a specific plugin domain (e.g., `"crm"`). Omit for general/global memories.
   - `include` — optional; pass `["content", "tags_full"]` only when you need those full payloads in the response.

3. Read the returned `memory_id` from the JSON response.

4. Tell the user the memory was saved. If it was an incidental save (e.g., during document creation), briefly mention what was saved.

**What makes a good memory:**
- Facts about clients, contacts, projects, or preferences that might not be in a document
- Decisions made and the reasoning behind them
- Constraints, preferences, or requirements that recur across conversations
- Key outcomes from calls or meetings (the "so what" — not a transcript)

**What should stay as a document, not a memory:**
- Long-form content, structured notes, or anything the user might want to read in full
- Information that's already well-captured in a tagged vault document

---

## Updating an existing memory

**Tool sequence:** `search` → `get_memory` → `write_memory`

Use when the user says "update that memory," "that's changed," "correct the memory about," or "that information is outdated."

1. **Find the memory:**
   Call `search` with `entity_types: ["memories"]` and a descriptive query about what the memory contains. Use `mode: "semantic"` for concept recall or `mode: "mixed"` when tag/list fallback is useful.

2. **Confirm you have the right one:**
   Call `get_memory` with the ID from the search result to retrieve the full content.
   Present the current content to the user and confirm before updating (skip if the match is unambiguous).

3. **Update it:**
   Call `write_memory`:
   - `mode` — `"update"`
   - `memory_id` — the ID of the memory to update
   - `content` — the new/corrected content
   - `tags` — replacement tag list; omit to preserve existing tags

4. Read the new `memory_id` from the response. Store this if you need to reference the memory again — updates create a new latest version, and future `write_memory(mode: "update")` or `archive_memory` calls should target the latest ID.

5. Tell the user what was changed.

**Note on versioning:** `write_memory(mode: "update")` preserves the original — it creates a new version rather than overwriting. The history is kept internally.

---

## Archiving (forgetting) a memory

**Tool sequence:** `search` → `get_memory` → `archive_memory`

Use when the user says "forget that," "that's no longer relevant," "archive the memory about," or "remove that memory."

1. **Find the memory:** Call `search` with `entity_types: ["memories"]` and a descriptive query.
2. **Confirm the right one:** Call `get_memory` and present it to the user before archiving.
3. **Archive it:** Call `archive_memory` with `memory_ids` set to the memory ID. It also accepts an array for batch archiving.
4. Confirm to the user that the memory was archived (soft delete — hidden from search but not permanently gone).

---

## Example patterns

**"Remember that Acme prefers async communication"**
→ `write_memory(mode: "create", content: "Acme Corp prefers async communication over real-time calls.", tags: ["#client/acme"])`

**"Actually, Acme switched to weekly syncs — update that memory"**
→ `search(entity_types: ["memories"], query: "Acme communication preferences")` → `get_memory` (confirm) → `write_memory(mode: "update")`

**"Forget the memory about the old pricing model"**
→ `search(entity_types: ["memories"], query: "old pricing model")` → `get_memory` (confirm) → `archive_memory`
