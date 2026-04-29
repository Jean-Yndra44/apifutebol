import os
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from src.base_client import BaseSportClient
from src.models import SportsEvent

load_dotenv()

_BASE_URL = "https://v3.football.api-sports.io"
_SEASON = 2024  # free tier cap: 2022–2024; next/last params blocked
_LAST_N = 5     # how many recent matches to return per team/league


class FootballClient(BaseSportClient):
    """API-Football v3 client, normalised to SportsEvent."""

    def __init__(self) -> None:
        api_key = os.getenv("FOOTBALL_API_KEY")
        api_host = os.getenv("FOOTBALL_API_HOST", "v3.football.api-sports.io")

        if not api_key:
            raise ValueError(
                "FOOTBALL_API_KEY not set. Copy .env.example to .env and add your key."
            )

        self._headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host,
        }

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{_BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self._headers, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(
                f"API request to '{endpoint}' failed "
                f"[{response.status_code}]: {response.text}"
            )

        return response.json()

    # ── Parsing ───────────────────────────────────────────────────────────────

    def _parse_fixtures(self, data: dict) -> list[SportsEvent]:
        events = []
        for entry in data.get("response", []):
            fixture = entry["fixture"]
            league = entry["league"]
            teams = entry["teams"]
            events.append(SportsEvent(
                title=f"{teams['home']['name']} vs {teams['away']['name']}",
                sport="football",
                category=league["name"],
                time=datetime.fromisoformat(fixture["date"]).astimezone(timezone.utc),
                status=fixture["status"]["long"],
            ))
        return events

    # ── BaseSportClient interface ─────────────────────────────────────────────

    def get_upcoming_events(  # DEBUG
        self,
        *,
        league_id: int | None = None,
        team_id: int | None = None,
    ) -> list[SportsEvent]:
        """Fetch all fixtures for _SEASON, then return the _LAST_N most recent.

        Free-tier constraints:
          - Only seasons 2022-2024 are accessible.
          - 'next' and 'last' query params are blocked — slice client-side instead.
          - 'status=NS' returns 0 for a completed season; omit it entirely.
        """
        params: dict = {"season": _SEASON}
        if league_id is not None:
            params["league"] = league_id
        if team_id is not None:
            params["team"] = team_id

        print(f"[Football] Calling: {_BASE_URL}/fixtures?{urlencode(params)}")
        data = self.get("/fixtures", params=params)
        all_events = self._parse_fixtures(data)

        label = f"league={league_id}" if league_id else f"team={team_id}"
        print(f"Football {_SEASON} ({label}): {len(all_events)} total fixtures — returning last {_LAST_N}")

        # Sort descending by time → take first _LAST_N → caller re-sorts ascending
        return sorted(all_events, reverse=True)[:_LAST_N]

    def get_leagues(self) -> dict:  # kept for app.py backwards compatibility
        """Kept for backwards compatibility with existing code."""
        return self.get("/leagues")
