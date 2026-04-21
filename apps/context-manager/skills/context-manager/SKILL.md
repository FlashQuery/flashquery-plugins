---
name: context-manager
description: Save and restore conversation context across Claude sessions using FlashQuery's vault. Use this skill when the user wants to save the current conversation context to resume it later, export a conversation for continuity, pick up a previous conversation, or load a saved context to continue work. Trigger on phrases like "save context", "export this conversation", "context-save", "context-get", "pick up where we left off", "continue from a saved context", "load my context", "save this session", "I want to continue this in a new window", or any mention of preserving or restoring conversation state. Even casual mentions like "can we save our progress?" or "let me pick this up later" should trigger this skill.
compatibility: "Requires FlashQuery MCP tools: mcp__flashquery__create_document, mcp__flashquery__search_documents, mcp__flashquery__get_document"
---

# Context Manager

Two workflows for saving and restoring conversation context across Claude sessions.

**Tool surface:** `mcp__flashquery__create_document`, `mcp__flashquery__search_documents`, `mcp__flashquery__get_document`

---

## Workflow 1: context-save

**Trigger phrases:** "save context", "context-save", "save this conversation", "export context", "I want to continue this in a new window", "save our progress"

### Goal
Reconstruct the current conversation into a structured Markdown file and save it to FlashQuery's vault so it can be retrieved and resumed in a new session.

### Steps

#### Step 1 — Reconstruct the context document

Synthesize the full conversation into the template below. Be as thorough as possible — this file must give a future Claude instance enough to continue the work without loss of momentum.

```markdown
# Context: [Short descriptive title of the conversation topic]

**Saved:** [Today's date and approximate time]
**Session type:** [e.g., Technical design, Requirements gathering, Content writing, etc.]

---

## Session Summary

[2–4 sentence narrative of what this conversation was about and what was accomplished. Write this as a handoff brief — what would a colleague need to know to pick this up?]

---

## Key Decisions & Conclusions

[Numbered list of things that were decided, agreed upon, or concluded. Include reasoning where relevant. If nothing was formally decided, capture the working direction the conversation was heading.]

1. ...
2. ...

---

## Open Threads

[Bulleted list of unresolved questions, in-progress items, or things that were deferred. These are the live wires a future session will need to pick back up.]

- ...

---

## Important Context & Constraints

[Any background information, constraints, preferences, or assumptions that were established or referenced during the conversation. Include things like: system architecture, project names, tech stack, user preferences, prior decisions from other conversations, etc.]

---

## Files & Artifacts Produced

[List any files, code, documents, or artifacts created during this session. Include filenames, locations, and a brief description of each.]

- None (or list them)

---

## Conversation Reconstruction

[Best-effort chronological reconstruction of the conversation. For long conversations, summarize early exchanges and be more detailed toward the end where the most recent and active work was happening. Use "User:" and "Claude:" labels.]

**User:** ...
**Claude:** ...

---

## Resumption Prompt

[A ready-to-paste prompt that a user can send at the start of a new session to restore context. It should orient the new Claude instance, reference the key state, and pose the natural next question or task.]

> I'm continuing a conversation that was saved to FlashQuery. Here is the full context:
>
> [PASTE FILE CONTENTS HERE AFTER RETRIEVING WITH context-get]
>
> [User's actual next prompt or question]
```

#### Step 2 — Generate the filename slug

- Derive a short, meaningful filename slug from the conversation topic
- Format: `[topic-slug]-[YYYY-MM-DD]` (e.g., `flashquery-mcp-transport-2025-11-14`)
- The slug should be lowercase, hyphen-separated, 3–6 words max
- **Collision check:** Before saving, call `mcp__flashquery__search_documents` with `tags: ["ai-context"]` and `query` set to the slug to check if a similar file already exists. If a match is found, append `-v2` (or `-v3`, etc.) to the slug.

#### Step 3 — Save to FlashQuery

Call `mcp__flashquery__create_document` with:
- `title`: A human-readable title derived from the slug (e.g., `"FlashQuery MCP Transport - 2025-11-14"`)
- `content`: The fully populated Markdown template from Step 1
- `path`: `"Contexts/[slug].md"` (e.g., `"Contexts/flashquery-mcp-transport-2025-11-14.md"`)
- `tags`: `["ai-context"]`

