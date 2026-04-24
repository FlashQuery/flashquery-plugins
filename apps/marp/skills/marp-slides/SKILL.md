---
name: marp-slides
description: Create and manage MARP presentation decks with SVG charts, dashboard components, animations, dark/light themes. Saves decks to the FlashQuery vault. Triggers on 'marp', 'slides', 'presentation', 'deck', 'create a presentation', 'make a slide deck'.
version: 1.0
updated: 2026-04-24
---

# MARP Slides v3

## Prerequisites
- VS Code extension "Marp for VS Code"
- VS Code settings: `markdown.marp.enableHtml: true` + `markdown.marp.allowLocalFiles: true`
- Export: `npx @marp-team/marp-cli slides.md --pdf --allow-local-files`

---

## FlashQuery Integration

This skill saves decks to the FlashQuery vault and recalls user preferences across sessions. If FlashQuery MCP is unavailable, the skill falls back to saving locally after confirming with the user.

### Step 0 — Recall configuration

At the start of every generation, call `mcp__flashquery-core__search_memory` to load saved configuration:
```
mcp__flashquery-core__search_memory({
  query: "marp_config presentations_folder templates_folder",
  tags: ["marp-config"]
})
```

If the call errors (MCP server not running), skip FlashQuery entirely for this session — see "FlashQuery unavailable" below.

If no config memory is found, suggest the user run `marp-configure` first, then proceed with defaults (`Presentations/` and `Presentations/Templates/`).

### Step 1 — Select template via semantic matching

Use the presentation topic (from what the user said) to find the best-matching template. Call:
```
mcp__flashquery-core__search_memory({
  query: "<presentation topic or description the user provided>",
  tags: ["marp-template"]
})
```

**Interpreting results:**
- **Strong match** (top result clearly relevant): offer it directly — *"Found your FlashQuery template — use it, or pick a different one?"*
- **Multiple plausible matches**: list the top 2–3 by name and ask the user to choose
- **Weak or no match**: fall back to listing all registered templates:
  ```
  mcp__flashquery-core__list_memories({ tags: ["marp-template"] })
  ```
  Present names and `use_for` descriptions. User picks one, or chooses "none / start from scratch".

**Once a template is selected**, read it:
```
mcp__flashquery-core__get_document({
  identifier: "<fqc_id from the template memory>"
})
```
Use its frontmatter, CSS, and slide structure as the base. Merge the user's content in — do not override the template's design choices unless the user asks.

**If no templates are registered at all**, tell the user they can run `marp-configure` to install the default templates, or `marp-save-template` to register their own. Then proceed from scratch.

### Step 1b — Light or dark mode

After selecting a template (or starting from scratch), ask:

> "Light or dark mode? (default: dark)"

- **Dark**: ensure frontmatter contains `class: dark`
- **Light**: remove `class: dark` from the frontmatter (or omit it entirely)

Both bundled templates support both modes via CSS custom properties — no other changes are needed.

### Step 2 — Find an existing deck (when updating)

If the user says "update my deck on X", "find my presentation about Y", or similar, search before generating:
```
mcp__flashquery-core__search_documents({
  query: "<user's topic>",
  tags: ["#marp"],
  mode: "mixed",
  limit: 5
})
```

Check `isError`. If results are found, confirm which deck to update. Use `mcp__flashquery-core__get_document` with the `fqc_id` to read existing content, then update with `mcp__flashquery-core__update_document`.

### Step 3 — Save the generated deck

After generating, ask the user where to save. Use the `presentations_folder` from Step 0 as the default base:
> "Where would you like to save this deck? (default: `<presentations_folder>/<title>.md`)"

Then call:
```
mcp__flashquery-core__create_document({
  title: "<deck title>",
  content: "<full marp markdown>",
  path: "<vault-relative path>",
  tags: ["#marp"],
  frontmatter: { marp: true, status: "draft" }
})
```

Check `isError`. If successful, **parse `fqc_id` from the response** — use this UUID for all future references to this deck. Report the vault path and `fqc_id` to the user.

