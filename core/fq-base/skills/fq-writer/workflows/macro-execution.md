# Macro Execution Workflow

Use this workflow only when the user explicitly asks to run a FlashQuery macro or when a documented workflow provides a macro source. For ordinary local data operations, call the direct MCP tools instead.

Call `call_macro` with either:
- `source` — inline macro source
- `source_ref` — a vault reference to macro source
- `input_vars` — optional variables for the macro
- `budget` — optional `{ max_total_tokens, max_model_calls, max_external_tool_calls, timeout_ms }`

Macro execution is an orchestration surface; it is not a replacement for `write_document`, `search`, `write_memory`, or record tools when a single direct tool can do the job.

If `call_macro` returns a forbidden-tool, template-masquerade, or runtime error, report the error and fall back to the direct FlashQuery tool sequence only when the macro's intent is clear and the user agrees.
