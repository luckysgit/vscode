-- CodeBattle MVP Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    input TEXT NOT NULL,
    expected TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT false,
    order_index INTEGER DEFAULT 0
);

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unique_code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'lobby' CHECK (status IN ('lobby', 'active', 'ended')),
    problem_id UUID REFERENCES problems(id),
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id TEXT,
    user_id TEXT,
    code TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'accepted', 'wrong_answer', 'runtime_error')),
    score INTEGER DEFAULT 0,
    time_taken_ms INTEGER,
    submitted_at TIMESTAMP DEFAULT NOW()
);