If a file already exists at the path, offer to use a different path or update the existing document.

### FlashQuery unavailable

If any MCP call returns an error:
> "FlashQuery isn't available right now. Would you like me to save the deck as a local file instead?"

If yes, write to the local filesystem at the path they specify. If no, generate and display in the conversation without saving.

---

## Example Decks (read before generating)

The `examples/` folder at the plugin root (two levels up from this SKILL.md — e.g. `marp/examples/`) contains 11 essential reference decks. **Before generating, read 2–3 that match the requested style.** These are the quality bar — match their composition, spacing, and visual density.

| Example | What it demonstrates |
|---|---|
| `marp_sample.md` | Foundational pattern showcase: tables, kbd, glassmorphism cards, stats grid, terminal/browser mockups, chat bubbles, circular gauges, split backgrounds. Read this first for any unfamiliar component. |
| `marp_facebook-ads.md` | Data-heavy dark (black/orange). Multi-ring donut charts, sparklines embedded in rows, funnel visualization, campaign table layout. |
| `marp_apartment.md` | Light theme (beige). Metric card grid, horizontal progress bars, pros/cons panel, multi-column comparison table with embedded progress indicators. |
| `marp_cocktail.md` | Luxury dark (navy/gold). 6-point radar/spider chart, Cinzel+Lora serif pair, beverage card layout, premium visual density. |
| `marp_coffee.md` | Technical dark (warm brown). Animated SVG steam (@keyframes), Space Mono+Work Sans monospace pair, donut ring charts, process-heavy layout. |
| `marp_garden.md` | Earthy dark (Bitter+Fira Sans). Gantt-style horizontal timeline with gradient phase bars, companion planting icons, stacked bar chart legend. |
| `marp_home-gym.md` | Neon dark (deep purple/teal). Animated glow (@keyframes glow box-shadow), 5-dot difficulty indicators, zone gauges, color-coded day columns. |
| `marp_walking-tour.md` | Warm light. Absolute-positioned circular number badges (`top: -14px` pattern), dashed arrow connectors with time labels, summary gradient card. |
| `marp_wardrobe.md` | Elegant light (Cormorant+Karla). CSS `writing-mode: vertical-rl` for rotated category labels, vertical connector lines between outfit pieces, color palette dot grid. |
| `marp_wine-tasting.md` | Dark burgundy (Cormorant Garamond+Inter). Flavor wheel SVG with concentric circles and radially positioned text labels, 5-point rating dots, food pairing icon cards. |
| `marp_language.md` | Dark navy/red (Noto Sans JP+Outfit+JetBrains Mono). Left-accent stripe cards, multi-script font support, opacity-graduated difficulty ladder, color-coded conjugation tables. |

---

## Core Rules
- Slides separated by `---`
- YAML frontmatter controls theme/pagination/styles
- `enableHtml` unlocks SVG, cards, charts, animations, interactive elements
- Default 16:9 (1280x720)

---

## Dark Starter Template

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Raleway:wght@100;200;300&display=swap');

