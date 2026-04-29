from pathlib import Path

import pandas as pd
import streamlit as st

from src.user_manager import UserProfile

_PROFILES_DIR = Path("profiles")


def list_profiles() -> list[str]:
    return [p.stem for p in sorted(_PROFILES_DIR.glob("*.json"))]


def main() -> None:
    st.set_page_config(page_title="Football Dashboard", page_icon="⚽", layout="wide")

    # ── Sidebar ──────────────────────────────────────────────────────────────
    st.sidebar.title("⚽ Football Dashboard")
    profiles = list_profiles()

    if not profiles:
        st.sidebar.error("No profiles found in /profiles.")
        st.stop()

    selected = st.sidebar.selectbox("Select user", profiles)
    profile = UserProfile(selected)

    # ── Main area ─────────────────────────────────────────────────────────────
    st.title(f"Welcome, {profile.name}!")
    st.caption(f"Timezone: {profile.timezone}")

    st.subheader("Favorite Teams")
    df = pd.DataFrame(profile.favorite_teams)[["id", "name", "sport"]]
    df.columns = ["ID", "Team", "Sport"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    if st.button("Fetch Latest Results", type="primary"):
        st.info("API integration coming next — stay tuned!")


if __name__ == "__main__":
    main()
