# Record Management Workflow

Use this workflow when the user explicitly wants to create, update, retrieve, or archive a structured plugin record and has supplied enough plugin/table context. Domain plugins should own their own record semantics when available; fq-base handles the generic FlashQuery tool shape.

## Create a record

Call `write_record` with:
- `mode`: `"create"`
- `plugin_id`
- `plugin_instance` — optional
- `table`
- `data` — schema-validated fields for that table
- `include` — optional `["data", "schema_metadata"]`

If you do not know the table schema, call `get_plugin_info` first with `include: ["tables", "schema"]`.

## Update a record

Call `write_record` with:
- `mode`: `"update"`
- `plugin_id`
- `plugin_instance` — optional
- `table`
- `id`
- `data` — fields to update
- `include` — optional

Do not pass generated record fields such as `created_at`, `updated_at`, `status`, `embedding`, or `instance_id` in `data` unless the source schema explicitly makes them user-owned.

## Archive a record

Call `archive_record` with:
```
archive_record({
  targets: [{ plugin_id: "<plugin>", table: "<table>", id: "<record-id>" }]
})
```

Include `plugin_instance` inside each target if the plugin uses non-default instances.

## Register or unregister plugin schemas

Use `register_plugin` only when the user is installing or updating a plugin schema:
- Provide `schema_yaml` or `schema_path`
- Optionally provide `plugin_instance`

Use `unregister_plugin` only for explicit removal requests. Without `force`, live records produce a conflict. With `force: true`, registry state and pending reviews are removed while existing plugin table rows are left orphaned.
