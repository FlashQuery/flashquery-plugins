---
name: add-project
description: >
  Use this skill when the user asks to add, create, or set up a new project
  in the Product Brain. Trigger on "add a project", "create a new project",
  "new product", "start tracking a new initiative", "add project for X",
  or when the user mentions a new product or initiative they want to start
  capturing knowledge for. Also trigger when the user asks to list projects,
  switch their active project, archive a project, or manage project lifecycle
  in any way. Even casual mentions like "I'm starting a new thing" or
  "let's set up a space for X" should trigger this skill.
---

# Add Project

Creates a new project in the Product Brain and makes it visible to all skills. Also handles project lifecycle: listing active projects, switching active context, and archiving.

## When to use

Use this skill when the user wants to:
- **Create a new project** — a new product, initiative, or area of work they want to capture knowledge for
- **List projects** — see what projects exist and their status
- **Switch active project** — change which project Orient and Review Loop focus on
- **Archive a project** — mark a project as no longer active

The rest of this skill focuses on project creation. Lifecycle operations are described at the end.

## Why projects must be created through this skill

All skills that capture or route documents — Capture, Review Loop, Orient — look up the active project by reading `prodbrain_projects` records. A folder with no corresponding database record means documents placed there can't be attributed to any project. This skill is the only path that creates both the database record and the folder structure as a single intentional operation.

## Creating a new project

### Gather information

Have a brief conversation with the user to establish:

**1. Project name** (required) — the display name for this project (e.g., "FlashQuery", "Client Portal", "Marketing Site"). This is how the project appears in Orient briefs and skill output.

**2. Project path** (required) — the folder name within the vault root (e.g., `flashquery/`, `client-portal/`). Suggest a kebab-case version of the project name as the default. The user should confirm or override.

**3. Description** (optional) — a sentence or two about what this project is. Useful for context in briefs and when skills need to understand the project's scope.

If the user's message already contains this information (e.g., "add a project called Client Portal"), extract it rather than asking again.

### Steps

#### 1. Retrieve configuration

Call `search_memory` with:
- `query`: `"product-brain-config vault root"`
- `tags`: `["product-brain-config"]`

This returns the vault root path and plugin configuration saved during Init. You need the vault root to construct the full project path.

If no configuration is found, the Product Brain hasn't been initialized yet. Tell the user to run Init first.

#### 2. Create the project record

Call `create_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `fields`:
  ```json
  {
    "name": "<project display name>",
    "project_path": "<vault_root>/<project_path>/",
    "status": "active",
    "description": "<optional description>",
    "created_at": "<current ISO timestamp>"
  }
  ```

Save the returned record ID — this is the `project_id` for all documents in this project.

#### 3. Create a welcome spark in the inbox

The research, specs, and work folders are created automatically by FlashQuery the first time a document is written into them. The inbox folder needs at least one document to exist, so create a welcome spark now.

Call `create_document` with:
- `title`: `Welcome to {project_name}`
- `path`: `{vault_root}/{project_path}/inbox/`
- `content`: a spark-format welcome note (frontmatter `type: spark`, brief body explaining this is the project inbox)

Then register the welcome spark in `prodbrain_documents` via `create_record` (same fields as described in Init step 5d). The project `prodbrain_projects` record from step 2 is what makes routing work across all skills — folders appear in Obsidian as content is captured.


#### 4. Update the registered schema

For FlashQuery to auto-track files dropped into the new project's folders outside a conversation, the plugin schema must declare those folders as `documents.types` entries. Re-register the plugin with a fully updated schema that includes all existing projects plus the new one.

a. Read the base schema from `references/schema.yaml` (in the plugin root — navigate two directory levels up from this SKILL.md).

b. Call `search_records` to get all active projects — including the one just created in step 2:

```
mcp__flashquery__search_records({
  plugin_id: "product-brain",
  table: "projects",
  filters: { status: "active" }
})
```

c. Construct the complete `documents.types` section. Start with the `_plugin/templates` and `_plugin/feedback` entries from the base schema. Then, for each active project, append four entries. Derive the project slug from `project_path` by stripping the vault root prefix and trailing slash (e.g., `"product-brain/client-portal/"` → slug `"client-portal"`). Pattern for each project:

```yaml
    - id: {slug}-inbox
      folder: {vault_root}/{project_path}/inbox
      description: "Inbox for {Project Name} — sparks land here"
      on_added: auto-track
      track_as: documents
      template: spark.md
      field_map:
        type: document_type
        status: status
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields

    - id: {slug}-research
      folder: {vault_root}/{project_path}/research
      description: "Research notes for {Project Name}"
      on_added: auto-track
      track_as: documents
      template: research-note.md
      field_map:
        type: document_type
        status: status
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields

    - id: {slug}-specs
      folder: {vault_root}/{project_path}/specs
      description: "Feature specs for {Project Name}"
      on_added: auto-track
      track_as: documents
      template: feature-spec.md
      field_map:
        type: document_type
        status: status
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields

    - id: {slug}-work
      folder: {vault_root}/{project_path}/work
      description: "Work items for {Project Name}"
      on_added: auto-track
      track_as: documents
      template: work-item.md
      field_map:
        type: document_type
        status: status
        tags: tags
      on_moved: keep-tracking
      on_modified: sync-fields
```

Repeat for every active project returned in step b.

d. Produce the full schema YAML by combining the base content (tables + `_plugin/` document type entries) with all project folder entries from step c.

e. Call `register_plugin` with:
   - `schema_yaml`: the full updated schema YAML string

   Registration is idempotent — existing tables and previously-declared folder entries are preserved. Only new entries are added.

#### 5. Update configuration memory

Call `search_memory` with `query: "product-brain-config"` and `tags: ["product-brain-config"]` to find the existing configuration memory. Then call `update_memory` with the existing `memory_id` and updated content that includes the new project in the active projects list.

If `update_memory` is not available, call `save_memory` with updated content and archive the old memory.

#### 6. Confirm and offer next step

Tell the user:
- The project was created with its name and folder path
- That they can start capturing content with Capture
- That Orient and Review Loop will include this project

Offer the natural next step: **Capture** to add the first item to the new project.

## Project lifecycle operations

### List projects

Call `search_records` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `filters`: `{ "status": "active" }` (or omit filter for all projects including archived)

Present the results showing each project's name, path, status, and description.

### Switch active project

The "active project" controls which project Orient and Review Loop focus on by default. It doesn't prevent other skills from working with any project — it's a session preference, not a structural change. No database record changes.

Call `save_memory` with:
- `content`: `[product-brain-config] Active project: {project_name} (id: {project_id}, path: {project_path})`
- `plugin_scope`: `"product-brain"`
- `tags`: `["product-brain-config", "active-project"]`

Orient and Review Loop read this via `search_memory` at the start of each run to scope their queries to the right project. Archive any previous active-project memory to avoid conflicts.

### Archive a project

Confirm the user's intent, then call `update_record` with:
- `plugin_id`: `"product-brain"`
- `table`: `"projects"`
- `id`: the project's record ID
- `fields`: `{ "status": "archived" }`

This removes the project from Orient and Review Loop processing. The project folder and all documents remain in the vault and in `prodbrain_documents` with their existing statuses — archiving is a status change, not a deletion. A project can be reactivated by updating its status back to `"active"`.

## Notes

- The `plugin_id` for all tool calls is `"product-brain"`.
- Project paths should be unique — check existing projects before creating a new one to avoid overlapping folder claims.
- A project with status `"archived"` can be reactivated by updating its status back to `"active"`.
