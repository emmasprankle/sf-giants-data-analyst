"""
Source 1: MLB Stats API → Snowflake raw
Pattern: request → parse → loop → save

Pulls SF Giants pitchers' game logs for the current season and loads
two raw tables into Snowflake:
  - raw.players        (one row per pitcher)
  - raw.pitcher_game_logs (one row per pitcher per game)
"""

import os
import json
import requests
import snowflake.connector
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
# Change these without touching any logic below

BASE_URL = "https://statsapi.mlb.com/api/v1"

ENDPOINTS = {
    "roster":   "/teams/{team_id}/roster",
    "player":   "/people/{player_id}",
    "game_log": "/people/{player_id}/stats",
}

GAME_LOG_PARAMS = {
    "stats":    "gameLog",
    "group":    "pitching",
    "season":   "2024",
    "gameType": "R",
}

PLAYER_FIELDS = {
    "id":            "id",
    "full_name":     "fullName",
    "birth_date":    "birthDate",
    "pitch_hand":    "pitchHand.code",
    "bat_side":      "batSide.code",
    "position":      "primaryPosition.abbreviation",
    "mlb_debut":     "mlbDebutDate",
    "active":        "active",
}

GAME_LOG_FIELDS = {
    "game_pk":        "game.gamePk",
    "game_date":      "date",
    "team_id":        "team.id",
    "team_name":      "team.name",
    "is_home":        "isHome",
    "wins":           "stat.wins",
    "losses":         "stat.losses",
    "era":            "stat.era",
    "innings_pitched":"stat.inningsPitched",
    "strikeouts":     "stat.strikeOuts",
    "walks":          "stat.baseOnBalls",
    "hits":           "stat.hits",
    "earned_runs":    "stat.earnedRuns",
    "home_runs":      "stat.homeRuns",
    "whip":           "stat.whip",
    "pitches_thrown": "stat.numberOfPitches",
    "strikes":        "stat.strikes",
}

SF_GIANTS_TEAM_ID = 137


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(endpoint, **params):
    url = BASE_URL + endpoint
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def dig(obj, dotted_key):
    """Traverse a nested dict using a dot-separated key path."""
    for key in dotted_key.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def snowflake_conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="RAW",
    )


# ── Extract ───────────────────────────────────────────────────────────────────

def fetch_pitchers(team_id):
    endpoint = ENDPOINTS["roster"].format(team_id=team_id)
    data = get(endpoint)
    return [
        p["person"]
        for p in data.get("roster", [])
        if p.get("position", {}).get("type") == "Pitcher"
    ]


def fetch_player(player_id):
    endpoint = ENDPOINTS["player"].format(player_id=player_id)
    data = get(endpoint)
    person = data.get("people", [{}])[0]
    return {col: dig(person, path) for col, path in PLAYER_FIELDS.items()}


def fetch_game_logs(player_id):
    endpoint = ENDPOINTS["game_log"].format(player_id=player_id)
    data = get(endpoint, **GAME_LOG_PARAMS)
    rows = []
    stats = data.get("stats", [])
    for split in (stats[0].get("splits", []) if stats else []):
        row = {col: dig(split, path) for col, path in GAME_LOG_FIELDS.items()}
        row["player_id"] = player_id
        rows.append(row)
    return rows


# ── Load ──────────────────────────────────────────────────────────────────────

DDL_PLAYERS = """
CREATE TABLE IF NOT EXISTS RAW.PLAYERS (
    player_id       INTEGER,
    full_name       VARCHAR,
    birth_date      VARCHAR,
    pitch_hand      VARCHAR,
    bat_side        VARCHAR,
    position        VARCHAR,
    mlb_debut       VARCHAR,
    active          BOOLEAN,
    _loaded_at      TIMESTAMP_NTZ
)
"""

DDL_GAME_LOGS = """
CREATE TABLE IF NOT EXISTS RAW.PITCHER_GAME_LOGS (
    player_id       INTEGER,
    game_pk         INTEGER,
    game_date       VARCHAR,
    team_id         INTEGER,
    team_name       VARCHAR,
    is_home         BOOLEAN,
    wins            INTEGER,
    losses          INTEGER,
    era             FLOAT,
    innings_pitched FLOAT,
    strikeouts      INTEGER,
    walks           INTEGER,
    hits            INTEGER,
    earned_runs     INTEGER,
    home_runs       INTEGER,
    whip            FLOAT,
    pitches_thrown  INTEGER,
    strikes         INTEGER,
    _loaded_at      TIMESTAMP_NTZ
)
"""


def load_players(cur, players, loaded_at):
    cur.execute("TRUNCATE TABLE IF EXISTS RAW.PLAYERS")
    for p in players:
        cur.execute(
            """
            INSERT INTO RAW.PLAYERS VALUES (
                %(player_id)s, %(full_name)s, %(birth_date)s,
                %(pitch_hand)s, %(bat_side)s, %(position)s,
                %(mlb_debut)s, %(active)s, %(loaded_at)s
            )
            """,
            {**p, "loaded_at": loaded_at},
        )
    print(f"  Loaded {len(players)} players")


def load_game_logs(cur, game_logs, loaded_at):
    cur.execute("TRUNCATE TABLE IF EXISTS RAW.PITCHER_GAME_LOGS")
    for row in game_logs:
        cur.execute(
            """
            INSERT INTO RAW.PITCHER_GAME_LOGS VALUES (
                %(player_id)s, %(game_pk)s, %(game_date)s,
                %(team_id)s, %(team_name)s, %(is_home)s,
                %(wins)s, %(losses)s, %(era)s, %(innings_pitched)s,
                %(strikeouts)s, %(walks)s, %(hits)s, %(earned_runs)s,
                %(home_runs)s, %(whip)s, %(pitches_thrown)s, %(strikes)s,
                %(loaded_at)s
            )
            """,
            {**row, "loaded_at": loaded_at},
        )
    print(f"  Loaded {len(game_logs)} game log rows")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    loaded_at = datetime.now(timezone.utc)

    print("Fetching SF Giants pitchers roster...")
    pitchers_raw = fetch_pitchers(SF_GIANTS_TEAM_ID)
    print(f"  Found {len(pitchers_raw)} pitchers")

    print("Fetching player details...")
    players = []
    for p in pitchers_raw:
        player = fetch_player(p["id"])
        player["player_id"] = p["id"]
        players.append(player)
        print(f"    {player['full_name']}")

    print("Fetching game logs...")
    all_game_logs = []
    for player in players:
        logs = fetch_game_logs(player["player_id"])
        all_game_logs.extend(logs)
        print(f"    {player['full_name']}: {len(logs)} games")

    print("Connecting to Snowflake...")
    with snowflake_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL_PLAYERS)
            cur.execute(DDL_GAME_LOGS)

            print("Loading raw.players...")
            load_players(cur, players, loaded_at)

            print("Loading raw.pitcher_game_logs...")
            load_game_logs(cur, all_game_logs, loaded_at)

        conn.commit()

    print("Done.")


if __name__ == "__main__":
    main()
