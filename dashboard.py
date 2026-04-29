import argparse

from src.user_manager import UserProfile


def main() -> None:
    parser = argparse.ArgumentParser(description="Football API personal dashboard.")
    parser.add_argument("--user", required=True, help="Profile name to load (e.g. jean)")
    args = parser.parse_args()

    profile = UserProfile(args.user)
    team_name = profile.primary_team["name"]

    print(f"Welcome, {profile.name}! Loading your {team_name} dashboard...")


if __name__ == "__main__":
    main()
