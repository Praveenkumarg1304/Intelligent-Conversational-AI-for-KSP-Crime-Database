# Frontend — Interactive Prototype

`index.html` is a **self-contained, static prototype** — plain HTML/CSS/JS,
no build step, no npm install required. Just open it in a browser.

It uses:
- **Leaflet** (map) + **leaflet.heat** (heatmap layer) — loaded from cdnjs
- **Chart.js** (dashboard charts) — loaded from cdnjs
- A synthetic in-memory dataset of 90 crime cases generated on page load —
  the exact same data now exported to `../dataset/crime_cases.csv`

## What it's for
Sign-up/sign-in flow, dashboard, live map (markers / heatmap / density
hotspots), Criminal Search, criminal network view, a rule-based Crime &
Safety Assistant chatbot, and a predictions/hotspot module — all computed
client-side from the in-memory dataset.

## What it is NOT
It is not connected to `../backend`. Accounts created via Sign Up exist
only in memory for that browser session (reset on reload) — there's no
real user database. The chatbot is a deterministic JavaScript analytics
engine that *simulates* what the real FastAPI + PostgreSQL + RAG + LLM
pipeline (`../backend/app/routes/chatbot_rag.py`) should produce once that
backend actually exists.

## Relationship to the team's real React app
Your team's actual frontend (per the earlier uploaded `package.json` /
`vite.config.js`) is a separate React + Vite + Tailwind project
(`ksp-crime-visualization`). This prototype doesn't replace it — treat it
as a design/logic reference (see `../design/DESIGN_SYSTEM.md` for the
exact visual tokens) to reimplement as React components against the real
backend.