:root {
  --accent: #ff6b1a; --accent-hover: #ff8c4a;
  --dark: #000; --card: #080808; --border: #111;
  --body: #999; --label: #666; --muted: #555; --light: #fff;
  --green: #22c55e; --red: #ef4444; --yellow: #f5a623;
}
section { background: var(--dark); color: var(--light); font-family: 'Raleway', sans-serif; font-weight: 200; padding: 56px 72px; }
h1 { font-family: 'Outfit'; font-weight: 800; font-size: 3em; color: var(--light); }
h2 { font-family: 'Raleway'; font-weight: 100; font-size: 1.3em; color: #888; }
h3 { font-family: 'Outfit'; font-weight: 600; font-size: 0.6em; color: var(--muted); text-transform: uppercase; letter-spacing: 0.2em; }
strong { color: var(--accent); font-weight: 300; }
section.lead { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
header { text-align: right; } header img { margin: 0; }
.row:hover { background: #0c0c0c; } .row { transition: background 0.2s; border-radius: 6px; }
details { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; margin-top: 8px; }
details summary { color: var(--accent); font-family: 'Outfit'; font-weight: 600; font-size: 0.8em; cursor: pointer; }
details p { color: var(--body); font-size: 0.78em; margin-top: 8px; }
.tag { font-family: 'Outfit'; font-weight: 600; font-size: 0.55em; letter-spacing: 0.12em; text-transform: uppercase; padding: 3px 10px; border-radius: 4px; }
abbr { text-decoration: none; border-bottom: 1px dotted #333; cursor: help; }
```

Frontmatter: include `marp: true` (required for VS Code preview) plus any optional fields like `header: '![w:100](./logo.png)'`, `paginate: true`, `theme: default`.

## Light Theme
Swap vars: `--accent: #2563eb; --dark: #fafafa; --card: #fff; --border: #eee; --body: #666; --label: #bbb; --light: #1a1a1a;`
Pair with Space Grotesk + IBM Plex Mono or Plus Jakarta Sans.

---

## Heading Hierarchy
- h1 = title slides (white/dark, extra large, 3–4.5em)
- h2 = subtitle (grey, thin, 1.3–1.8em)
- h3 = section label (muted, uppercase, small, 0.55–0.65em, letter-spacing: 0.2em)

---

## Font Pairings

Choose by domain. Never use a display font (Bebas Neue, Cinzel, Playfair) for body text.

| Heading | Body | Best for |
|---|---|---|
| Outfit 800 | Raleway 100–200 | Dashboard, data, default dark (documented starter) |
| DM Serif Display | DM Sans 300 | Recipes, editorial, food |
| Space Grotesk 700 | IBM Plex Mono 300 | Travel data, light technical themes |
| Sora 700 | Sora 200 | Product comparisons, minimal |
| Urbanist 800 | Urbanist 100 | Music, Spotify-style |
| Plus Jakarta Sans 800 | Plus Jakarta Sans 200 | Retros, team decks |
| Cinzel 600 | Lora 400 | Luxury, premium, dark navy (cocktail, wine) |
| Space Mono 400 | Work Sans 300 | Technical/process content, monospace feel |
| Cormorant Garamond | Inter 300 | Upscale, food/wine, elegant light |
| Cormorant 700 | Karla 300 | Fashion, wardrobe, elegant light |
| Bitter 700 | Fira Sans 300 | Earthy, botanical, garden, nature |
| Rajdhani 600 | Rubik 300 | Neon, sporty, high-energy, gym |
| Bebas Neue | Nunito Sans 300 | Bold travel titling, road trip |
| Noto Sans JP + Outfit | JetBrains Mono | Multi-script content, language learning |
| Baloo 2 700 | Poppins 300 | Playful, kids, casual events |

**Font size scale**: Title 3.8–4.5em · Heading 1.8em · Body 0.7–1.05em · Label 0.55–0.65em

---

## Images

CRITICAL: Relative paths only. `./image.png` works. Absolute paths break in preview.

- Logo header: `header: '![w:100](./logo.png)'` — hide per slide: `<!-- _header: '' -->`
- Photo bg: `![bg brightness:0.15](https://unsplash.com/photo-ID?w=1400)`
- Split: `![bg right:35% brightness:0.2 blur:3px](url)` or `![bg left:30%](url)`
- CDN logos: `<img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/name.png" style="width:200px;" />`
- Centered inline: wrap in `<div style="display:flex; justify-content:center;">` with border-radius/border

---

## Dashboard Components

### Metric Card (gradient top border)
`position:relative; overflow:hidden;` with absolute div at top: `background:linear-gradient(90deg, var(--accent), transparent); height:2px;`. Icon + label + big number + trend arrow.

### Status Dots
`<svg width="8" height="8" viewBox="0 0 8 8"><circle cx="4" cy="4" r="4" fill="#22c55e"/></svg>`
Green = active, yellow (#f5a623) = pending, red (#ef4444) = paused.

### Verdict / Status Tags
`<span class="tag" style="background:#22c55e12; color:var(--green); border:1px solid #22c55e22;">Scale</span>`
Swap green for red (kill) or yellow (review).

### Hover Rows
Wrap in `<div class="row">` for hover highlight (transition: background 0.2s defined in starter CSS).

### Difficulty / Rating Dots
5-dot system: filled circle = achieved, empty circle = remaining.
`<span style="color:var(--accent);">●●●</span><span style="color:#333;">●●</span>` (3/5)

---

## SVG Charts

### Line / Area Chart
SVG polyline (line) + polygon with linearGradient fill (area). viewBox="0 0 900 240", preserveAspectRatio="none". Add grid lines, dashed target line, circle data points.

### Pie / Donut Chart
Each segment = separate `<circle>` with stroke-dasharray + stroke-dashoffset. Circumference = 2π×r. For r=110: ~691. Segment = (pct/100)×691. Offsets accumulate negatively. `transform="rotate(-90 cx cy)"`.

### Multi-Ring Donut Chart
Stack multiple `<circle>` elements with different `r` values (e.g., 90, 70, 50) and different stroke-dasharray values. Each ring shows a different metric. Useful for comparing related percentages without a legend taking up slide space.

### Gauge / Half-Circle Meter
SVG path arc for background + colored value arc. Needle line from center + circle pivot. For scores 0–100. `stroke-linecap="round"`.

### Donut Ring (single metric)
`circ = 2π×r`. Offset = circ − (circ × pct/100). For r=74: circ=465. 89%: offset=51.

### Sparkline (inline mini)
`<svg width="50" height="16"><polyline points="0,14 8,12 16,10 24,8 50,2" fill="none" stroke="#22c55e" stroke-width="1.2"/></svg>`
Embed directly in table cells or data rows to show trend without a full chart.

### Stacked Bar (composition)
Flex div with colored width-percent segments, `border-radius`, `overflow:hidden`.

### Vertical Bar Chart
Flex container `align-items:flex-end`. Gradient bars: `background:linear-gradient(180deg, var(--accent), #cc5515); border-radius:3px 3px 0 0;`

### Radar / Spider (6-point)
SVG polygon for hexagonal grid + data shape with `fill-opacity:0.1` and stroke outline. Six data points positioned using trigonometry (60° increments). Useful for flavor profiles, attribute comparisons, skill assessments.

### Flavor Wheel (concentric rings)
Multiple concentric `<circle>` rings with labeled segments. Position text labels with `transform="rotate(angle) translate(r,0) rotate(-angle)"` to keep text readable. For flavor profiles, wine, coffee, sensory data.

### Gantt-Style Timeline
Horizontal flex rows — each row is a phase with a gradient bar (`background:linear-gradient(90deg, colorA, colorB)`) sized by width-percent to represent duration. Add month/week column headers above.

### Funnel Visualization
Stack trapezoid SVG shapes (polygon points) with decreasing width per stage. Each stage labeled with count and conversion rate.

---

## SVG Connectors & Flow

### Dashed Arrow Connector (horizontal)
`<svg><line x1="0" y1="12" x2="80" y2="12" stroke="#444" stroke-width="1" stroke-dasharray="4,3"/><polyline points="76,8 82,12 76,16" fill="none" stroke="#444" stroke-width="1"/></svg>`
Add a centered `<text>` above for walk time / duration label.

### Vertical Connector Line
`<div style="width:1px; height:32px; background:#333; margin:4px auto;"></div>`
Use between vertically stacked elements (outfit pieces, phase cards, stop cards).

### Vertical Gradient Flow Bar
`<div style="width:4px; height:60px; background:linear-gradient(180deg, var(--accent), transparent); margin:0 auto; border-radius:2px;"></div>`
Shows time/distance/flow between timeline items. More expressive than a plain line.

### Wavy SVG Connector
`<svg width="100" height="30" viewBox="0 0 100 30"><path d="M0,15 Q25,0 50,15 T100,15" fill="none" stroke="#888" stroke-width="1.5"/></svg>`
Use between timeline phases for a softer, organic feel. Good for event and lifestyle decks.

---

## Card Patterns

### Left-Accent Stripe Card
`<div style="border-left:3px solid var(--accent); padding:10px 14px; background:var(--card);">content</div>`
Use for vocabulary cards, language data, definition lists, any item that needs strong left-edge visual anchoring.

### Absolute-Positioned Number Badge
```html
<div style="position:relative; margin-top:14px;">
  <div style="position:absolute; top:-14px; left:50%; transform:translateX(-50%);
    width:28px; height:28px; border-radius:50%; background:var(--accent);
    display:flex; align-items:center; justify-content:center;
    font-family:'Outfit'; font-weight:800; font-size:0.7em; color:#fff;">3</div>
  <div style="... card content ..."></div>
</div>
```
Place numbered badges floating above stop/step cards.

### Top-Border Accent Card
`<div style="border-top:3px solid var(--accent); border-radius:0 0 8px 8px; padding:16px 18px; background:var(--card);">content</div>`
Good for seasonal cards, category cards, any card needing a colored cap.

### Glassmorphism Card
`<div style="background:rgba(255,255,255,0.05); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px;">content</div>`
Works well on image-background slides. Only visible in HTML export and VS Code preview.

---

## Interactive Elements

- Collapsible: `<details><summary>Title</summary><p>Content</p></details>`
- Tooltip: `<abbr title="Full text">TERM</abbr>`
- Slider: `<input type="range" style="accent-color:var(--accent);" />`
- Checkbox: `<input type="checkbox" checked style="accent-color:var(--accent);" />`
- Progress: `<progress value="76" max="100" style="accent-color:var(--accent);"></progress>`
- Keyboard key: `<kbd style="background:#111; border:1px solid #333; border-radius:3px; padding:1px 6px; font-family:monospace; font-size:0.8em;">Ctrl</kbd>`

---

## Layout Components

- **Card Row**: `display:flex; gap:14px;` with `flex:1` children
- **Before/After Split**: Two flex panels, `border-top` red vs green
- **Terminal Mockup**: Traffic light dots + monospace body on dark background
- **Browser Mockup**: Dots + URL bar div + content area
- **Chat Bubbles**: User (left, grey bubble) + agent (right, accent-tinted bubble)
- **Flowchart**: Boxes + SVG arrow connectors between them
- **Timeline (horizontal dots)**: `border-left` or dot circles with `::before`
- **Day Column Headers**: Flex row of labeled columns with colored header cells for day-of-week layouts

### CSS `writing-mode` for Rotated Labels
`<div style="writing-mode:vertical-rl; transform:rotate(180deg); font-size:0.55em; letter-spacing:0.15em; text-transform:uppercase; color:var(--muted);">Category</div>`
Use for sidebar category labels, axis labels on charts, or classification labels alongside card rows.

### Color Palette Dot Grid
`<div style="width:24px; height:24px; border-radius:50%; background:#2a4a3e; display:inline-block; margin:3px;"></div>`
Arrange in a flex-wrap grid for color palette displays, wine color identifiers, material swatches.

### Opacity-Graduated Ladder
Render progression levels as a vertical list where each level gets decreasing opacity toward the bottom (achieved = opacity 1, not yet reached = opacity 0.2–0.4). Useful for difficulty rankings, achievement trees, language levels.

---

## Multi-Script Typography

When a deck includes non-Latin characters (Japanese, Arabic, Korean, etc.):
1. Import both a Latin font and a script-appropriate font (e.g., `Noto Sans JP` for Japanese)
2. Apply the script font as a secondary fallback in `font-family`
3. Use monospace (JetBrains Mono, Space Mono) for data fields, code blocks, and structured language data
4. Example: `font-family: 'Outfit', 'Noto Sans JP', sans-serif;`

---

## SVG Icons

All wrapped in `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="1.5">`.
Sizes: inline=16, cards=44, feature=32.

Dollar: `path d="M12 2v20M17 5H9.5a3.5 3.5 0 1 0 0 7h5a3.5 3.5 0 1 1 0 7H6"`
Heartbeat: `polyline points="22 12 18 12 15 21 9 3 6 12 2 12"`
Check (green): `path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"` + `polyline points="22 4 12 14.01 9 11.01"`
Arrow up (green): `polyline points="18 15 12 9 6 15"`
Arrow down (red): `polyline points="18 9 12 15 6 9"`
X circle (red): `circle cx=12 cy=12 r=10` + two crossing lines
Clock: `circle cx=12 cy=12 r=10` + `polyline points="12 6 12 12 16 14"`
Eye: `path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"` + `circle cx=12 cy=12 r=3`
Lightning: `path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"`
Warning (yellow): triangle path
Search: `circle cx=11 cy=11 r=8` + line to corner
Bars: three vertical paths
Users: user silhouette + circle
Globe: circle + horizontal line + vertical ellipse
Lock: rect + arch path
Book: two paths for book shape

---

## Animations

Only visible in HTML export and VS Code preview. Use sparingly — one animation type per deck maximum.

### Float (ambient lift)
```css
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
```
Apply: `animation: float 4s ease-in-out infinite;`
Stagger cards with delay: `animation-delay: 0.5s;`

### Glow (neon pulse)
```css
@keyframes glow {
  0%,100% { box-shadow: 0 0 8px var(--accent); }
  50%      { box-shadow: 0 0 24px var(--accent), 0 0 40px var(--accent-hover); }
}
```
Apply to cards or metric numbers. Good for neon/gym/energy themes.

### Steam / Flow (SVG path animation)
```css
@keyframes steam {
  0%   { stroke-dashoffset: 100; opacity: 0; }
  50%  { opacity: 0.6; }
  100% { stroke-dashoffset: 0; opacity: 0; }
}
```
Apply to SVG `<path>` with `stroke-dasharray: 100;`. Good for process/brewing/flow visualizations.

### Blink (cursor)
```css
@keyframes blink { 0%,100%{border-color:var(--accent)} 50%{border-color:transparent} }
```
Apply to a `border-right` cursor in terminal mockups.

---

## Export

```bash
npx @marp-team/marp-cli slides.md --pdf --allow-local-files
npx @marp-team/marp-cli slides.md --pptx --allow-local-files
npx @marp-team/marp-cli slides.md --html --allow-local-files
```

`--pptx-editable` needs LibreOffice. Animations, glassmorphism, and `<details>` only render in HTML export and VS Code preview.

---

## Design Rules

1. One idea per slide. Overflow clips silently — no warning in source.
2. h1 = white/dark. Accent color for data highlights and CTAs only, never primary text.
3. Body text #999, labels #666. Never darker than #555 on dark backgrounds.
4. Max 6 rows per list slide.
5. Charts over raw numbers. Mix visual types across slides (don't repeat the same chart).
6. Relative image paths only (`./image.png`). Absolute paths break in preview.
7. Always preview in VS Code before exporting.
8. Per-slide overrides: `_backgroundColor`, `_header`, `_paginate`, `_footer`
9. Custom portrait dimensions: `section { width: 540px; height: 720px; }` (use CSS, not `size:` frontmatter). Stack vertically and scale down 15–20%.
10. Accent colors follow domain psychology: green = growth/health, orange = energy/action, gold = luxury/premium, red = urgency/warning, blue = trust/data.
11. Serif font pairs (Cinzel, Cormorant, Playfair) signal luxury, editorial, or culinary domains. Monospace pairs (Space Mono, IBM Plex) signal technical, data, or process domains.
12. Animations are domain signals — use steam for process/brewing, glow for energy/neon, float for ambient/lifestyle. Never animate text content.
