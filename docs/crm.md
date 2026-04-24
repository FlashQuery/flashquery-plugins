# FlashQuery CRM

**Version:** 1.6.0 · **Category:** App · **Author:** FlashQuery

Contact and relationship management through conversation — track contacts, businesses, interactions, opportunities, and pipeline status across three data layers.

---

## Overview

FlashQuery CRM is a "dissolved CRM" — there is no application to open, no dashboard to check, no forms to fill out. All operations happen through conversation with your Claude assistant. Say "add a contact for Sarah Chen at Acme Corp" and Claude creates a vault document, a database record, and wikilinks to the company. Say "what do I know about Acme?" and Claude synthesizes across documents, records, and memories to give you a dossier.

Your data lives in three places, each optimized for a different use. Vault documents are rich Markdown files you can browse in Obsidian — contact notes, company profiles, interaction timelines. Database records are structured rows in Postgres for fast queries — "who haven't I talked to in 30 days?" or "what's closing this quarter?" Memories are semantic embeddings for ambient intelligence — communication preferences, relationship context, and deal signals that surface at the right moment.

## Prerequisites

- **FlashQuery** MCP server installed and connected to your Claude assistant
- **Claude Code** (CLI) or **Cowork** (desktop)

## Installation & Setup

First, make sure you've added the FlashQuery marketplace to Claude Code (one-time step — see [Getting Started](../README.md#getting-started) in the root README):

```
/plugin marketplace add https://github.com/FlashQuery/flashquery-plugins
```

Then install the plugin:

```
/plugin install crm@flashquery-plugins
```

Then tell Claude: **"Initialize CRM"**

The initialization conversation walks you through two choices: (1) registering the CRM database schema (four tables: contacts, businesses, interactions, opportunities), and (2) choosing your vault folder structure — either a single `CRM/` folder or separate folders for contacts and companies. This is a one-time setup.

---

## Skills & Workflows

### add-contact — Create a new contact

Add a person to your CRM with a vault document, database record, and optional business wikilinks.

**When Claude activates this skill:** "add a contact," "create a contact for X," "add X to my CRM," "I met someone new," "save this contact," "track this person"

**How it works:** Provide at least a name — everything else (role, email, company, tags, relationship type) is gathered conversationally. Claude checks for duplicates, creates a vault document from the contact template (with sections for Contact Information, Relationship Context, Communication, Opportunities, Next Steps, and Interaction Timeline), creates a linked database record, and — if you mention a company — adds bidirectional wikilinks between the contact and business documents.

**Example:** "I met Sarah Chen at the product conference. She's VP of Product at Acme Corp, and she's interested in our data layer for their mobile app."

---

### add-business — Create a new company

Add an organization to your CRM with a vault document and database record.

**When Claude activates this skill:** "add a company," "create a business," "add a business record for X," "I'm working with a new company," "track this company," "new client company"

**How it works:** Provide at least a company name. Claude checks for duplicates, creates a vault document from the company template (with sections for Company Information, What They Do, Key Contacts, Opportunities, and Notes), and creates a database record. Industry tags (like `#industry/saas` or `#industry/energy`) are applied if you mention what the company does.

---

### add-opportunity — Create a deal or opportunity

Track a potential project, deal, or engagement in your pipeline.

**When Claude activates this skill:** "add an opportunity," "new deal with Acme," "log this opportunity," "track this as a deal," "potential project with X," "there's work coming from X," "they want us to pitch," "add to my pipeline"

**How it works:** Claude finds the linked contact and/or company, determines appropriate tags from the CRM tag vocabulary, and creates an opportunity record in the database. Opportunities don't get their own vault documents — the narrative lives in the associated contact and company documents, where Claude inserts it into the Opportunities section. Close dates can be imprecise ("April 2026" or "Q3 2026") and Claude converts them appropriately.

**Example:** "There's a potential consulting engagement with Acme Corp through Sarah Chen. They want help with their data architecture. Probably closing Q3, worth around $50k."

---

### log-interaction — Record a meeting, call, or conversation

Document an interaction with a contact and keep the timeline up to date.

**When Claude activates this skill:** "log a call with X," "record an interaction," "I just met with X," "we had a meeting," "had coffee with X yesterday," "just got off a call with X," "log a meeting with X," "I emailed X about Y"

**How it works:** Claude finds the contact (and optionally the business), creates an interaction record in the database with the date and type, appends the interaction to the contact's vault document under the Interaction Timeline section, and updates the `last_interaction` date on the contact record. If you mention action items, Claude also updates the Next Steps section.

**Example:** "I had coffee with Sarah Chen yesterday. We talked about the data architecture project — she said they got budget approval and want to kick off in June. I need to send her a proposal by Friday."

---

### find-entity — Look up contacts, companies, or opportunities

Search for and retrieve CRM entities by name, tags, relationship, or status.

**When Claude activates this skill:** "find X," "look up X," "search for X," "show me X," "who works at X," "show me my contacts tagged Y," "do I have a record for X," "list my contacts"

**How it works:** Claude uses three search modes depending on what you're asking:

**Structured search** — Queries the database for entities matching your criteria (name, tags, status) and returns a summary list with names, record IDs, status, and tags.

**Relationship traversal** — Finds an entity and then traces its wikilinks to discover related contacts, companies, and opportunities. The document's wikilinks are the authoritative relationship list.

**Full detail retrieval** — Pulls everything about an entity: the complete vault document, all database records, and any saved memories. Presents a unified view with memories grouped by category (communication preferences, relationship context, deal context, company intelligence).

---

### update-entity — Modify an existing contact, company, or opportunity

Change tags, pipeline stage, relationship type, name, or document sections on an existing CRM entity.

