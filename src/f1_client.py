import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from src.base_client import BaseSportClient
from src.models import SportsEvent

load_dotenv()

_BASE_URL = "https://v1.formula-1.api-sports.io"
_SEASON = 2026


class F1Client(BaseSportClient):
    """API-Sports Formula 1 client for the 2026 season.

    Uses the same API key as FootballClient — API-Sports keys are cross-sport.
    Host header switches to v1.formula-1.api-sports.io.
    """

    def __init__(self) -> None:
        api_key = os.getenv("FOOTBALL_API_KEY")
        if not api_key:
            raise ValueError(
                "FOOTBALL_API_KEY not set. The same key grants access to the F1 API."
            )
        self._headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "v1.formula-1.api-sports.io",
        }

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{_BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self._headers, params=params, timeout=10)
        if response.status_code != 200:
            raise RuntimeError(
                f"F1 API '{endpoint}' failed [{response.status_code}]: {response.text}"
            )
        return response.json()

    def _parse_race(self, race: dict) -> SportsEvent | None:
        """Return a SportsEvent for a future race, or None if past / unparseable."""
        now = datetime.now(tz=timezone.utc)

        # API-Sports may send a UNIX timestamp or an ISO-8601 date string.
        if ts := race.get("timestamp"):
            race_time = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        elif raw := race.get("date"):
            try:
                race_time = datetime.fromisoformat(
                    str(raw).replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            except (ValueError, TypeError):
                return None
        else:
            return None

        if race_time <= now:
            return None  # skip completed races

        return SportsEvent(
            title=race.get("competition", {}).get("name", "F1 Race"),
            sport="f1",
            category=f"Formula 1 — {_SEASON} Season",
            time=race_time,
            status=race.get("status", "Scheduled"),
        )

    def get_upcoming_events(self) -> list[SportsEvent]:
        data = self.get("/races", params={"season": _SEASON})
        events = []
        for race in data.get("response", []):
            if event := self._parse_race(race):
                events.append(event)
        return events
