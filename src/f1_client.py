import json
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from src.base_client import BaseSportClient
from src.models import SportsEvent

load_dotenv()

_BASE_URL = "https://v1.formula-1.api-sports.io"
_SEASON = 2024  # free tier is capped at 2024; all races are past, so show Last 5


class F1Client(BaseSportClient):
    """API-Sports Formula 1 client.

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
        """Parse a race entry — only actual races, not qualifying or practice sessions."""
        if race.get("type") != "Race":
            return None

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

        return SportsEvent(
            title=race.get("competition", {}).get("name", "F1 Race"),
            sport="f1",
            category=f"Formula 1 {_SEASON} — Last Races",
            time=race_time,
            status=race.get("status", "Race Completed"),
        )

    def get_upcoming_events(self) -> list[SportsEvent]:  # DEBUG
        print(f"\n[F1] Calling: {_BASE_URL}/races?season={_SEASON}")
        data = self.get("/races", params={"season": _SEASON})
        print(f"[F1] Raw response:\n{json.dumps(data, indent=2)}")

        all_events = [e for race in data.get("response", []) if (e := self._parse_race(race))]

        # 2024 = free tier; every race is in the past — return the 5 most recent.
        last_5 = sorted(all_events, reverse=True)[:5]
        print(f"F1 {_SEASON}: {len(all_events)} total races — showing last {len(last_5)}")

        if not all_events:
            self._check_previous_season(data)

        return last_5

    def _check_previous_season(self, empty_data: dict) -> None:
        """If the target season returned nothing, probe the prior year for context."""
        raw_count = len(empty_data.get("response", []))
        print(f"  ->{_SEASON} returned {raw_count} races total.")
        prev = _SEASON - 1
        print(f"  ->Checking {prev}...")
        try:
            fallback = self.get("/races", params={"season": prev})
        except Exception as exc:
            print(f"  ->{prev} check failed: {exc}")
            return
        prev_count = len(fallback.get("response", []))
        if prev_count > 0:
            print(f"  ->{prev} has {prev_count} race(s) — possible subscription gap on {_SEASON}.")
        else:
            print(f"  ->{prev} also empty.")