**When Claude activates this skill:** "mark Sarah as VIP," "move Acme to proposal stage," "they're a client now," "move the deal to negotiation," "update the opportunity stage," "she changed her name," "they rebranded," "tag this as high priority," "remove the prospect tag," "update Sarah's Next Steps"

**How it works:** Claude handles four types of updates:

**Tag changes** — Add or remove tags on an entity. Only one `#stage/` tag can be active at a time (Claude removes the old one when applying a new stage). Tags are applied to both the vault document and the database record.

**Name changes** — Rename a contact or company. Claude updates the vault document title, the database record, and searches for old-name references in other documents to update wikilinks.

**Section updates** — Rewrite a specific section of a contact or company document (e.g., "update Sarah's Next Steps to..."). Uses targeted section replacement to preserve the rest of the document.

**Bulk tag updates** — Apply a change to an entity and optionally propagate it to related entities (with confirmation).

---

### crm-intel — Intelligence synthesis, meeting prep, and pipeline overview

Get synthesized intelligence across all three data layers — meeting prep dossiers, pipeline overviews, follow-up recommendations, and relationship insights.

**When Claude activates this skill:** "brief me on X," "what do I know about X," "give me a dossier on X," "where do my deals stand," "show me my pipeline," "what's closing this quarter," "pipeline overview," "who haven't I spoken to," "what should I follow up on"

**How it works:** Claude handles two types of intelligence queries:

**Entity-specific queries** (meeting prep, dossiers) — Claude finds the entity, reads the full vault document, discovers relationships through wikilinks, surfaces all relevant memories (using both semantic and tag-filtered search), and checks your behavioral preferences for how briefings should be presented. The result is a synthesized briefing covering Background, Recent Interactions, Open Opportunities, Things to Remember, and Suggested Talking Points.

**Broad queries** (pipeline, follow-ups) — Claude queries the database for opportunities, contacts, or businesses matching your criteria, surfaces relevant ambient intelligence from memories, and synthesizes the results. For pipeline queries, Claude avoids tag-based filtering and uses semantic search to catch opportunities that might be tagged differently than expected.

**Example:** "Brief me on Acme Corp — I have a call with Sarah tomorrow" produces a dossier with everything you know about Acme, your interaction history with Sarah, any open opportunities, and talking points informed by saved memories about Sarah's communication preferences and deal context.

---

### crm-memory — Save and recall impressions and preferences

Store, search, and update ambient intelligence about contacts and companies — observations, preferences, and signals that don't belong in a structured document.

**When Claude activates this skill:** "remember that Sarah prefers email," "note that X is sensitive about Y," "what do I remember about X," "save this observation," "always lead briefings with opportunity status," "I heard at a conference that X"

**How it works:** Memories are organized into four categories:

- **communication_preferences** — how someone prefers to be reached, meeting format preferences, response patterns
- **relationship_context** — rapport notes, personal details, sensitivities, relationship dynamics
- **deal_context** — pricing signals, budget hints, timeline indicators, competitive intelligence
- **company_intelligence** — market position, strategic moves, organizational changes, industry trends

When saving a memory, Claude categorizes it and tags it for later retrieval. When recalling, Claude uses semantic search to find contextually relevant memories — you don't need to remember exact words. When updating, Claude creates a new version of the memory (the old version is preserved).

---

### archive-entity — Remove a contact or company from active use

Soft-archive an entity across all three data layers. Nothing is deleted — archived entities are recoverable.

**When Claude activates this skill:** "archive this contact," "archive Acme," "deactivate this record," "we're done with them," "they went out of business," "she left the company," "close this out"

**How it works:** Claude confirms before archiving, then archives the vault document, the database record, removes stage tags, and optionally archives linked opportunities and related memories. A memory is saved recording the archival context (why the entity was archived) so the information isn't lost even though the entity is no longer active.

---

### initialize-plugin — One-time CRM setup

Register the CRM database schema and configure vault folders.

**When Claude activates this skill:** "initialize CRM," "set up CRM," "register the CRM plugin," "create CRM tables"

**How it works:** Reads the CRM schema definition, calls FlashQuery's `register_plugin` tool to create four database tables (contacts, businesses, interactions, opportunities), asks you to choose a vault folder structure, saves your configuration as a memory for cross-session recall, and confirms the setup.

---

## Database Schema

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **contacts** | name, last_interaction, tags, fqc_id | Contact lookup, pipeline filtering, follow-up queries ("who haven't I talked to?") |
| **businesses** | name, tags, fqc_id | Company lookup, industry filtering |
| **interactions** | contact_id, business_id, date, tags | Interaction history, date-range queries, type filtering |
| **opportunities** | name, contact_id, business_id, close_date, tags | Pipeline tracking, closing forecasts, stage filtering |

---

## Key Concepts

**Document-first pattern.** The vault document is always created first — it's the primary source of truth. The database record is a query-layer index into the document. This means you can always browse your CRM data in Obsidian as plain Markdown files.

**Wikilinks for relationships.** Cross-entity associations (Sarah works at Acme, Acme has an opportunity) are represented as `[[wikilinks]]` in vault documents. When Claude looks up relationships, it reads the document's links — they're the authoritative source.

**Memory categories.** CRM memories are organized into four categories (communication_preferences, relationship_context, deal_context, company_intelligence) so they can be surfaced at the right moment. When you're prepping for a meeting, communication preferences and relationship context bubble up. When you're reviewing pipeline, deal context and company intelligence surface.

**Design principles.** The CRM follows five design principles: Minimum Column Principle (database records have only the columns needed for queries; everything else lives in the vault document), Tags Belong to the User (tags are your organizational vocabulary), Wikilinks for Relationships, Document Cognitive Load Test (templates pass a 30-second scan test), and Three-Layer Routing Test (every attribute routes to the correct storage layer).
