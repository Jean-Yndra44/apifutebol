import json
from pathlib import Path

_PROFILES_DIR = Path(__file__).parent.parent / "profiles"


class UserProfile:
    """Represents a loaded user profile from profiles/<username>.json."""

    def __init__(self, username: str) -> None:
        path = _PROFILES_DIR / f"{username}.json"

        if not path.exists():
            raise FileNotFoundError(
                f"No profile found for '{username}'. "
                f"Expected: {path}"
            )

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        self.username = username
        self.name: str = data["name"]
        self.favorite_teams: list[dict] = data["favorite_teams"]
        self.timezone: str = data["timezone"]

    @property
    def primary_team(self) -> dict:
        """Return the first team in favorite_teams."""
        return self.favorite_teams[0]

    def __repr__(self) -> str:
        return f"UserProfile(username={self.username!r}, name={self.name!r})"
