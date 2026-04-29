"""Live API verification — run with: python debug_check.py"""
from src.f1_client import F1Client, _SEASON as F1_SEASON
from src.football_client import FootballClient, _SEASON as FB_SEASON

PALMEIRAS_ID = 121
BRASILEIRAO_ID = 71

print("=" * 60)
print(f"LIVE API CHECK — F1 {F1_SEASON} | Football {FB_SEASON}/{FB_SEASON + 1}")
print("=" * 60)

# ── F1 ────────────────────────────────────────────────────────────────────
print("\n>>> F1")
try:
    f1_events = F1Client().get_upcoming_events()
except Exception as exc:
    print(f"F1 client error: {exc}")
    f1_events = []

# ── Football ──────────────────────────────────────────────────────────────
print(f"\n>>> Football — Brasileirao Serie A (league {BRASILEIRAO_ID})")
try:
    fb = FootballClient()
    bra_events = fb.get_upcoming_events(league_id=BRASILEIRAO_ID)
except Exception as exc:
    print(f"Football (league) client error: {exc}")
    bra_events = []

print(f"\n>>> Football — Palmeiras (team {PALMEIRAS_ID})")
try:
    palm_events = fb.get_upcoming_events(team_id=PALMEIRAS_ID)
except Exception as exc:
    print(f"Football (team) client error: {exc}")
    palm_events = []

# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"F1 {F1_SEASON} (Last 5 Races)   : {len(f1_events)} race(s) found")
print(f"Football {FB_SEASON}/{FB_SEASON + 1} (Brasileirao) : {len(bra_events)} fixture(s) found")
print(f"Football {FB_SEASON}/{FB_SEASON + 1} (Palmeiras)   : {len(palm_events)} fixture(s) found")
print("=" * 60)
