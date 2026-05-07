# Document Search Workflow

Use this workflow when the user specifically wants to find vault documents.

## When to use

- "Find my notes on X"
- "Show me the documents about X"
- "Do I have a proposal for Acme?"
- "Show me what's been worked on recently"
- "Find all meeting notes tagged #client/acme"

## Tool: `search_documents`

Choose the mode based on the query type:

| Mode | When to use | What it does |
|------|-------------|--------------|
| `"filesystem"` (default) | Tag filtering, browsing recent docs, when embeddings may be stale | Scans vault, filters by tags/query substring, sorts by last-modified |
| `"semantic"` | Natural-language topic query | Semantic similarity search via pgvector |
| `"mixed"` | Want both relevance-ranked and exhaustive results | Semantic first, then filesystem to fill remaining slots |

## Steps

1. **Choose the mode:** Tag/recency filtering → `filesystem`. Topic-based query → `semantic` or `mixed`. Want completeness → `mixed`.

2. **Call `search_documents`:**
   ```
   search_documents(
     tags: [...],           // optional tag filters
     tag_match: "any",      // or "all" if multiple tags must all match
     query: "...",          // required for semantic/mixed; optional for filesystem
     mode: "mixed",
     limit: 10
   )
   ```

3. **Triage results efficiently.** To inspect multiple results without reading file bodies, call `get_document` with an array of paths and `include: ["frontmatter", "headings"]` — returns per-document metadata and heading structure.

4. **Synthesize and respond.** Answer the user's question, citing titles and paths.

## Common patterns

**"Find my meeting notes with Acme"**
```
search_documents(tags: ["#client/acme", "#type/meeting-notes"], mode: "filesystem")
```

**"Show me documents about competitor pricing"**
```
search_documents(query: "competitor pricing", mode: "semantic")
```

**"What have I been working on recently?"**
```
search_documents(mode: "filesystem")  // no filters — returns 20 most recent
```

**"Find all draft proposals"**
```
search_documents(tags: ["#type/proposal", "#status/draft"], tag_match: "all", mode: "filesystem")
```

## Getting full content

After search, to read a specific document:
```
get_document(identifiers: "clients/acme/proposal.md")
```

To quickly check structure (frontmatter, headings, fqc_id):
```
get_document(identifiers: "clients/acme/proposal.md", include: ["frontmatter", "headings"])
```

To batch-check metadata and headings on multiple results:
```
get_document(identifiers: ["path1.md", "path2.md", "path3.md"], include: ["frontmatter", "headings"])
```

### `get_document` structure parameters

- `include` (array, optional) — use `["frontmatter", "headings"]` for structure without body content.
- `max_depth` (integer, optional) — cap the heading levels returned. Pass `max_depth: 2` to return only H1s and H2s, for example. Omit or pass `6` to include every level.

**Link note:** the removed `get_doc_outline` tool used to return outbound links without body content. There is no exact replacement. If links are needed, read the relevant section with `get_document` and parse wikilinks from that section.

### Token-efficient triage pattern

- **Batch metadata scan** — pass `identifiers` as an array and `include: ["frontmatter", "headings"]` to get fqc_ids, tags, titles, and heading structure for many files in one call.
- **Single-document structure inspection** — pass a single string identifier and, if you only care about the top of the outline, set `max_depth: 2` or `max_depth: 3` to keep the response compact.

## When search returns unexpectedly empty

If the user just added or moved files outside the chat and search returns nothing you'd expect to see, the scanner may not have picked them up yet. Run `force_file_scan()` to reindex, then retry the search. Pass `background: true` for fire-and-forget if the user doesn't need to see the scan results inline. See the vault-maintenance workflow in fq-organizer for the full scan behavior.
