# Frontend — Interactive Prototype

`index.html` is a **self-contained, static prototype** — plain HTML/CSS/JS,
no build step, no npm install required. Just open it in a browser.

It uses:
- **Leaflet** (map) + **leaflet.heat** (heatmap layer) — loaded from cdnjs
- **Chart.js** (dashboard charts) — loaded from cdnjs
- A synthetic in-memory dataset of 90 crime cases generated on page load,
  mapped onto real Karnataka district/station coordinates — **not** real
  case data.

## What it's for
This is a demo/pitch prototype: login, dashboard, live map (markers /
heatmap / density hotspots), Criminal Search, criminal network view, a
rule-based Crime & Safety Assistant chatbot, and a predictions/hotspot
module — all computed client-side from the in-memory dataset.

## What it is NOT
It is not connected to `../backend`. The chatbot in here is a
deterministic JavaScript analytics engine that *simulates* what the real
FastAPI + PostgreSQL + RAG + LLM pipeline (see `../backend/app/routes/chatbot_rag.py`)
should produce once that backend actually exists and is wired up.

## Relationship to the team's real React app
Your team's actual frontend (per the earlier uploaded `package.json` /
`vite.config.js`) is a separate React + Vite + Tailwind project
(`ksp-crime-visualization`). This prototype is **not** that project and
doesn't replace it — treat this as a design/logic reference (page
structure, chatbot intents, map modes, search filters) to reimplement as
React components against the real backend, not as a drop-in replacement
for the real app.
