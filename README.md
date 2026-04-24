# FlashQuery Plugins

Official plugin marketplace for [FlashQuery](https://github.com/flashquery/flashquery) — the open source, local-first data management layer for AI workflows.

Plugins extend FlashQuery with domain-specific skills, database schemas, document templates, and workflow automation. Each plugin runs entirely through conversation with a Claude assistant — there is no separate application UI. Claude calls FlashQuery's MCP tools to manage structured data, vault documents, and semantic memories on your behalf.

Your data stays yours: Postgres tables you can query directly, Markdown files you can open in Obsidian, and vector embeddings stored in your own Supabase instance.

## Available Plugins

### Core Plugins

Core plugins provide the foundational capabilities that other plugins build on.

| Plugin | Description | Version | Docs |
|--------|-------------|---------|------|
| **[FQ-Base](./core/fq-base)** | Core skills for writing, finding, and organizing vault documents and memories, plus vault maintenance commands. The general-purpose foundation layer. | 1.0.0 | [Details](./docs/fq-base.md) |
| **[FQ-Skill-Creator](./core/fq-skill-creator)** | Meta-skill for creating new Claude skills that use FlashQuery MCP tools. Includes a complete reference for all 35 FlashQuery tools. | 2.0.0 | [Details](./docs/fq-skill-creator.md) |

### App Plugins

App plugins provide specialized workflows for specific domains. Each one adds its own database schema, document templates, and conversational skills on top of FlashQuery's three-layer storage model.

| Plugin | Description | Version | Docs |
|--------|-------------|---------|------|
| **[FlashQuery CRM](./apps/crm)** | Contact and relationship management through conversation. Track contacts, businesses, interactions, opportunities, and pipeline status across three data layers. | 1.6.0 | [Details](./docs/crm.md) |
| **[Product Brain](./apps/product-brain)** | Product knowledge management. Capture sparks, research notes, feature specs, and work items with daily workflow support and AI-assisted synthesis. | 0.1.0 | [Details](./docs/product-brain.md) |
| **[MARP](./apps/marp)** | Create and manage MARP presentation decks with SVG charts, dashboard components, and dark/light themes, stored in your vault. | 1.1.0 | [Details](./docs/marp.md) |
| **[Context Manager](./apps/context-manager)** | Save and restore conversation context across Claude sessions. Pick up exactly where you left off. | 1.0.0 | [Details](./docs/context-manager.md) |

### Standalone Skills

These are individual skills available outside of a plugin bundle.

| Skill | Description | Docs |
|-------|-------------|------|
| **[Plugin Creator](./skills/plugin-creator)** | Assemble a collection of skills, commands, MCP servers, and hooks into a properly structured, installable Claude plugin. | [Details](./docs/plugin-creator-skill.md) |

## Getting Started

### Prerequisites

You need two things before installing plugins:

1. **FlashQuery** — installed and running as an MCP server connected to your Claude assistant. Plugins call FlashQuery tools (`create_document`, `search_records`, `save_memory`, etc.) and will not function without them. See the [FlashQuery repo](https://github.com/flashquery/flashquery) for installation instructions.

2. **Claude Code** — the CLI tool from Anthropic. Plugins are distributed as a Claude Code plugin marketplace. You can install Claude Code from [claude.com/claude-code](https://claude.com/claude-code). Plugins and skills are managed entirely through Claude — there are no separate UIs to install or configure.

### Add the Marketplace

Point Claude Code at this repository to access all available plugins:

```
/plugin marketplace add https://github.com/FlashQuery/flashquery-plugins
```

Or using the shorthand form:

```
/plugin marketplace add flashquery/flashquery-plugins
```

If Claude Code prompts you for a URL, provide the full GitHub URL: `https://github.com/FlashQuery/flashquery-plugins`

This registers the FlashQuery plugin marketplace in your Claude Code configuration. You only need to do this once.

### Browse Available Plugins

Once the marketplace is added, you can see what's available:

```
/plugin marketplace list
```

### Install a Plugin

Install any plugin by name:

```
/plugin install fq-base@flashquery-plugins
/plugin install fq-skill-creator@flashquery-plugins
/plugin install crm@flashquery-plugins
/plugin install product-brain@flashquery-plugins
/plugin install marp@flashquery-plugins
/plugin install context-manager@flashquery-plugins
```

### Initialize After Installing

Plugins that manage data need a one-time setup. After installing, tell your Claude assistant to run the plugin's init skill:

- **FlashQuery CRM**: "Initialize CRM" — creates database tables and configures vault folder structure
- **Product Brain**: "Initialize Product Brain" — creates database tables, templates, tag vocabulary, and your first project
- **MARP**: "Configure MARP" — sets up folder structure and installs default templates

FQ-Base and Context Manager work immediately after installation with no initialization step.

### Update Plugins

Pull the latest versions of all plugins:

```
/plugin marketplace update flashquery-plugins
```

## How Plugins Work

A FlashQuery plugin is a bundle of **skills** — conversational workflows that your Claude assistant follows when you ask it to do something. When you say "add a contact for Sarah Chen at Acme Corp," Claude reads the `add-contact` skill, which tells it exactly which FlashQuery tools to call, in what order, and with what parameters.

All interaction happens through conversation with Claude. There is no separate application, dashboard, or UI to manage. Claude is the interface — you speak naturally, and Claude orchestrates the underlying data operations.

Plugins use FlashQuery's three-layer storage model:

- **Documents** — Markdown files in your vault, readable in Obsidian or any text editor. This is the human layer.
- **Records** — Structured rows in Postgres (via Supabase) for fast queries. This is the query layer.
- **Memories** — Semantic embeddings for ambient intelligence that surfaces at the right moment. This is the AI layer.

Every plugin skill routes information to the appropriate layer based on who needs it and how it will be accessed.

## Repository Structure

```
flashquery-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── core/
│   ├── fq-base/                  # Core vault and memory skills (3 skills, 3 commands)
│   └── fq-skill-creator/         # Meta-skill for building FQ-powered skills (1 skill)
├── apps/
│   ├── crm/                      # Contact and relationship management (10 skills)
│   ├── product-brain/            # Product knowledge management (13 skills)
│   ├── marp/                     # Presentation deck creation (5 skills/commands)
│   └── context-manager/          # Cross-session context persistence (1 skill, 2 commands)
├── skills/
│   └── plugin-creator/           # Standalone skill for assembling plugins
├── docs/                         # Human-facing documentation for each plugin
└── README.md                     # This file
```

## Building Your Own Plugin

Plugins follow a standard structure that Claude understands:

```
your-plugin/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name, version, description)
├── skills/
│   └── your-skill/
│       └── SKILL.md              # Skill definition
├── references/
│   ├── schema.yaml               # Database tables and folder claims
│   └── tags.md                   # Tag vocabulary
└── README.md
```

The `schema.yaml` file defines your plugin's database tables and is passed to FlashQuery's `register_plugin` tool during initialization. Skills are Markdown files that describe step-by-step workflows using FlashQuery's MCP tools. See any plugin in this repository for a working example.

The **FQ-Skill-Creator** plugin can help you write skills — install it and ask Claude to create a new skill. The **Plugin Creator** standalone skill can help you bundle finished skills into a distributable plugin.

For design guidance, refer to the [Plugin Building Considerations](https://github.com/flashquery/flashquery-product/blob/main/Plugins%20and%20Skills/Plugin%20Building%20Considerations.md) document, which covers schema design, callback handlers, skill patterns, tag vocabularies, and the scanning pattern.

## Contributing

We welcome contributions — new plugins, improvements to existing ones, or documentation fixes. If you're building a plugin for a new domain, open an issue first to discuss the design. The Plugin Building Considerations document is required reading before submitting a new plugin.

## License

This repository is part of the FlashQuery project. See [LICENSE](./LICENSE) for details.

## Links

- [FlashQuery](https://github.com/flashquery/flashquery) — the MCP server that powers all plugins
- [Claude Code Plugin Docs](https://code.claude.com/docs/en/plugins) — how Claude Code plugins work
- [Plugin Marketplace Docs](https://code.claude.com/docs/en/plugin-marketplaces) — creating and distributing marketplaces
