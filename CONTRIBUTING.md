# Contributing Guide

Welcome to the project. Follow the steps below to get your environment running and pick up a challenge.

---

## 1. Clone the repo

```bash
git clone https://github.com/Jean-Yndra44/apifutebol.git
cd apifutebol
```

---

## 2. Set up your `.env` file

The `.env` file holds your personal API credentials and is **never committed to Git**.

```bash
cp .env.example .env
```

Open `.env` and fill in your key:

```
FOOTBALL_API_KEY=your_actual_key_here
FOOTBALL_API_HOST=v3.football.api-sports.io
```

Get a free API key at [api-football.com](https://www.api-football.com).
The free tier allows **100 requests/day** and is locked to **seasons 2022–2024** (see the API Limits section below).

---

## 3. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

## 4. Run the app

```bash
# Web dashboard (Streamlit)
streamlit run app.py --server.headless true

# Terminal dashboard
python dashboard.py --user jean

# Live API diagnostics
python debug_check.py
```

---

## Architecture: The Normalization Engine

The project uses a **multi-sport normalization engine** so that every sport feeds into a single unified table. Before adding anything new, read these four files in order:

| File | Role |
|---|---|
| `src/models.py` | Defines `SportsEvent` — the single data format every sport must produce |
| `src/base_client.py` | Abstract base class `BaseSportClient` — enforces the `get_upcoming_events()` contract |
| `src/football_client.py` | Live implementation: API-Football v3, returns `list[SportsEvent]` |
| `src/f1_client.py` | Live implementation: API-Sports F1, returns `list[SportsEvent]` |

Every sport adapter follows the same pattern:

```python
# src/your_sport_client.py
from src.base_client import BaseSportClient
from src.models import SportsEvent

class YourSportClient(BaseSportClient):
    def get_upcoming_events(self) -> list[SportsEvent]:
        # call your API, parse the response
        return [SportsEvent(title=..., sport=..., category=..., time=..., status=...)]
```

Once your client exists, add it to `_ACTIVE_CLIENTS` in `app.py` and `dashboard.py` — the rest of the pipeline picks it up automatically.

---

## API Limits (Free Tier)

The free plan has hard constraints that shape how the clients are built:

| Constraint | Detail |
|---|---|
| Season cap | Seasons 2025+ are blocked — all queries use **season=2024** |
| `next` / `last` params | Blocked on free tier — the clients fetch the full season and slice the last 5 results client-side |
| `status=NS` | Returns 0 for a completed season — do not use it as a filter |
| Daily request limit | 100 requests/day — all API calls in `app.py` are wrapped with `@st.cache_data(ttl=3600)` |
| F1 season cap | Same restriction — `f1_client.py` targets 2024 and shows the last 5 completed races |

To verify what the API is actually returning, run:

```bash
python debug_check.py
```

---

## Your Challenge

Pick one of the two tracks below, create a branch, and open a PR against `main`.

### Track A — UI: Cards and Team Logos

The current Streamlit table is functional but plain. Improve it:

```bash
git checkout -b feature/ui-cards
```

- Use `st.columns()` to display each event as a card instead of a table row.
- Pull the team logo from the fixture data (`teams.home.logo`, `teams.away.logo`) and render it with `st.image()`.
- The logo URL is already present in the API response — you do not need extra requests.

**Starting point:** `app.py` → `events_to_dataframe()` and the `render_*` functions in the sidebar.

---

### Track B — New Sport Adapter: NBA

Add a Basketball client using the API-Sports NBA endpoint.

```bash
git checkout -b feature/nba-adapter
```

1. Create `src/nba_client.py` inheriting from `BaseSportClient`.
2. The NBA API lives at `https://v2.nba.api-sports.io` — same key, different host header (`x-rapidapi-host: v2.nba.api-sports.io`).
3. Use the `/games` endpoint with `season=2024`.
4. Map each game to a `SportsEvent` with `sport="basketball"`.
5. Add `NBAClient` to `_ACTIVE_CLIENTS` in `app.py` and `dashboard.py`.
6. Add `"basketball": "🏀"` to the `SPORT_ICONS` / `_SPORT_ICON` dictionaries in `app.py`.

**Starting point:** `src/f1_client.py` is the cleanest template — copy its structure and swap the endpoint.

---

## Quick Reference

| Command | Purpose |
|---|---|
| `git status` | Check what files have changed |
| `git add <file>` | Stage a file for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push -u origin <branch>` | Push a new branch to GitHub |
| `python debug_check.py` | Verify live API responses and request counts |
