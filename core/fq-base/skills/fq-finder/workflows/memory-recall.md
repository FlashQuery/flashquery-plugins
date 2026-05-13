# Memory Recall Workflow

Use this workflow when the user wants to retrieve something they previously saved to memory.

## When to use

- "What did I save about X?"
- "What did I remember about Acme's communication style?"
- "Show me all my memories tagged #client/acme"
- "Pull up that memory about the integration timeline"

## Decision tree

```
Does the user have a specific topic in mind?
  ├── Yes → use search with entity_types: ["memories"] (semantic or mixed recall)
  └── No, they want to browse → use search with entity_types: ["memories"], list_all: true, and optional tags
            ↓
Does the user need the full content of a specific memory?
  └── Yes → use get_memory with the ID
```

---

## Semantic recall: `search`

```
search(
  query: "Acme communication preferences",
  entity_types: ["memories"],
  mode: "semantic",  // use "mixed" when keyword/list fallback is useful
  tags: [...],        // optional; narrow by tag if appropriate
  tag_match: "any",   // optional; defaults to "any". Pass "all" to require every tag.
  limit: 10
)
```

Tag intersection is genuinely useful for memory recall because memories are often multi-tagged (`#client/acme` + `#topic/pricing`, for example). Pass `tag_match: "all"` when the user's question sits at the overlap of two or more topics:

```
search(
  query: "pricing conversations",
  entity_types: ["memories"],
  mode: "semantic",
  tags: ["#client/acme", "#topic/pricing"],
  tag_match: "all"
)
```

Results include a similarity score, preview content (truncated at 200 chars), and a memory ID. If content is truncated, call `get_memory(memory_ids: "{id}")`.

**If semantic search errors** (embedding unavailable): Retry with `mode: "filesystem"` plus relevant tags. Memory filesystem mode searches memory text and tags without embeddings.

---

## Browsing: `search` list mode

Use when the user wants to see what's stored without a specific query.

```
search(
  entity_types: ["memories"],
  list_all: true,
  mode: "filesystem",
  tags: ["#client/acme"],   // optional
  tag_match: "any",
  limit: 50
)
```

Returns memories sorted by recency (newest first), content previewed at 200 characters.

**Common patterns:**
- "Show me all my memories tagged #client/acme" → `search(tags: ["#client/acme"])`
- "Show me all my memories tagged #client/acme" → `search(entity_types: ["memories"], mode: "filesystem", list_all: true, tags: ["#client/acme"])`
- "What have I saved recently?" → `search(entity_types: ["memories"], mode: "filesystem", list_all: true)` (no filters)

---

## Full content: `get_memory`

```
get_memory(memory_ids: "c3d4e5f6-a7b8-9012-cdef-123456789012")

// or batch:
get_memory(memory_ids: ["id1", "id2", "id3"])
```

Used as a follow-up after `search` when the preview is insufficient.

---

## Example flows

**"What did I save about Acme's communication preferences?"**
→ `search(query: "Acme communication preferences", entity_types: ["memories"], mode: "semantic", tags: ["#client/acme"])`
→ `get_memory(memory_ids: "{top result id}")` for full content
→ "You saved a memory noting that Acme prefers async communication. Full note: [content]"

**"Pull up the memory about the integration timeline"**
→ `search(query: "integration timeline", entity_types: ["memories"], mode: "semantic")`
→ `get_memory(memory_ids: "{top result id}")`
→ Present full content
