from dataclasses import dataclass
from datetime import datetime


@dataclass(order=True)
class SportsEvent:
    time: datetime      # first field so dataclass ordering sorts by time
    title: str
    sport: str
    category: str
    status: str
