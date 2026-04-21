---
description: Create a new Claude skill that uses FlashQuery MCP tools
argument-hint: [skill name or description]
---

The user wants to create a new Claude skill powered by FlashQuery MCP tools. Invoke the `fq-skill-creator:creator` skill to guide them through the full workflow.

## Instructions

Use the `fq-skill-creator:creator` skill to run the complete skill creation workflow:

1. **Understand the skill requirements** — clarify what the skill does, what data it needs to work with (documents, memories, records, or a mix), and what search patterns matter
2. **Identify which FlashQuery tools the skill needs** — map data requirements to the right tool categories using the decision guide in the skill
3. **Write the skill body** — produce the SKILL.md with FlashQuery tool calls wired in correctly, following all FlashQuery conventions (fqc_id usage, error handling, tag patterns, section editing)
4. **Hand off to `/skill-creator`** — delegate testing, evaluation, and iteration to the standard skill-creator workflow

## Using the argument

If the user provided `$ARGUMENTS`, treat it as the initial description of the skill they want to build. Use it to pre-answer Step 1 (understanding requirements) and move directly to clarifying data needs rather than asking from scratch.

If no argument was provided, open with: "What kind of skill would you like to build? What should it do, and what data does it need to work with?"

## Key conventions to embed in the resulting skill

The skill body you produce must follow these FlashQuery conventions:

- Use `fqc_id` (UUID), not file paths — parse it from `create_document` responses
- Check `isError` on every tool response before proceeding
- Write lock recovery: retry once after a brief pause; inform the user on second failure
- Tag conventions: `#status/*` prefix for status tags; one status tag per document; use `apply_tags` for incremental changes
- Section editing over full rewrites: prefer `replace_doc_section` or `insert_in_doc` over `update_document` for partial changes
- Semantic search latency: newly created documents may not appear in semantic search immediately — this is normal

## Reference

The full FlashQuery tool reference (all 35 tools, parameters, return values, examples) is available in the `fq-skill-creator:creator` skill at `references/flashquery-tools.md`. Use it to get exact parameter names and shapes when writing the new skill's tool call patterns.
