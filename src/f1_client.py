import json
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
        """Return a SportsEvent for a future race, or None if past / unparseable."""
        now = datetime.now(tz=timezone.utc)

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
            return None

        return SportsEvent(
            title=race.get("competition", {}).get("name", "F1 Race"),
            sport="f1",
            category=f"Formula 1 — {_SEASON} Season",
            time=race_time,
            status=race.get("status", "Scheduled"),
        )

    def get_upcoming_events(self) -> list[SportsEvent]:  # DEBUG
        print(f"\n[F1] Calling: {_BASE_URL}/races?season={_SEASON}")
        data = self.get("/races", params={"season": _SEASON})

        print(f"[F1] Raw response:\n{json.dumps(data, indent=2)}")

        events = [e for race in data.get("response", []) if (e := self._parse_race(race))]
        print(f"F1 {_SEASON}: {len(events)} event(s) found")

        if not events:
            self._check_previous_season(data)

        return events

    def _check_previous_season(self, season_2026_data: dict) -> None:
        """If 2026 returned nothing, probe 2025 to distinguish 'no data yet' vs 'off-season'."""
        raw_count = len(season_2026_data.get("response", []))
        print(f"  ->{_SEASON} returned {raw_count} total races (0 upcoming).")
        print(f"  ->Checking {_SEASON - 1} to see if it is still the active season...")

        try:
            fallback = self.get("/races", params={"season": _SEASON - 1})
        except Exception as exc:
            print(f"  ->{_SEASON - 1} check failed: {exc}")
            return

        prev_count = len(fallback.get("response", []))
        if prev_count > 0:
            print(
                f"  ->{_SEASON - 1} season has {prev_count} race(s). "
                f"The {_SEASON} calendar is likely not published yet."
            )
        else:
            print(f"  ->{_SEASON - 1} also empty. Possible API subscription gap.")
