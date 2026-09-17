BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS rooms (
 id TEXT PRIMARY KEY,
 code TEXT NOT NULL UNIQUE,
 host_id TEXT NOT NULL REFERENCES accounts(id),
 title TEXT NOT NULL,
 problem_version_id TEXT NOT NULL REFERENCES problem_versions(id),
 visibility TEXT NOT NULL CHECK(visibility IN ('Public','Unlisted')),
 status TEXT NOT NULL DEFAULT 'LOBBY' CHECK(status IN ('LOBBY','CLOSED')),
 capacity INTEGER NOT NULL CHECK(capacity BETWEEN 2 AND 100),
 request_id TEXT NOT NULL,
 payload_hash TEXT NOT NULL,
 created_at REAL NOT NULL,
 closed_at REAL,
 UNIQUE(host_id,request_id)
);
CREATE INDEX IF NOT EXISTS rooms_discovery ON rooms(status,visibility,created_at DESC);
CREATE TABLE IF NOT EXISTS room_members (
 room_id TEXT NOT NULL REFERENCES rooms(id),
 user_id TEXT NOT NULL REFERENCES accounts(id),
 joined_at REAL NOT NULL,
 PRIMARY KEY(room_id,user_id)
);
CREATE INDEX IF NOT EXISTS room_members_user ON room_members(user_id,room_id);
INSERT OR IGNORE INTO problem_bank_migrations VALUES (2,CURRENT_TIMESTAMP);
COMMIT;