```
mcp__flashquery__create_document({
  title: "FlashQuery MCP Transport - 2025-11-14",
  content: "...",
  path: "Contexts/flashquery-mcp-transport-2025-11-14.md",
  tags: ["ai-context"]
})
```

**After the call:** Check the response for `isError`. If `isError` is true, report the error to the user and suggest they check FlashQuery connectivity. If the error is a write lock, wait a moment and retry once — if it fails again, inform the user.

**On success:** Parse the `fqc_id` from the response (a UUID like `550e8400-e29b-41d4-a716-446655440000`). Store it for reference — it's the stable identifier for this document.

#### Step 4 — Report back to the user

After a successful save, confirm:
- The file was saved successfully
- Location: `Contexts/[filename].md`
- Tagged: `ai-context`
- Brief note on what was captured (e.g., "Captured 3 key decisions and 2 open threads about FlashQuery MCP transport design.")
- The `fqc_id` if the user may want to reference it directly

If the save fails, report the error clearly and suggest the user check FlashQuery connectivity.

---

## Workflow 2: context-get

**Trigger phrases:** "context-get", "load context", "retrieve context", "pick up a saved conversation", "continue from saved context", "load my session"

### Goal
Find a previously saved context in FlashQuery's vault, retrieve it, and prime the current session to continue from where the previous one left off.

### Steps

#### Step 1 — Ask for the context name

Ask the user:
> "What's the name (or part of the name) of the context you want to load? Even a few words from the topic is fine."

#### Step 2 — Search FlashQuery

Call `mcp__flashquery__search_documents` with:
- `query`: The partial name or topic supplied by the user
- `tags`: `["ai-context"]`
- `mode`: `"mixed"`
- `limit`: 10

```
mcp__flashquery__search_documents({
  query: "<user's search terms>",
  tags: ["ai-context"],
  mode: "mixed",
  limit: 10
})
```

Check the response for `isError` before reading results. If the search fails, let the user know and suggest they verify FlashQuery is running.

**Note:** Documents saved in the current session may not appear in semantic search immediately due to asynchronous embedding. If the user is looking for something just saved, try `mode: "filesystem"` as a fallback.

#### Step 3 — Handle search results

**If exactly one result:** Confirm the match with the user before loading:
> "Found: `Contexts/[filename].md` — is this the one?"

**If multiple results:** Present them as a numbered list and ask the user to choose:
> "I found several matches:
> 1. `flashquery-mcp-transport-2025-11-14.md`
> 2. `flashquery-architecture-2025-11-10.md`
>
> Which one would you like to load?"

**If no results:** Let the user know and suggest they try a different search term or verify the file was saved with the `ai-context` tag.

#### Step 4 — Ask for the next prompt

Once the user confirms the file to load, ask:
> "What would you like to do next? I'll load the full context and then we can pick right up."

#### Step 5 — Load the file and continue

Call `mcp__flashquery__get_document` using the `fqc_id` from the search result (preferred over path for stability):

```
mcp__flashquery__get_document({
  identifier: "<fqc_id from search result>"
})
```

Check the response for `isError`. If the load fails, report clearly and suggest the user verify the file still exists.

Then respond to the user's prompt with full awareness of the loaded context — treating the saved session summary, decisions, open threads, and conversation reconstruction as active working context. **Do not summarize the context back to the user unprompted** — just use it and proceed naturally with their next prompt.

---

## Design Notes

- **Reconstruction fidelity:** Earlier parts of long conversations may be summarized rather than verbatim — this is expected. Prioritize recency and specificity toward the end of the session.
- **No verbatim transcript access:** Claude reconstructs from memory. The "Conversation Reconstruction" section is a best-effort summary, not a raw export.
- **Self-contained:** The saved file should be fully self-contained — a future Claude instance with no other context should be able to orient itself entirely from the file.
- **Tag discipline:** Always apply the `ai-context` tag on save; always filter by it on search. This keeps context files findable and separable from other vault documents.
- **Use fqc_id, not paths:** When referencing a document after creation, always use the UUID (`fqc_id`) returned by `create_document`. Paths can change if the user reorganizes their vault.
- **Error handling:** Always check `isError` on every tool response before proceeding. Write lock errors should be retried once; persistent errors should be reported clearly to the user.
