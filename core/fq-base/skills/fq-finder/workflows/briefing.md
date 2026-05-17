# Briefing Workflow

Use this workflow when the user wants a structured overview of a topic, project, or context — pulling together documents, memories, and optionally plugin records in one sweep.

## When to use

- "Give me a briefing on X"
- "What's the status of the website project?"
- "Orient me on the Acme account before my call"
- "Overview of [topic]"
- At the start of a work session on a known topic

## Tool: `get_briefing`

```
get_briefing(
  tags: ["#client/acme"],      // required — scope by tags
  tag_match: "any",            // optional; defaults to "any". Pass "all" to require every tag.
  limit: 20,                   // per section; default is 20
  entity_types: ["documents", "memories", "records"], // optional
  plugin_id: "crm"             // optional — include plugin records
)
```

The common case — any of the listed tags matching — can omit `tag_match` entirely:

```
get_briefing(tags: ["#client/acme"])            // tag_match defaults to "any"
get_briefing(tags: ["#client/acme", "#type/proposal"], tag_match: "all")   // must have both
```

When `plugin_id` is provided, `get_briefing` includes records from that plugin's taggable tables (`tags` or `tag` column) and applies the same tag criteria to those rows. If the plugin has no taggable tables, the response may include a `plugin_no_taggable_tables` warning.

## Steps

1. **Identify the scope tags** from the user's request:
   - "briefing on Acme" → `["#client/acme"]`
   - "website redesign status" → `["#project/website-redesign"]`

2. **Decide on `plugin_id`** — include if the user's context involves structured plugin data (contacts, opportunities, etc.).

3. **Call `get_briefing`.** The response is JSON with `generated_at`, `entity_types`, `tags`, `tag_match`, `limit`, optional `warnings`, and `groups`. Each group corresponds to a requested tag and contains mixed `items` from documents, memories, and taggable plugin records.

4. **Drill into specifics if needed.** Call `get_document` on the most relevant doc, or `get_memory` on a truncated memory.

5. **Present the briefing as a synthesized summary** — not a raw dump. Cover: what documents exist, what memories are relevant, notable status items.

## When `get_briefing` vs `search`

| Situation | Prefer |
|-----------|--------|
| Clear topic with known tags | `get_briefing` — scoped, structured |
| Natural-language query without clear tags | `search` — semantic, unscoped |
| Documents only | `search` |
| Pre-meeting orientation | `get_briefing` |

## Example

**"Orient me on Acme before my call"**
```
get_briefing(tags: ["#client/acme"], plugin_id: "crm")
```
→ Synthesize: "Here's a quick Acme brief — proposal in draft, two meeting note docs, a memory noting async communication preference with ~$50k budget, CRM shows the opportunity at proposal stage. Want me to pull up the full proposal?"
