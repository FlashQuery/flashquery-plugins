# Plugin Creator (Standalone Skill)

**Category:** Standalone Skill · **Author:** FlashQuery

Assemble a collection of skills, commands, MCP servers, agents, and hooks into a properly structured, installable Claude plugin (`.plugin` file).

---

## Overview

Plugin Creator is a standalone skill — not a plugin itself — that helps you package finished components into a distributable Claude plugin. If you've already created one or more skills (potentially using [FQ-Skill-Creator](./fq-skill-creator.md) to write them) and you're ready to bundle them up, this skill guides Claude through the assembly, validation, and packaging process.

It understands the Claude plugin structure — manifest files, skill registration, command definitions, MCP server configs, agent definitions, and hooks — and produces both a `.plugin` file (installable zip) and an unpacked plugin folder (for marketplace distribution).

This skill is about **assembly and packaging**, not building components from scratch. It takes what you already have and wires it into the proper structure. If you need help creating individual skills first, do that separately, then come back here to package them.

## Prerequisites

- One or more completed skills, commands, or other components ready to package
- **Claude Code** (CLI) or **Cowork** (desktop) for plugin installation and testing

---

## Workflow

### Phase 1: Inventory

Claude determines what components exist and what still needs creating. It asks what skills, commands, MCPs, agents, or hooks you want to include, whether component files already exist on disk, and where they're located. Claude reads every existing component file before proceeding.

**Output:** A clear list of every component going into the plugin, each marked as "exists" or "needs to be created."

### Phase 2: Design the manifest

Claude gathers metadata for the `plugin.json` manifest:

- **name** — kebab-case, becomes the skill namespace prefix (e.g., `code-tools` → `/code-tools:review`)
- **description** — one sentence explaining what the plugin does
- **version** — starts at `0.1.0` for new plugins; for updates, Claude reads the current version and suggests an appropriate bump (PATCH for fixes, MINOR for new features, MAJOR for breaking changes)
- **author.name** — who built it
- **keywords** — optional, useful for discoverability

Claude confirms the manifest with you before building.

### Phase 3: Assemble the plugin

Claude creates the plugin directory structure and populates it:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          ← required manifest (ONLY file in this directory)
├── skills/                  ← conversational skills
│   └── skill-name/
│       └── SKILL.md
├── commands/                ← slash commands
│   └── command-name.md
├── agents/                  ← subagent definitions (if needed)
│   └── agent-name.md
├── hooks/                   ← event hooks (if needed)
│   └── hooks.json
├── .mcp.json                ← MCP server configs (if needed)
├── settings.json            ← optional (e.g., default agent)
└── README.md
```

Only directories that are actually needed are created. Existing files are copied into the correct location; components that need to be created are authored during this phase.

**Key structural rules:** Components go at the plugin root, not inside `.claude-plugin/`. The `.claude-plugin/` directory contains only `plugin.json`. MCP configs use `${CLAUDE_PLUGIN_ROOT}` for local paths instead of hardcoded absolute paths.

### Phase 4: Validate and lint

Claude validates the plugin structure and lints all skill files:

- Confirms required files exist (`plugin.json` at minimum)
- Checks that no component directories are nested inside `.claude-plugin/`
- Verifies each skill has a `SKILL.md` with proper frontmatter
- Validates that `plugin.json` is well-formed JSON with required fields
- Lints skills for common issues (e.g., using `#status/` tags instead of frontmatter status properties)

Any errors are fixed before proceeding. Warnings can be acknowledged and skipped with your confirmation.

### Phase 5: Package and deliver

Claude creates two outputs:

- **`plugin-name.plugin`** — an installable zip file you can share or install directly with `/plugin install`
- **`plugin-name/`** — the unpacked plugin folder, used as the `source` path in a marketplace manifest

Both are placed in the output directory.

### Phase 6: Sync versions and update marketplace

Claude ensures version consistency across all locations where the version string appears: `plugin.json` (source of truth), `README.md` frontmatter, and — if publishing to the FlashQuery marketplace — the `marketplace.json` entry. A programmatic cross-check verifies all three match before delivering.

---

## How It Fits Into the Plugin Development Workflow

1. **Design your skills** — figure out what your plugin needs to do
2. **Write the skills** — use [FQ-Skill-Creator](./fq-skill-creator.md) if your skills use FlashQuery tools
3. **Bundle into a plugin** — use this skill to assemble everything into a `.plugin` file
4. **Distribute** — publish to a marketplace or share the file directly
