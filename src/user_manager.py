import json
from pathlib import Path

_PROFILES_DIR = Path(__file__).parent.parent / "profiles"


class UserProfile:
    """Loads, exposes, and persists a user profile stored in profiles/<username>.json."""

    def __init__(self, username: str) -> None:
        self._path = _PROFILES_DIR / f"{username}.json"

        if not self._path.exists():
            raise FileNotFoundError(
                f"No profile found for '{username}'. Expected: {self._path}"
            )

        self.username = username
        self._load()

    # ── I/O ──────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        with self._path.open(encoding="utf-8") as f:
            data = json.load(f)

        self.name: str = data["name"]
        self.timezone: str = data["timezone"]
        self.favorite_teams: list[dict] = data.get("favorite_teams", [])
        self.favorite_leagues: list[dict] = data.get("favorite_leagues", [])

    def _save(self) -> None:
        payload = {
            "name": self.name,
            "favorite_teams": self.favorite_teams,
            "favorite_leagues": self.favorite_leagues,
            "timezone": self.timezone,
        }
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    # ── Mutations ─────────────────────────────────────────────────────────────

    def add_team(self, team: dict) -> bool:
        """Add *team* to favorites. Returns False if already present."""
        if any(t["id"] == team["id"] for t in self.favorite_teams):
            return False
        self.favorite_teams.append(team)
        self._save()
        return True

    def add_league(self, league: dict) -> bool:
        """Add *league* to followed competitions. Returns False if already present."""
        if any(l["id"] == league["id"] for l in self.favorite_leagues):
            return False
        self.favorite_leagues.append(league)
        self._save()
        return True

    # ── Convenience ───────────────────────────────────────────────────────────

    @property
    def primary_team(self) -> dict:
        return self.favorite_teams[0] if self.favorite_teams else {}

    def __repr__(self) -> str:
        return f"UserProfile(username={self.username!r}, name={self.name!r})"
