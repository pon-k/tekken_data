
-- Drop existing tables if they exist

DROP TABLE IF EXISTS match_participations CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS characters CASCADE;
DROP TABLE IF EXISTS regions CASCADE;

-- Regions

CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Characters

CREATE TABLE characters (
    chara_id INT PRIMARY KEY,
    name TEXT
);

-- Players

CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    polaris_id TEXT,
    name TEXT,
    lang TEXT,
    region_id INT REFERENCES regions(region_id),
    area_id INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_players_user_id ON players(user_id);

-- Matches

CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    battle_id TEXT UNIQUE NOT NULL,
    battle_timestamp BIGINT NOT NULL,
    battle_datetime TIMESTAMP GENERATED ALWAYS AS (TO_TIMESTAMP(battle_timestamp)) STORED,
    battle_type INT,
    game_version INT,
    stage_id INT,
    winner_slot SMALLINT,  -- 1 = Player 1 won, 2 = Player 2 won
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_matches_battle_id ON matches(battle_id);
CREATE INDEX idx_matches_timestamp ON matches(battle_timestamp);

-- Match Participations

CREATE TABLE match_participations (
    participation_id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(match_id) ON DELETE CASCADE,
    player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
    slot SMALLINT NOT NULL CHECK (slot IN (1,2)),
    chara_id INT REFERENCES characters(chara_id),
    power INT,
    rank INT,
    rating_before INT,
    rating_change INT,
    rounds_won INT
);

INSERT INTO regions (name) VALUES
('Asia'),
('Middle East'),
('Oceania'),
('America'),
('Europe'),
('Africa')
ON CONFLICT DO NOTHING;
