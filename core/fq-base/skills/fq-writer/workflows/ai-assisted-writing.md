# AI-Assisted Writing Workflow

Use this workflow when the user wants AI to generate or transform content, and then save the result as a vault document or memory.

Requires `llm:` configured in `flashquery.yml`. If `call_model` returns `isError: true`, fall back to prompting the user to provide the content manually (see Error handling in SKILL.md).

## Decision tree

```
Does the user want to write to an existing document or create a new one?
  ├── New document → Generate-and-create pattern
  └── Existing document → Generate-and-update pattern
        Does the content go in a specific section?
          ├── Yes → Generate-and-insert or Generate-and-replace
          └── No → Generate-and-append
```

---

## Choosing a resolver

`call_model` supports two ways to select the model:

| Situation | Use |
|-----------|-----|
| User specifies a model by name ("use the fast model") | `resolver: "model"`, `name: "<alias>"` |
| Calling from a reusable workflow or skill | `resolver: "purpose"`, `name: "<purpose_name>"` — uses the purpose's fallback chain |
| No preference stated | Default to `resolver: "purpose"` with a general-purpose purpose name if one is configured; otherwise `resolver: "model"` with a sensible alias |

---

## Generate-and-create

**Tools:** `call_model` → `write_document` → (optionally) `write_memory`

Use when the user wants AI to draft brand-new content that becomes a new document.

1. Build a clear prompt from the user's request. Include context the model will need: the audience, desired length, tone, key points to cover.

2. Call `call_model`:
   ```
   call_model({
     resolver: "purpose",
     name: "general",
     messages: [{ role: "user", content: "<your prompt>" }],
     trace_id: "<optional — set if you'll make multiple calls and want cumulative cost tracking>"
   })
   ```
   Parse `response` from the response for the generated content.

3. Review the generated text. If the output needs a follow-up call (e.g., to translate, summarize, or reformat), call `call_model` again with the same `trace_id` to keep cost tracking cumulative.

4. Call `write_document` with the generated content:
   - `mode` — `"create"`
   - `title` — derive from the user's request or the generated content's first heading
   - `content` — the AI-generated body (full markdown)
   - `path` — infer or ask if context doesn't make it obvious
   - `tags` — infer from context

5. Parse the `fq_id` from the JSON response.

6. Optionally call `write_memory` for key facts surfaced in the generated content.

7. Tell the user the document was saved, show its path, and (if `trace_id` was used) mention the token/cost totals from `metadata.trace_cumulative` in the response.

---

## Generate-and-update

**Tools:** `call_model` → `write_document` (or `insert_in_doc` / `replace_doc_section`)

Use when the user wants AI to rewrite, extend, or transform part of an existing document.

1. If you need to read the current content first, call `get_document` to retrieve it.

2. Call `call_model` with the existing content. If the host agent needs to inspect or edit the content before prompting, read it with `get_document`. If the model only needs the content as context, pass it by reference with `{{ref:...}}` and follow [Model Reference Delegation](model-reference-delegation.md).

3. Choose the right write tool based on scope:
   - Full body rewrite → `write_document`
   - Append to the end → `insert_in_doc`
   - Insert at a heading → `insert_in_doc`
   - Replace a named section → `replace_doc_section`

4. Call the selected write tool with the generated text.

---

## Using trace_id for multi-call workflows

Set a `trace_id` (any string, e.g. a UUID) on the first `call_model` call and reuse it on all subsequent calls in the same workflow. The response will include a `metadata.trace_cumulative` block:

```json
"metadata": {
  "trace_cumulative": {
  "total_calls": 3,
  "total_tokens": { "input": 1840, "output": 612 },
  "total_cost_usd": 0.0031,
  "total_latency_ms": 8200
  }
}
```

This lets you report the total cost of a multi-step generation to the user at the end.

---

## Example patterns

**"Use AI to write a follow-up email to Acme and save it as a doc"**
→ `call_model` (draft email body) → `write_document` (title: "Acme Follow-up Email", path: "clients/acme/emails/follow-up.md")

**"Generate a summary of these meeting notes and append it to the doc"**
→ `get_document` (read current notes) → `call_model` (summarize) → `insert_in_doc` (append summary under a "Summary" heading)

**"Draft a proposal for Acme's AI integration project"**
→ `call_model` (resolver: "purpose", name: "general", messages: ["Draft a professional project proposal for..."]) → `write_document` (path: "clients/acme/proposal.md", tags: ["#type/proposal", "#client/acme", "#status/draft"])

**"Rewrite the Background section of the Acme proposal to be more concise"**
→ `get_document` → `call_model` (rewrite the Background section content) → `replace_doc_section` (heading: "Background", content: generated text)

**"Translate my notes into a formal report (track the cost)"**
→ `call_model` (trace_id: "report-draft-001", messages: ["Rewrite these notes as a formal report: ..."]) → `call_model` (trace_id: "report-draft-001", messages: ["Now write an executive summary for: ..."]) → `write_document` → report `trace_cumulative.total_cost_usd` to user
