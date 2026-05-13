# Unified Search Workflow

Use this workflow when the user is looking for information without specifying whether it's in a document or a memory. It's the default starting point when intent is broad.

## When to use

- "What do we know about X?"
- "Anything on X?"
- "Find everything related to X"
- Any query where the user hasn't narrowed down to documents, memories, or records

## Tool: `search`

`search` searches documents and memories in one call. Use `mode: "semantic"` for embedding search, `mode: "filesystem"` for title/path/tag/text matching, or `mode: "mixed"` for both. Mixed is the default and is usually the best broad recall mode.

```
search(
  query: "the user's topic",
  mode: "mixed",
  tags: [...],      // optional — narrow by tag if context makes it clear
  tag_match: "any", // optional; defaults to "any". Pass "all" to require every tag on each hit.
  limit: 10,        // global result limit after merge/dedupe/sort
  entity_types: ["documents", "memories"]   // default; both types
)
```

**`tag_match` example — require every tag:**
```
search(
  query: "pricing discussion",
  mode: "mixed",
  tags: ["#client/acme", "#type/meeting-notes"],
  tag_match: "all"
)
```
Use `"all"` when the user's intent is an intersection ("meeting notes with Acme that are about pricing"). Default `"any"` is usually right for broad exploratory queries.

## Steps

1. **Formulate the query.** Extract the core topic from the user's message. Be specific:
   - User: "what do we know about Acme's timeline?" → query: `"Acme timeline"`
   - User: "anything on the website project?" → query: `"website project"`

2. **Add tag filters if appropriate.** If the user's context clearly scopes to a client, project, or topic, include matching tags. Otherwise leave `tags` unset.

3. **Call `search`.** Review the results — documents and memories are returned together with IDs, match sources, and similarity scores when semantic search contributed.

4. **Follow up on top document results.** For documents with high similarity scores (> 0.85), consider calling `get_document` to read the full content before synthesizing your answer.

5. **Synthesize and respond.** Answer the user's actual question using the retrieved content. Cite document titles and note when something came from a memory.

## Fallback: when embedding is unavailable

If semantic search is unavailable, retry `search` with `mode: "filesystem"`. Use `list_all: true` only for an intentionally unfiltered browse; otherwise provide a `query`, `tags`, or `path_filter`.

## Example

**User:** "What do we know about Acme's budget?"

```
search(query: "Acme budget", mode: "mixed", tags: ["#client/acme"])
```

Results: proposal doc (score: 0.91) + memory "Acme's budget ~$50k" (score: 0.87)
→ Call `get_document` on the proposal for full pricing detail if needed.
→ Answer: "Based on your proposal and a saved memory, Acme has ~$50k budgeted for the integration. Full proposal is at `clients/acme/proposal.md`."
