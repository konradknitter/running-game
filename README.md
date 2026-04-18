# running-game — Konrad's Running Dashboard

A personal running dashboard hosted on GitHub Pages. All training data lives in JSON files — no build step, no framework. Push to `main` and the site updates.

## Live site

`https://konradknitter.github.io/running-game/`

## How it works

| File | Purpose |
|---|---|
| `index.html` | Single-page app — fetches data and renders everything |
| `data/config.json` | Athlete profile, PRs, reference paces, notes |
| `data/manifest.json` | Chart weeks + which weeks to display |
| `data/days/YYYY-MM-DD.json` | One file per day with training data |

---

## Adding a completed run

Create `data/days/YYYY-MM-DD.json` (e.g. `data/days/2026-05-03.json`):

```json
{
  "type": "run",
  "name": "Easy Sunday",
  "dist": 12.5,
  "pace": "5:22",
  "hr": "128",
  "tag": "good",
  "tagLabel": "Ideał",
  "stats": [
    ["Dystans",  "12,5 km"],
    ["Czas",     "1h 7m"],
    ["Avg pace", "5:22/km"],
    ["Avg HR",   "128 bpm"],
    ["Typ",      "Easy Z2"]
  ],
  "laps": [
    {"n": "km 1–5",   "pace": "5:30/km", "hr": "120–126", "note": "warm up"},
    {"n": "km 6–12",  "pace": "5:18/km", "hr": "126–132", "note": "steady"}
  ],
  "feedback": "Solid easy run. HR controlled throughout.",
  "rules": [
    {"t": "Takeaway", "b": "Base building on track."}
  ]
}
```

**Tag values:** `good` · `ok` · `warn` · `race`

---

## Adding a planned day

```json
{
  "type": "planned",
  "planned": "10 km easy",
  "detail": "5:10–5:30/km · relaxed"
}
```

Leave out the file entirely for a rest/OFF day — the dashboard renders it automatically.

---

## Adding a new week to the dashboard

In `data/manifest.json`, append to `displayWeeks`:

```json
{
  "start":        "2026-05-04",
  "displayLabel": "04–10 Maj 2026",
  "sectionTitle": "Tydzień · Pn 04.05 — Nd 10.05.2026",
  "kmText":       "52,4 km",
  "kmSubText":    null
}
```

`start` must be a **Monday** (`YYYY-MM-DD`). The dashboard loads 7 days from that date automatically.

---

## Updating the mileage chart

In `data/manifest.json`, append to `chartWeeks`:

```json
{"label": "28.04–03.05", "km": 52.4}
```

Add `"partial": true` for the current in-progress week (renders lighter bar).

---

## Updating PRs or reference paces

Edit `data/config.json` — the `prs` and `paces` arrays.

---

## Deployment

Push any change to `main`. GitHub Actions (`.github/workflows/deploy-pages.yml`) deploys automatically — no build step needed.

```
git add data/days/2026-05-03.json
git commit -m "Add Sunday easy run 03.05"
git push
```

Site is live within ~30 seconds.
