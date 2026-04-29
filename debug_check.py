"""Live 2026 API verification — run with: python debug_check.py"""
from src.f1_client import F1Client
from src.football_client import FootballClient

PALMEIRAS_ID = 121
BRASILEIRAO_ID = 71

print("=" * 60)
print(f"LIVE API CHECK — Season 2026")
print("=" * 60)

# ── F1 ────────────────────────────────────────────────────────────────────
print("\n>>> F1")
try:
    f1_events = F1Client().get_upcoming_events()
except Exception as exc:
    print(f"F1 client error: {exc}")
    f1_events = []

# ── Football ──────────────────────────────────────────────────────────────
print("\n>>> Football — Brasileirão Série A (league 71)")
try:
    fb = FootballClient()
    bra_events = fb.get_upcoming_events(league_id=BRASILEIRAO_ID)
except Exception as exc:
    print(f"Football (league) client error: {exc}")
    bra_events = []

print("\n>>> Football — Palmeiras (team 121)")
try:
    palm_events = fb.get_upcoming_events(team_id=PALMEIRAS_ID)
except Exception as exc:
    print(f"Football (team) client error: {exc}")
    palm_events = []

# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"F1 2026             : {len(f1_events)} event(s) found")
print(f"Football 2026 (BRA) : {len(bra_events)} event(s) found")
print(f"Football 2026 (PAL) : {len(palm_events)} event(s) found")
print("=" * 60)
