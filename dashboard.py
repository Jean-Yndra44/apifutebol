import argparse

from src.f1_client import F1Client
from src.football_client import FootballClient
from src.models import SportsEvent
from src.user_manager import UserProfile

_ACTIVE_CLIENTS = [
    FootballClient,
    F1Client,
]


def fetch_all_events() -> list[SportsEvent]:
    events: list[SportsEvent] = []
    for ClientClass in _ACTIVE_CLIENTS:
        try:
            client = ClientClass()
            events.extend(client.get_upcoming_events())
        except Exception as exc:
            print(f"[{ClientClass.__name__}] skipped — {exc}")
    return sorted(events)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-sport personal dashboard.")
    parser.add_argument("--user", required=True, help="Profile name to load (e.g. jean)")
    args = parser.parse_args()

    profile = UserProfile(args.user)
    print(f"Welcome, {profile.name}! Loading your dashboard...\n")

    events = fetch_all_events()

    if not events:
        print("No upcoming events found.")
        return

    print(f"{'Time (UTC)':<22} {'Sport':<10} {'Category':<28} {'Title'}")
    print("-" * 90)
    for event in events:
        time_str = event.time.strftime("%Y-%m-%d %H:%M")
        print(f"{time_str:<22} {event.sport:<10} {event.category:<28} {event.title}")


if __name__ == "__main__":
    main()
