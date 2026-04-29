from datetime import datetime, timezone

from src.base_client import BaseSportClient
from src.models import SportsEvent

_MOCK_EVENTS = [
    {
        "title": "Monaco Grand Prix",
        "category": "Formula 1 — 2024 Season",
        "time": datetime(2024, 5, 26, 13, 0, tzinfo=timezone.utc),
        "status": "Scheduled",
    },
    {
        "title": "Canadian Grand Prix",
        "category": "Formula 1 — 2024 Season",
        "time": datetime(2024, 6, 9, 18, 0, tzinfo=timezone.utc),
        "status": "Scheduled",
    },
    {
        "title": "Spanish Grand Prix",
        "category": "Formula 1 — 2024 Season",
        "time": datetime(2024, 6, 23, 13, 0, tzinfo=timezone.utc),
        "status": "Scheduled",
    },
]


class F1Client(BaseSportClient):
    """Mock F1 client — returns static dummy data.

    Replace _MOCK_EVENTS with a real API call (e.g. Ergast / OpenF1)
    when a live integration is ready.
    """

    def get_upcoming_events(self) -> list[SportsEvent]:
        return [
            SportsEvent(
                title=e["title"],
                sport="f1",
                category=e["category"],
                time=e["time"],
                status=e["status"],
            )
            for e in _MOCK_EVENTS
        ]
