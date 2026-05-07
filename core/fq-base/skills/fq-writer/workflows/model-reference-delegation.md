# Model Reference Delegation Workflow

Use this workflow when a model should use vault documents or templates as context, but the host agent does not need to read that content into its own context first.

This is a `call_model` workflow. It requires `llm:` configured in `flashquery.yml`.

## Choose the reference pattern

| Need | Pattern |
|------|---------|
| Pass one known document | `{{ref:path/to/doc.md}}` or `{{ref:<fqc_id>}}` |
| Pass one known section | `{{ref:path/to/doc.md#Heading}}` |
| Follow a frontmatter pointer | `{{ref:source.md->projections.summary}}` |
| Fill a reusable template once | `{{ref:templates/review.md}}` plus `template_params["templates/review.md"]` |
| Use the same template more than once | `{{ref:@alias}}` plus `template_params.alias._template` |
| Inject a variable-length bundle | `{{ref:@alias}}` plus `template_params.alias._items` |
| Let the delegated model choose tools/templates during its own loop | Use a `purpose` with exposed tools/templates; do not try to express that as host references |

Prefer `{{ref:<fqc_id>}}` when the reference will be reused or stored. Paths are readable, but IDs survive moves and renames. Do not use `{{id:...}}`; current reference hydration uses `{{ref:...}}` for paths, filenames, and UUIDs.

## Direct references

Put references in host-authored `system` or `user` message content. FlashQuery resolves them before provider dispatch and returns `metadata.injected_references` plus `metadata.prompt_chars`.

```json
{
  "resolver": "purpose",
  "name": "general",
  "messages": [
    {
      "role": "user",
      "content": "Summarize this for an executive audience:\n\n{{ref:clients/acme/discovery.md}}"
    }
  ],
  "return_messages": true
}
```

Use section references when only one section is needed:

```text
{{ref:clients/acme/proposal.md#Pricing}}
```

Use pointer references when a source document's frontmatter names the target:

```text
{{ref:clients/acme/latest.md->versions.approved}}
```

`#` and `->` are mutually exclusive. If either side can be ambiguous, use an `fqc_id`.

## Template references

If the referenced document has `fq_template: true`, FlashQuery hydrates template placeholders from `template_params`. Template parameters are keyed by the template identifier used in the reference.

```json
{
  "resolver": "purpose",
  "name": "general",
  "messages": [
    {
      "role": "user",
      "content": "Run this review:\n\n{{ref:templates/document-review.md}}"
    }
  ],
  "template_params": {
    "templates/document-review.md": {
      "target_doc": "clients/acme/proposal.md",
      "criteria": "clarity, completeness, and commercial risk"
    }
  }
}
```

Template frontmatter controls parameter behavior:

- `type: "string"` substitutes the value literally.
- `type: "document"` treats the value as a document identifier and injects that document's body.
- Missing required params fail before the provider call.
- Unknown params are ignored and reported as template warnings.

## Alias references

Use aliases when one prompt needs multiple instances of the same template, or when the prompt should define a slot and the caller decides what fills it.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Compare these two reviews:\n\nA:\n{{ref:@review_a}}\n\nB:\n{{ref:@review_b}}"
    }
  ],
  "template_params": {
    "review_a": {
      "_template": "templates/document-review.md",
      "target_doc": "clients/acme/proposal.md",
      "criteria": "commercial risk"
    },
    "review_b": {
      "_template": "templates/document-review.md",
      "target_doc": "clients/acme/contract.md",
      "criteria": "legal risk"
    }
  }
}
```

Alias placeholders cannot use section or pointer operators. `{{ref:@review_a#Findings}}` and `{{ref:@review_a->target}}` are invalid.

## List aliases

Use `_items` when one placeholder should expand into an ordered set of documents and hydrated templates.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Use this background bundle:\n\n{{ref:@background}}\n\nDraft the project brief."
    }
  ],
  "template_params": {
    "background": {
      "_items": [
        "clients/acme/discovery.md",
        "clients/acme/proposal.md#Scope",
        "clients/acme/latest.md->versions.approved",
        {
          "_template": "templates/context-note.md",
          "target_doc": "clients/acme/meeting-notes.md",
          "focus": "open decisions"
        }
      ],
      "_separator": "\n\n---\n\n"
    }
  }
}
```

String entries inside `_items` use the same inner grammar as direct references, without `{{ref:` and `}}`. They cannot start with `@`. Object entries use `_template` plus per-item params.

## Failure and safety behavior

Reference hydration is fail-fast. If any active reference fails, `call_model` returns `isError: true` with `error: "reference_resolution_failed"` and `failed_references`; no provider call is made.

References and template placeholders are single-pass:

- FlashQuery scans only original host-authored `system` and `user` content.
- Injected content is not recursively scanned for more `{{ref:...}}` or template placeholders.
- Later tool results, assistant messages, and model-emitted tool arguments are not scanned.

Use `\{{ref:path.md}}` when you need to show literal reference syntax to the model.

## When to use `get_document` instead

Use `get_document` before `call_model` when the host agent must inspect, edit, quote, validate, or summarize the content before deciding what to ask. Use references when the content is only context for the delegated model. For large documents, preflight with `get_document` using headings or metadata before injecting full bodies.
