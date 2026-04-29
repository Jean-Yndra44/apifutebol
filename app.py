from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.f1_client import F1Client
from src.football_client import FootballClient
from src.models import SportsEvent
from src.user_manager import UserProfile

_PROFILES_DIR = Path("profiles")
_PLACEHOLDER = "— select —"
_SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")
_SEASON = 2026

# All 12 API-Sports categories.
# status: "live" = full integration | "f1" = mock data available | "wip" = not yet integrated
_SPORTS: list[dict] = [
    {"name": "Football",          "icon": "⚽", "status": "live"},
    {"name": "Formula 1",         "icon": "🏎️", "status": "f1"},
    {"name": "Basketball",        "icon": "🏀", "status": "wip"},
    {"name": "Baseball",          "icon": "⚾", "status": "wip"},
    {"name": "Ice Hockey",        "icon": "🏒", "status": "wip"},
    {"name": "American Football", "icon": "🏈", "status": "wip"},
    {"name": "Rugby League",      "icon": "🏉", "status": "wip"},
    {"name": "Rugby Union",       "icon": "🏉", "status": "wip"},
    {"name": "Volleyball",        "icon": "🏐", "status": "wip"},
    {"name": "Handball",          "icon": "🤾", "status": "wip"},
    {"name": "Cricket",           "icon": "🏏", "status": "wip"},
    {"name": "Tennis",            "icon": "🎾", "status": "wip"},
]

_SPORT_ICON: dict[str, str] = {s["name"].lower().replace(" ", "_"): s["icon"] for s in _SPORTS}
_SPORT_ICON.update({"football": "⚽", "f1": "🏎️"})

_F1_LEAGUE = {"id": 9001, "name": "F1 2024 Season", "sport": "f1"}


# ── Cached API helpers ─────────────────────────────────────────────────────

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
        data = FootballClient().get("/teams", params={"league": league_id, "season": _SEASON})
        return sorted(data.get("response", []), key=lambda t: t["team"]["name"])
    except Exception:
        return []


# ── Profile-aware event fetching ───────────────────────────────────────────

def fetch_all_events(profile: UserProfile) -> tuple[list[SportsEvent], list[str]]:
    """Query only the teams and leagues the user actually follows."""
    events: list[SportsEvent] = []
    errors: list[str] = []
    seen: set[tuple] = set()

    def add_unique(new_events: list[SportsEvent]) -> None:
        for e in new_events:
            key = (e.time, e.title)
            if key not in seen:
                seen.add(key)
                events.append(e)

    football_leagues = [l for l in profile.favorite_leagues if l.get("sport") == "football"]
    football_teams   = [t for t in profile.favorite_teams   if t.get("sport") == "football"]
    f1_entries       = [l for l in profile.favorite_leagues if l.get("sport") == "f1"]

    if football_leagues or football_teams:
        try:
            client = FootballClient()
            for league in football_leagues:
                add_unique(client.get_upcoming_events(league_id=league["id"]))
            for team in football_teams:
                add_unique(client.get_upcoming_events(team_id=team["id"]))
        except Exception as exc:
            errors.append(f"FootballClient: {exc}")

    if f1_entries:
        try:
            add_unique(F1Client().get_upcoming_events())
        except Exception as exc:
            errors.append(f"F1Client: {exc}")

    return sorted(events), errors


def events_to_dataframe(events: list[SportsEvent]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Sport": _SPORT_ICON.get(e.sport, e.sport) + " " + e.sport.upper(),
            "Time (BRT)": e.time.astimezone(_SAO_PAULO_TZ).strftime("%Y-%m-%d %H:%M"),
            "Category": e.category,
            "Event": e.title,
            "Status": e.status,
        }
        for e in events
    ])


# ── Debug helpers ─────────────────────────────────────────────────────────

def _compute_debug(events: list[SportsEvent], profile: UserProfile) -> list[str]:
    """Return sidebar captions for followed sports that returned zero events."""
    fetched = {e.sport for e in events}
    msgs = []

    follows_football = (
        any(t.get("sport") == "football" for t in profile.favorite_teams) or
        any(l.get("sport") == "football" for l in profile.favorite_leagues)
    )
    follows_f1 = any(l.get("sport") == "f1" for l in profile.favorite_leagues)

    if follows_football and "football" not in fetched:
        msgs.append(f"Checked Football for {_SEASON} — No upcoming events found in the next 7 days.")
    if follows_f1 and "f1" not in fetched:
        msgs.append(f"Checked Formula 1 for {_SEASON} — No upcoming events found in the next 7 days.")

    return msgs


# ── Sidebar sections ───────────────────────────────────────────────────────

