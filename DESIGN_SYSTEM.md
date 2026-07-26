# Design System — "Case-File Dossier" Theme

Pulled directly from `frontend/index.html`'s CSS variables — this is what
the prototype actually uses, not a re-guess. Use this as the single source
of truth if the real React frontend is built to match.

## Color tokens

| Token | Hex | Use |
|---|---|---|
| `--ink-950` | `#080B10` | Page background |
| `--ink-900` | `#0B0F16` | Panel/card background |
| `--ink-800` | `#121826` | Filter bars, table hover, secondary surfaces |
| `--ink-700` | `#1A2233` | Borders, table row dividers |
| `--ink-600` | `#232D42` | Panel borders, chart gridlines |
| `--brass-400` | `#E4C567` | Primary accent (headings, KPI numbers, active nav) |
| `--brass-500` | `#C9A227` | Primary buttons, "case tab" label background |
| `--brass-600` | `#A6821C` | Darker brass accents |
| `--alert-400` | `#E0685F` | Alert text (Undetected status, warnings) |
| `--alert-500` | `#C1443C` | Alert accents, highest-risk highlighting |
| `--alert-600` | `#9A332C` | Darkest alert accent |
| `--teal` | `#3FA79A` | Secondary accent (Charge Sheeted status, "safe" indicators) |
| `--paper-100` | `#F3EFE6` | Primary body text |
| `--paper-300` | `#D9D3C4` | Secondary/muted body text |
| `--mute-400` | `#7A8290` | Labels, placeholder text |
| `--mute-500` | `#5C6474` | Faintest text, disabled states |

Status-pill colors (used consistently across map markers, table pills,
hotspot bubbles):
- Under Investigation → brass (`--brass-400`)
- Charge Sheeted → teal (`--teal`)
- Closed → mute (`--mute-400`)
- Undetected → alert (`--alert-400`)

Density/heatmap gradient (green→red, used in map hotspot mode):
Low `#4CAF50` → Moderate `#E4C567` → High `#E08A3F` → Very High `#C1443C`

## Typography

| Role | Font | Where |
|---|---|---|
| Display / headings | **Oswald** (400/500/600/700) | `h1`–`h4`, section titles |
| Body | **Inter** (400/500/600/700) | Paragraphs, labels, buttons |
| Mono / data | **JetBrains Mono** (400/500) | Case numbers, coordinates, timestamps, KPI figures, status pills |

Loaded via Google Fonts in `frontend/index.html`'s `<head>`.

## Signature component: the "case tab"
A small brass-colored label with a clipped bottom-right corner
(`clip-path: polygon(0 0, 100% 0, 92% 100%, 0% 100%)`), used as a section
header on every panel — e.g. `AI INSIGHTS · AUTO-GENERATED`,
`CRIMINAL SEARCH — FIELDS SOURCED FROM DATASET`. This is the one
recurring visual motif that should carry over if rebuilt in React —
it's what makes panels read as case-file folders rather than generic
dashboard cards.

## Layout patterns
- Sidebar: 220px fixed width, dark surface, 3-letter monospace "nav codes"
  (DSH / MAP / REC / NET / BOT / PRD) instead of icons — deliberately, to
  reinforce the case-file/stamp aesthetic over a typical icon-based nav.
- Panels: 1px `--ink-600` border, subtle top highlight
  (`box-shadow: 0 1px 0 rgba(228,197,103,0.06)`), 2px border radius (sharp,
  not rounded — matches the "official document" feel).
- KPI cards: large JetBrains Mono numerals in brass/teal/alert depending on
  metric type, small inline SVG icon in the top-right corner.
