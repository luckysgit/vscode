BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS problems (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES accounts(id),
    current_version_id TEXT REFERENCES problem_versions(id) DEFERRABLE INITIALLY DEFERRED,
    draft_version_id TEXT REFERENCES problem_versions(id) DEFERRABLE INITIALLY DEFERRED,
    visibility TEXT NOT NULL DEFAULT 'Private' CHECK(visibility IN ('Private','Public')),
    draft_visibility TEXT CHECK(draft_visibility IN ('Private','Public')),
    status TEXT NOT NULL DEFAULT 'DRAFT' CHECK(status IN ('DRAFT','PUBLISHED','ARCHIVED')),
    revision INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    archived_at REAL
);
CREATE INDEX IF NOT EXISTS problems_owner_updated ON problems(owner_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS problems_public ON problems(visibility, status, updated_at DESC);
CREATE TABLE IF NOT EXISTS problem_versions (
    id TEXT PRIMARY KEY,
    problem_id TEXT NOT NULL REFERENCES problems(id),
    version_number INTEGER NOT NULL CHECK(version_number > 0),
    title TEXT NOT NULL,
    short_description TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy','Medium','Hard')),
    input_format TEXT NOT NULL,
    output_format TEXT NOT NULL,
    constraints_text TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_by TEXT NOT NULL REFERENCES accounts(id),
    created_at REAL NOT NULL,
    published_at REAL,
    UNIQUE(problem_id, version_number)
);
CREATE TABLE IF NOT EXISTS problem_tags (
    problem_version_id TEXT NOT NULL REFERENCES problem_versions(id),
    tag TEXT NOT NULL,
    PRIMARY KEY(problem_version_id, tag)
);
CREATE INDEX IF NOT EXISTS problem_tags_tag ON problem_tags(tag);
CREATE TABLE IF NOT EXISTS test_cases (
    id TEXT PRIMARY KEY,
    problem_version_id TEXT NOT NULL REFERENCES problem_versions(id),
    input TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_hidden INTEGER NOT NULL CHECK(is_hidden IN (0,1)),
    sort_order INTEGER NOT NULL CHECK(sort_order >= 0),
    created_at REAL NOT NULL,
    UNIQUE(problem_version_id, sort_order)
);
CREATE TABLE IF NOT EXISTS problem_create_requests (
    owner_id TEXT NOT NULL REFERENCES accounts(id),
    request_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    problem_id TEXT NOT NULL REFERENCES problems(id),
    PRIMARY KEY(owner_id, request_id)
);
CREATE TRIGGER IF NOT EXISTS immutable_published_version_update BEFORE UPDATE ON problem_versions
WHEN OLD.published_at IS NOT NULL BEGIN SELECT RAISE(ABORT, 'Published versions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_version_delete BEFORE DELETE ON problem_versions
WHEN OLD.published_at IS NOT NULL BEGIN SELECT RAISE(ABORT, 'Published versions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_case_insert BEFORE INSERT ON test_cases
WHEN (SELECT published_at FROM problem_versions WHERE id=NEW.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tests are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_case_update BEFORE UPDATE ON test_cases
WHEN (SELECT published_at FROM problem_versions WHERE id=OLD.problem_version_id) IS NOT NULL
OR (SELECT published_at FROM problem_versions WHERE id=NEW.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tests are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_case_delete BEFORE DELETE ON test_cases
WHEN (SELECT published_at FROM problem_versions WHERE id=OLD.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tests are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_tag_insert BEFORE INSERT ON problem_tags
WHEN (SELECT published_at FROM problem_versions WHERE id=NEW.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tags are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_tag_update BEFORE UPDATE ON problem_tags
WHEN (SELECT published_at FROM problem_versions WHERE id=OLD.problem_version_id) IS NOT NULL
OR (SELECT published_at FROM problem_versions WHERE id=NEW.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tags are immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_published_tag_delete BEFORE DELETE ON problem_tags
WHEN (SELECT published_at FROM problem_versions WHERE id=OLD.problem_version_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'Published tags are immutable'); END;
CREATE TABLE IF NOT EXISTS problem_bank_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
INSERT OR IGNORE INTO problem_bank_migrations VALUES (1, CURRENT_TIMESTAMP);
COMMIT;
