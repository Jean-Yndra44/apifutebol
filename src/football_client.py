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

    def get_upcoming_events(self, next: int = 10) -> list[SportsEvent]:
        """Return the next *next* fixtures as normalised SportsEvent objects."""
        data = self.get("/fixtures", params={"next": next})
        events = []

        for entry in data.get("response", []):
            fixture = entry["fixture"]
            league = entry["league"]
            teams = entry["teams"]

            title = f"{teams['home']['name']} vs {teams['away']['name']}"
            event_time = datetime.fromisoformat(fixture["date"]).astimezone(timezone.utc)
            status = fixture["status"]["long"]

            events.append(SportsEvent(
                title=title,
                sport="football",
                category=league["name"],
                time=event_time,
                status=status,
            ))

        return events

    def get_leagues(self) -> dict:
        """Kept for backwards compatibility with existing code."""
        return self.get("/leagues")
