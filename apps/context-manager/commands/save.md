---
description: Save the current conversation context to FlashQuery for later resumption
argument-hint: [topic-hint]
---

Save the current conversation context to FlashQuery's vault so it can be retrieved and resumed in a new session.

The user may have passed a topic hint in $ARGUMENTS — use it to inform the filename slug if provided.

## Instructions

### Step 1 — Synthesize the context document

Reconstruct the full conversation into this template. Be thorough — this file must give a future Claude instance enough to continue without loss of momentum:

```markdown
# Context: [Short descriptive title]

**Saved:** [Today's date and approximate time]
**Session type:** [e.g., Technical design, Requirements gathering, Content writing]

---

## Session Summary

[2–4 sentence handoff brief of what was discussed and accomplished]

---

## Key Decisions & Conclusions

1. ...

---

## Open Threads

- ...

---

## Important Context & Constraints

[Background, constraints, preferences, assumptions, tech stack, prior decisions]

---

## Files & Artifacts Produced

- None (or list them with path and brief description)

---

## Conversation Reconstruction

[Best-effort chronological reconstruction. Summarize early exchanges; be detailed toward the end. Use "User:" and "Claude:" labels.]

---

## Resumption Prompt

> I'm continuing a conversation that was saved to FlashQuery. Here is the full context:
>
> [PASTE FILE CONTENTS HERE AFTER RETRIEVING WITH /context-manager:context-load]
>
> [User's actual next prompt]
```

### Step 2 — Generate the filename slug

- If $ARGUMENTS contains a topic hint, use it as the basis for the slug
- Otherwise derive the slug from the conversation topic
- Format: `[topic-slug]-[YYYY-MM-DD]` (e.g., `flashquery-mcp-design-2026-04-21`)
- Lowercase, hyphen-separated, 3–6 words max
- **Collision check:** Call `mcp__flashquery__search_documents` with `tags: ["ai-context"]` and `query` set to the slug. If a similar file already exists, append `-v2` (or `-v3`, etc.).

### Step 3 — Save to FlashQuery

Call `mcp__flashquery__create_document` with:
- `title`: human-readable title from the slug (e.g., `"FlashQuery MCP Design - 2026-04-21"`)
- `content`: the fully populated template from Step 1
- `path`: `"Contexts/[slug].md"`
- `tags`: `["ai-context"]`

Check `isError` on the response. If the save fails with a write lock, wait a moment and retry once. If it fails again, report the error and suggest the user check FlashQuery connectivity.

Parse the `fqc_id` from a successful response.

### Step 4 — Confirm to the user

Report:
- The file was saved successfully
- Location: `Contexts/[filename].md`
- Tagged: `ai-context`
- A brief note on what was captured (e.g., "Captured 3 key decisions and 2 open threads.")
