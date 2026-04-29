from pathlib import Path

import pandas as pd
import streamlit as st

from src.f1_client import F1Client
from src.football_client import FootballClient
from src.models import SportsEvent
from src.user_manager import UserProfile

_PROFILES_DIR = Path("profiles")

_ACTIVE_CLIENTS = [
    FootballClient,
    F1Client,
]

SPORT_ICONS = {
    "football": "⚽",
    "f1": "🏎️",
}


def list_profiles() -> list[str]:
    return [p.stem for p in sorted(_PROFILES_DIR.glob("*.json"))]


def fetch_all_events() -> tuple[list[SportsEvent], list[str]]:
    events: list[SportsEvent] = []
    errors: list[str] = []
    for ClientClass in _ACTIVE_CLIENTS:
        try:
            events.extend(ClientClass().get_upcoming_events())
        except Exception as exc:
            errors.append(f"{ClientClass.__name__}: {exc}")
    return sorted(events), errors


def events_to_dataframe(events: list[SportsEvent]) -> pd.DataFrame:
    rows = [
        {
            "Sport": SPORT_ICONS.get(e.sport, e.sport) + " " + e.sport.upper(),
            "Time (UTC)": e.time.strftime("%Y-%m-%d %H:%M"),
            "Category": e.category,
            "Event": e.title,
            "Status": e.status,
        }
        for e in events
    ]
    return pd.DataFrame(rows)


def main() -> None:
    st.set_page_config(page_title="Sports Dashboard", page_icon="🏆", layout="wide")

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.title("🏆 Sports Dashboard")
    profiles = list_profiles()

    if not profiles:
        st.sidebar.error("No profiles found in /profiles.")
        st.stop()

    selected = st.sidebar.selectbox("Select user", profiles)
    profile = UserProfile(selected)

    st.sidebar.divider()
    st.sidebar.subheader("Favorite Teams")
    for team in profile.favorite_teams:
        icon = SPORT_ICONS.get(team["sport"], "🏅")
        st.sidebar.markdown(f"{icon} **{team['name']}** (ID {team['id']})")

    # ── Main area ─────────────────────────────────────────────────────────────
    st.title(f"Welcome, {profile.name}!")
    st.caption(f"Timezone: {profile.timezone}")

    st.subheader("Upcoming Events — All Sports")

    if st.button("Fetch Events", type="primary"):
        with st.spinner("Fetching events from all sources..."):
            events, errors = fetch_all_events()

        for err in errors:
            st.warning(f"Skipped client — {err}")

        if events:
            df = events_to_dataframe(events)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(events)} event(s) loaded from {len(_ACTIVE_CLIENTS)} source(s).")
        else:
            st.info("No upcoming events found.")
    else:
        st.info("Press **Fetch Events** to load upcoming events across all sports.")


if __name__ == "__main__":
    main()
