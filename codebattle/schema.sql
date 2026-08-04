-- ==========================================================================
-- CODEBATTLE — PRODUCTION POSTGRESQL DATABASE SCHEMA
-- Based on Technical Guide: codebattle_Technical.md
-- ==========================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id      TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    avatar_url    TEXT,
    tier          TEXT DEFAULT 'free' CHECK (tier IN ('free', 'paid')),
    xp            INTEGER DEFAULT 0,
    rank          TEXT DEFAULT 'bronze',
    streak        INTEGER DEFAULT 0,
    last_solve_at TIMESTAMP,
    stripe_customer_id TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Connections (Mutual QR/Code based connections)
CREATE TABLE IF NOT EXISTS connections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_a_id   UUID REFERENCES users(id) ON DELETE CASCADE,
    user_b_id   UUID REFERENCES users(id) ON DELETE CASCADE,
    connected_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_a_id, user_b_id),
    CHECK (user_a_id < user_b_id)
);

-- Problems Table
CREATE TABLE IF NOT EXISTS problems (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    forked_from  UUID REFERENCES problems(id) ON DELETE SET NULL,
    version      INTEGER DEFAULT 1,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL,
    difficulty   TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    visibility   TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'connections')),
    unique_code  TEXT UNIQUE,
    language_tags TEXT[],
    solve_count  INTEGER DEFAULT 0,
    avg_solve_ms INTEGER,
    is_flagged   BOOLEAN DEFAULT false,
    is_approved  BOOLEAN DEFAULT false,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Test Cases Table
CREATE TABLE IF NOT EXISTS test_cases (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id  UUID REFERENCES problems(id) ON DELETE CASCADE,
    input       TEXT NOT NULL,
    expected    TEXT NOT NULL,
    is_hidden   BOOLEAN DEFAULT false,
    order_index INTEGER
);

-- Problists Table
CREATE TABLE IF NOT EXISTS problists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    visibility  TEXT DEFAULT 'private' CHECK (visibility IN ('public', 'private', 'connections')),
    unique_code TEXT UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Problist Problems Join Table
CREATE TABLE IF NOT EXISTS problist_problems (
    problist_id UUID REFERENCES problists(id) ON DELETE CASCADE,
    problem_id  UUID REFERENCES problems(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    PRIMARY KEY (problist_id, problem_id)
);

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    unique_code  TEXT UNIQUE NOT NULL,
    status       TEXT DEFAULT 'lobby' CHECK (status IN ('lobby', 'countdown', 'active', 'ended')),
    tier         TEXT DEFAULT 'free' CHECK (tier IN ('free', 'paid')),
    max_players  INTEGER DEFAULT 100,
    timer_type   TEXT DEFAULT 'countdown' CHECK (timer_type IN ('countdown', 'countup')),
    time_limit_s INTEGER DEFAULT 1800,
    problem_order TEXT DEFAULT 'sequential' CHECK (problem_order IN ('sequential', 'freeforall')),
    is_public    BOOLEAN DEFAULT false,
    scheduled_at TIMESTAMP,
    started_at   TIMESTAMP,
    ended_at     TIMESTAMP,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Room Problems Join Table
CREATE TABLE IF NOT EXISTS room_problems (
    room_id     UUID REFERENCES rooms(id) ON DELETE CASCADE,
    problem_id  UUID REFERENCES problems(id),
    order_index INTEGER NOT NULL,
    PRIMARY KEY (room_id, problem_id)
);

-- Submissions Table
CREATE TABLE IF NOT EXISTS submissions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES users(id) ON DELETE SET NULL,
    problem_id        UUID REFERENCES problems(id) ON DELETE CASCADE,
    room_id           UUID REFERENCES rooms(id) ON DELETE SET NULL,
    language          TEXT NOT NULL,
    source_code       TEXT NOT NULL,
    status            TEXT NOT NULL,
    execution_time_ms INTEGER,
    memory_used_kb    INTEGER,
    passed_cases      INTEGER DEFAULT 0,
    total_cases       INTEGER DEFAULT 0,
    submitted_at      TIMESTAMP DEFAULT NOW()
);
