import os

import requests
from dotenv import load_dotenv

load_dotenv()

_BASE_URL = "https://v3.football.api-sports.io"


class FootballAPIClient:
    """Thin HTTP wrapper around the API-Football v3 REST API.

    Handles auth headers and response validation so endpoint functions
    (get_leagues, get_fixtures, etc.) only deal with query params and data.
    """

    def __init__(self) -> None:
        api_key = os.getenv("FOOTBALL_API_KEY")
        api_host = os.getenv("FOOTBALL_API_HOST", "v3.football.api-sports.io")

        if not api_key:
            raise ValueError(
                "FOOTBALL_API_KEY not set. Copy .env.example to .env and add your key."
            )

        self._headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host,
        }

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Send a GET request to *endpoint* and return the parsed JSON body.

        Raises RuntimeError on non-200 responses so callers get a clear
        message instead of silently working with error payloads.
        """
        url = f"{_BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self._headers, params=params, timeout=10)

        if response.status_code != 200:
            raise RuntimeError(
                f"API request to '{endpoint}' failed "
                f"[{response.status_code}]: {response.text}"
            )

        return response.json()


# ---------------------------------------------------------------------------
# Endpoint functions — import FootballAPIClient in a new file to add more.
# ---------------------------------------------------------------------------

def get_leagues(client: FootballAPIClient | None = None) -> dict:
    """Return all leagues available in the API."""
    if client is None:
        client = FootballAPIClient()
    return client.get("/leagues")
