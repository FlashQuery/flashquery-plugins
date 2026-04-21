---
description: Load a previously saved conversation context from FlashQuery
argument-hint: [topic or name]
---

Find and load a previously saved conversation context from FlashQuery's vault, then prime the current session to continue from where the previous one left off.

The user may have passed a search term in $ARGUMENTS — use it directly as the initial query if provided.

## Instructions

### Step 1 — Ask for the context name (if no argument)

If $ARGUMENTS is empty, ask:
> "What's the name (or part of the name) of the context you want to load? Even a few words from the topic is fine."

If $ARGUMENTS contains text, skip this step and use it as the query.

### Step 2 — Search FlashQuery

Call `mcp__flashquery__search_documents` with:
- `query`: the user's search terms (or $ARGUMENTS)
- `tags`: `["ai-context"]`
- `mode`: `"mixed"`
- `limit`: 10

Check `isError` before reading results. If the search fails, report the error and suggest the user verify FlashQuery is running.

**Note:** Documents saved in the current session may not appear in semantic results immediately. If the user is looking for something just saved, retry with `mode: "filesystem"`.

### Step 3 — Present results

**Exactly one result:** Confirm before loading:
> "Found: `[filename]` — is this the one?"

**Multiple results:** Present as a numbered list and ask the user to choose.

**No results:** Let the user know and suggest trying a different search term or verifying the file was saved with the `ai-context` tag.

### Step 4 — Ask for the next prompt

Once the user confirms which file to load:
> "What would you like to do next? I'll load the full context and we can pick right up."

### Step 5 — Load the file and continue

Call `mcp__flashquery__get_document` using the `fqc_id` from the search result:
- `identifier`: the `fqc_id` UUID from the search result

Check `isError`. If the load fails, report clearly.

Use the loaded content — session summary, decisions, open threads, conversation reconstruction — as active working context. Do NOT summarize the context back to the user unprompted. Just use it and proceed naturally with their next prompt.