def render_following(profile: UserProfile) -> None:
    st.sidebar.subheader("📋 Following")

    shown = False

    for team in profile.favorite_teams:
        icon = _SPORT_ICON.get(team.get("sport", ""), "🏅")
        st.sidebar.markdown(f"⭐ {icon} {team['name']}")
        shown = True

    for league in profile.favorite_leagues:
        icon = _SPORT_ICON.get(league.get("sport", ""), "🏆")
        st.sidebar.markdown(f"⭐ {icon} {league['name']}")
        shown = True

    if not shown:
        st.sidebar.caption("Nothing followed yet — use the finder below.")


def render_find_new_team(profile: UserProfile) -> None:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Find New Team")

    # Step 0 — Sport
    sport_labels = [f"{s['icon']} {s['name']}" for s in _SPORTS]
    selected_label = st.sidebar.selectbox(
        "Sport", [_PLACEHOLDER] + sport_labels, key="sel_sport"
    )
    if selected_label == _PLACEHOLDER:
        return

    sport = next(s for s in _SPORTS if f"{s['icon']} {s['name']}" == selected_label)

    # ── WIP sports ────────────────────────────────────────────────────────────
    if sport["status"] == "wip":
        st.sidebar.info("🛠️ Work in Progress: Integration for this sport is coming soon!")
        return

    # ── Formula 1 (mock data) ─────────────────────────────────────────────────
    if sport["status"] == "f1":
        st.sidebar.info(
            "🛠️ Work in Progress: Live F1 data coming soon. Mock data is active."
        )
        already = any(l.get("sport") == "f1" for l in profile.favorite_leagues)
        if already:
            st.sidebar.success("⭐ Already following F1 2024 Season")
        elif st.sidebar.button("🏎️ Follow F1 2024 Season", key="btn_f1"):
            profile.add_league(_F1_LEAGUE)
            st.session_state["_note"] = ("success", "Now following **F1 2024 Season**!")
            st.rerun()
        return

    # ── Football — cascading dropdowns ────────────────────────────────────────

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

    already_league = any(l["id"] == league_id for l in profile.favorite_leagues)
    if already_league:
        st.sidebar.success(f"⭐ Already following {league_name}")
    elif st.sidebar.button("🏆 Follow this Competition", key="btn_league"):
        profile.add_league({"id": league_id, "name": league_name, "sport": "football"})
        st.session_state["_note"] = ("success", f"Now following **{league_name}**!")
        st.rerun()

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

    tid = team_map[team_name]["team"]["id"]
    already_team = any(t["id"] == tid for t in profile.favorite_teams)
    if already_team:
        st.sidebar.success(f"⭐ Already following {team_name}")
    elif st.sidebar.button("⚽ Follow this Team", key="btn_team"):
        profile.add_team({"id": tid, "name": team_name, "sport": "football"})
        st.session_state["_note"] = ("success", f"Added **{team_name}** to favorites!")
        st.rerun()


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(page_title="Sports Dashboard", page_icon="🏆", layout="wide")

    st.sidebar.title("🏆 Sports Dashboard")
    profiles = [p.stem for p in sorted(_PROFILES_DIR.glob("*.json"))]
    if not profiles:
        st.sidebar.error("No profiles found in /profiles.")
        st.stop()

    selected = st.sidebar.selectbox("Select user", profiles)
    profile = UserProfile(selected)

    if "_note" in st.session_state:
        level, msg = st.session_state.pop("_note")
        (st.sidebar.success if level == "success" else st.sidebar.info)(msg)

    render_following(profile)

    for msg in st.session_state.get("_debug", []):
        st.sidebar.caption(f"🔍 {msg}")

    render_find_new_team(profile)

    # Main area
    st.title(f"Welcome, {profile.name}!")
    st.caption(f"Timezone: {profile.timezone}")
    st.subheader("Upcoming Events — Your Sports")

    if st.button("Fetch Events", type="primary"):
        with st.spinner("Fetching from your followed teams and leagues..."):
            events, errors = fetch_all_events(profile)

        st.session_state["_debug"] = _compute_debug(events, profile)

        for err in errors:
            st.warning(f"Skipped: {err}")

        if events:
            st.dataframe(events_to_dataframe(events), use_container_width=True, hide_index=True)
            st.caption(f"{len(events)} event(s) matched your profile.")
        else:
            st.info(
                "No upcoming events found. "
                "Follow some teams or leagues in the sidebar first!"
            )
    else:
        st.info("Press **Fetch Events** to load upcoming events for your followed teams and leagues.")


if __name__ == "__main__":
    main()
