import json
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

# DB CONNECTION

conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
)
conn.autocommit = False   # we will manually commit
cur = conn.cursor()

# INSERT/UPSERT HELPERS

def upsert_player(prefix, match):
    """Insert or update a player and return player_id."""

    query = """
        INSERT INTO players (user_id, polaris_id, name, lang, region_id, area_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            polaris_id = EXCLUDED.polaris_id,
            name = EXCLUDED.name,
            lang = EXCLUDED.lang,
            region_id = EXCLUDED.region_id,
            area_id = EXCLUDED.area_id
        RETURNING player_id;
    """

    values = (
        match[f"{prefix}user_id"],
        match[f"{prefix}polaris_id"],
        match[f"{prefix}name"],
        match[f"{prefix}lang"],
        match.get(f"{prefix}region_id"),
        match.get(f"{prefix}area_id"),
    )

    cur.execute(query, values)
    return cur.fetchone()[0]


def insert_match(match):
    """Insert a match and return match_id."""

    query = """
        INSERT INTO matches
            (battle_id, battle_timestamp, battle_type, game_version, stage_id, winner_slot)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (battle_id) DO NOTHING
        RETURNING match_id;
    """

    values = (
        match["battle_id"],
        match["battle_at"],
        match["battle_type"],
        match["game_version"],
        match["stage_id"],
        match["winner"],
    )

    cur.execute(query, values)
    result = cur.fetchone()

    # If conflict occurred and match already exists:
    if result is None:
        cur.execute("SELECT match_id FROM matches WHERE battle_id = %s", (match["battle_id"],))
        result = cur.fetchone()

    return result[0]


def insert_participation(match_id, slot, prefix, match, player_id):
    """Insert a player's participation row."""

    query = """
        INSERT INTO match_participations
            (match_id, player_id, slot, chara_id, power, rank, rating_before, rating_change, rounds_won)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """

    values = (
        match_id,
        player_id,
        slot,
        match[f"{prefix}chara_id"],
        match[f"{prefix}power"],
        match[f"{prefix}rank"],
        match[f"{prefix}rating_before"],
        match[f"{prefix}rating_change"],
        match[f"{prefix}rounds"],
    )

    cur.execute(query, values)


# MAIN LOADER

def load_match(match):
    """Load a single match into SQL."""

    # 1. Insert match
    match_id = insert_match(match)

    # 2. Upsert both players
    p1_id = upsert_player("p1_", match)
    p2_id = upsert_player("p2_", match)

    # 3. Insert participation rows
    insert_participation(match_id, 1, "p1_", match, p1_id)
    insert_participation(match_id, 2, "p2_", match, p2_id)


def load_json_file(json_path):
    """Load a JSON file containing one or many match objects."""

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        # Single match object
        load_match(data)
    else:
        # A list of matches
        for match in data:
            load_match(match)


# RUN LOADER

if __name__ == "__main__":
    try:
        load_json_file("t8data_dump")
        conn.commit()
        print("Import completed successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
        raise
    finally:
        cur.close()
        conn.close()
