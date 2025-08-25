-- Database initialization script for Vocabulary Learning App
-- This script creates all necessary tables for the application

-- Users table to store user information from Google OAuth
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    given_name VARCHAR(255) NOT NULL,
    family_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Word groups table (from JSON files)
CREATE TABLE word_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Words table (from JSON files)
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES word_groups(id) ON DELETE CASCADE,
    word TEXT NOT NULL,
    part_of_speech VARCHAR(50),
    meaning_en TEXT NOT NULL,
    meaning_th TEXT NOT NULL,
    examples TEXT[],
    synonyms TEXT[],
    antonyms TEXT[],
    word_forms TEXT[],
    difficulty VARCHAR(20),
    frequency VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, word)
);

-- Indices for better query performance
CREATE INDEX idx_words_group_id ON words(group_id);
CREATE INDEX idx_words_difficulty ON words(difficulty);
CREATE INDEX idx_words_frequency ON words(frequency);

-- User word levels table (for tracking user progress)
CREATE TABLE user_word_levels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 0 CHECK (level >= 0),
    last_practiced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, word_id)
);

-- Indices for better query performance
CREATE INDEX idx_user_word_levels_user_id ON user_word_levels(user_id);
CREATE INDEX idx_user_word_levels_word_id ON user_word_levels(word_id);
CREATE INDEX idx_user_word_levels_level ON user_word_levels(level);

-- Practice sessions table
CREATE TABLE practice_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    total_score INTEGER DEFAULT 0,
    words_attempted INTEGER DEFAULT 0,
    words_correct INTEGER DEFAULT 0
);

-- Indices for better query performance
CREATE INDEX idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX idx_practice_sessions_start_time ON practice_sessions(start_time);

-- User progress table (for tracking individual word attempts)
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES practice_sessions(id) ON DELETE CASCADE,
    level_at_time INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken INTEGER, -- in seconds
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for better query performance
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_word_id ON user_progress(word_id);
CREATE INDEX idx_user_progress_session_id ON user_progress(session_id);
CREATE INDEX idx_user_progress_attempted_at ON user_progress(attempted_at);

-- User statistics aggregation table (for faster dashboard queries)
CREATE TABLE user_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    words_correct INTEGER DEFAULT 0,
    total_words_practiced INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, week_start)
);

-- Indices for better query performance
CREATE INDEX idx_user_statistics_user_id ON user_statistics(user_id);
CREATE INDEX idx_user_statistics_week_start ON user_statistics(week_start);

-- Synonyms table for the synonym game
CREATE TABLE synonyms (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    meaning VARCHAR(255) NOT NULL,
    words TEXT[] NOT NULL
);

-- Synonym games table to track game sessions
CREATE TABLE synonym_games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    played_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Synonym scores table to track scores for each round of a game
CREATE TABLE synonym_scores (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES synonym_games(id) ON DELETE CASCADE,
    subgame_order INTEGER NOT NULL,
    meaning VARCHAR(255) NOT NULL,
    score DOUBLE PRECISION NOT NULL
);

-- Create a view for current user word levels (combines latest progress with current levels)
CREATE OR REPLACE VIEW current_user_word_levels AS
SELECT
    uwl.user_id,
    uwl.word_id,
    uwl.level,
    uwl.last_practiced,
    w.group_id,
    w.difficulty,
    w.frequency
FROM user_word_levels uwl
JOIN words w ON uwl.word_id = w.id;

-- Create a view for user group performance
CREATE OR REPLACE VIEW user_group_performance AS
SELECT
    up.user_id,
    w.group_id,
    wg.name as group_name,
    COUNT(up.id) as total_words_practiced,
    SUM(CASE WHEN up.is_correct THEN 1 ELSE 0 END) as correct_answers,
    ROUND(
        AVG(CASE WHEN up.is_correct THEN 1.0 ELSE 0.0 END) * 100,
        2
    ) as accuracy_rate,
    MAX(up.attempted_at) as last_practiced
FROM user_progress up
JOIN words w ON up.word_id = w.id
JOIN word_groups wg ON w.group_id = wg.id
GROUP BY up.user_id, w.group_id, wg.name;

-- Function to update user word level based on correctness
CREATE OR REPLACE FUNCTION update_user_word_level(
    p_user_id INTEGER,
    p_word_id INTEGER,
    p_is_correct BOOLEAN
) RETURNS INTEGER AS $$
DECLARE
    current_level INTEGER;
    new_level INTEGER;
BEGIN
    -- Get current level
    SELECT level INTO current_level
    FROM user_word_levels
    WHERE user_id = p_user_id AND word_id = p_word_id;
    
    -- If no record exists, create one with level 0
    IF NOT FOUND THEN
        current_level := 0;
        INSERT INTO user_word_levels (user_id, word_id, level)
        VALUES (p_user_id, p_word_id, current_level);
    END IF;
    
    -- Calculate new level
    IF p_is_correct THEN
        new_level := current_level + 1;
    ELSE
        new_level := GREATEST(current_level - 1, 0); -- Minimum level is 0
    END IF;
    
    -- Update the level
    UPDATE user_word_levels
    SET level = new_level, last_practiced = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id AND word_id = p_word_id;
    
    RETURN new_level;
END;
$$ LANGUAGE plpgsql;

-- Function to get user statistics for the past week
CREATE OR REPLACE FUNCTION get_user_weekly_stats(p_user_id INTEGER)
RETURNS TABLE(
    correct_words INTEGER,
    total_words INTEGER,
    accuracy_rate NUMERIC,
    total_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        SUM(CASE WHEN up.is_correct THEN 1 ELSE 0 END)::INTEGER as correct_words,
        COUNT(*)::INTEGER as total_words,
        ROUND(AVG(CASE WHEN up.is_correct THEN 1.0 ELSE 0.0 END) * 100, 2)::NUMERIC as accuracy_rate,
        SUM(up.level_at_time + 1)::INTEGER as total_score
    FROM user_progress up
    WHERE up.user_id = p_user_id
    AND up.attempted_at >= CURRENT_DATE - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;