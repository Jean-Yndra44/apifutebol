# Contributing Guide

Welcome to the project. Follow the steps below to get your local environment running.

---

## 1. Clone the repo and check out the branch

```bash
git clone https://github.com/Jean-Yndra44/apifutebol.git
cd apifutebol
git checkout feature/initial-setup
```

---

## 2. Set up your `.env` file

The `.env` file holds your personal API credentials and is **never committed to Git**.

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your own key:

```
FOOTBALL_API_KEY=your_actual_key_here
FOOTBALL_API_HOST=v3.football.api-sports.io
```

Get a free API key at [api-football.com](https://www.api-football.com) — the free tier allows 100 requests per day.

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

## 4. Your challenge

Create a new branch and add a function that fetches teams from the **Brasileirão Série A**.

```bash
git checkout -b feature/get-teams
```

In a new file `src/teams.py`, use the `FootballAPIClient` from `src/api_client.py` to write a `get_teams()` function that calls the `/teams` endpoint with:

- `league=71` (Brasileirão Série A)
- `season=2024`

The result should print the name of each team in the league.

**Hint:** look at how `get_leagues()` is structured in `src/api_client.py` — your function will follow the same pattern.

When you're done, push your branch and open a Pull Request against `feature/initial-setup`.

---

## Quick reference

| Command | Purpose |
|---|---|
| `git status` | Check what files have changed |
| `git add <file>` | Stage a file for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push -u origin <branch>` | Push a new branch to GitHub |
