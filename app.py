from pathlib import Path

import pandas as pd
import streamlit as st

from src.f1_client import F1Client
from src.football_client import FootballClient
from src.models import SportsEvent
from src.user_manager import UserProfile

_PROFILES_DIR = Path("profiles")
_PLACEHOLDER = "— select —"

_ACTIVE_CLIENTS = [FootballClient, F1Client]

SPORT_ICONS = {"football": "⚽", "f1": "🏎️"}


# ── Cached API helpers ─────────────────────────────────────────────────────
# Each function creates its own FootballClient so that the cache layer never
# holds a reference to a stateful object. TTL = 1 h keeps API usage low.

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_countries() -> list[dict]:
    try:
        data = FootballClient().get("/countries")
        return sorted(data.get("response", []), key=lambda c: c["name"])
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_leagues_by_country(country: str) -> list[dict]:
    try:
        data = FootballClient().get("/leagues", params={"country": country, "type": "League"})
        return sorted(data.get("response", []), key=lambda l: l["league"]["name"])
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_teams_by_league(league_id: int) -> list[dict]:
    try:
        data = FootballClient().get("/teams", params={"league": league_id, "season": 2024})
        return sorted(data.get("response", []), key=lambda t: t["team"]["name"])
    except Exception:
        return []


# ── Event helpers ──────────────────────────────────────────────────────────

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
    return pd.DataFrame([
        {
            "Sport": SPORT_ICONS.get(e.sport, e.sport) + " " + e.sport.upper(),
            "Time (UTC)": e.time.strftime("%Y-%m-%d %H:%M"),
            "Category": e.category,
            "Event": e.title,
            "Status": e.status,
        }
        for e in events
    ])


# ── Sidebar sections ───────────────────────────────────────────────────────

def render_following(profile: UserProfile) -> None:
    st.sidebar.subheader("📋 Following")

    shown = False

    for team in profile.favorite_teams:
        icon = SPORT_ICONS.get(team.get("sport", ""), "🏅")
        st.sidebar.markdown(f"{icon} **{team['name']}**")
        shown = True

    for league in profile.favorite_leagues:
        st.sidebar.markdown(f"🏆 **{league['name']}**")
        shown = True

    if not shown:
        st.sidebar.caption("Nothing followed yet — use the finder below.")


def render_find_new_team(profile: UserProfile) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Find New Team")

    # Step 1 — Country
    countries = fetch_countries()
    if not countries:
        st.sidebar.warning("API unavailable. Check your secrets.")
        return

    country = st.sidebar.selectbox(
        "Country",
        [_PLACEHOLDER] + [c["name"] for c in countries],
        key="sel_country",
    )
    if country == _PLACEHOLDER:
        return

    # Step 2 — League
    leagues = fetch_leagues_by_country(country)
    if not leagues:
        st.sidebar.caption(f"No leagues found for {country}.")
        return

    league_map = {l["league"]["name"]: l for l in leagues}
    league_name = st.sidebar.selectbox(
        "League / Competition",
        [_PLACEHOLDER] + list(league_map),
        key="sel_league",
    )
    if league_name == _PLACEHOLDER:
        return

    league = league_map[league_name]
    league_id = league["league"]["id"]

    if st.sidebar.button("🏆 Follow this Competition", key="btn_league"):
        added = profile.add_league({"id": league_id, "name": league_name, "sport": "football"})
        st.session_state["_note"] = (
            "success",
            f"Now following **{league_name}**!" if added else f"Already following **{league_name}**.",
        )
        st.rerun()

    # Step 3 — Team
    teams = fetch_teams_by_league(league_id)
    if not teams:
        st.sidebar.caption("No teams found for this league/season.")
        return

    team_map = {t["team"]["name"]: t for t in teams}
    team_name = st.sidebar.selectbox(
        "Team",
        [_PLACEHOLDER] + list(team_map),
        key="sel_team",
    )
    if team_name == _PLACEHOLDER:
        return

    if st.sidebar.button("⚽ Follow this Team", key="btn_team"):
        tid = team_map[team_name]["team"]["id"]
        added = profile.add_team({"id": tid, "name": team_name, "sport": "football"})
        st.session_state["_note"] = (
            "success",
            f"Added **{team_name}** to favorites!" if added else f"Already following **{team_name}**.",
        )
        st.rerun()


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(page_title="Sports Dashboard", page_icon="🏆", layout="wide")

    # User selector
    st.sidebar.title("🏆 Sports Dashboard")
    profiles = [p.stem for p in sorted(_PROFILES_DIR.glob("*.json"))]
    if not profiles:
        st.sidebar.error("No profiles found in /profiles.")
        st.stop()

    selected = st.sidebar.selectbox("Select user", profiles)
    profile = UserProfile(selected)

    # One-shot notification from previous rerun (add_team / add_league result)
    if "_note" in st.session_state:
        level, msg = st.session_state.pop("_note")
        (st.sidebar.success if level == "success" else st.sidebar.info)(msg)

    render_following(profile)
    render_find_new_team(profile)

    # Main area
    st.title(f"Welcome, {profile.name}!")
    st.caption(f"Timezone: {profile.timezone}")

    st.subheader("Upcoming Events — All Sports")

    if st.button("Fetch Events", type="primary"):
        with st.spinner("Fetching from all sources..."):
            events, errors = fetch_all_events()

        for err in errors:
            st.warning(f"Skipped: {err}")

        if events:
            st.dataframe(events_to_dataframe(events), use_container_width=True, hide_index=True)
            st.caption(f"{len(events)} event(s) from {len(_ACTIVE_CLIENTS)} source(s).")
        else:
            st.info("No upcoming events found.")
    else:
        st.info("Press **Fetch Events** to load upcoming events across all sports.")


if __name__ == "__main__":
    main()
