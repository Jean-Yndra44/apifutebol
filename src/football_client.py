import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from src.base_client import BaseSportClient
from src.models import SportsEvent

load_dotenv()

_BASE_URL = "https://v3.football.api-sports.io"


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

    def get_upcoming_events(
        self,
        *,
        league_id: int | None = None,
        team_id: int | None = None,
        next: int = 10,
    ) -> list[SportsEvent]:
        """Fetch upcoming fixtures, optionally filtered by league or team.

        When neither is supplied the API returns fixtures globally (free-tier
        may return an empty list without a filter — always prefer passing one).
        """
        params: dict = {"next": next}
        if league_id is not None:
            params.update({"league": league_id, "season": 2024})
        if team_id is not None:
            params["team"] = team_id
        return self._parse_fixtures(self.get("/fixtures", params=params))

    def get_leagues(self) -> dict:
        """Kept for backwards compatibility with existing code."""
        return self.get("/leagues")
