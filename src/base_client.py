from abc import ABC, abstractmethod

from src.models import SportsEvent


class BaseSportClient(ABC):
    """Contract every sport client must fulfil.

    Subclasses implement get_upcoming_events() and return a list of
    normalised SportsEvent objects — callers never touch raw API payloads.
    """

    @abstractmethod
    def get_upcoming_events(self) -> list[SportsEvent]:
        ...
