-- ============================================================
--  Telegram Quiz Bot — Supabase Schema
-- ============================================================

-- Users (students & teachers)
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Subjects / disciplines
CREATE TABLE IF NOT EXISTS subjects (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tests
CREATE TABLE IF NOT EXISTS tests (
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    subject_id  BIGINT REFERENCES subjects(id) ON DELETE SET NULL,
    teacher_id  BIGINT REFERENCES users(id) ON DELETE CASCADE,
    is_public   BOOLEAN DEFAULT TRUE,
    access_code TEXT UNIQUE,                  -- only for private tests
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Questions
CREATE TABLE IF NOT EXISTS questions (
    id             BIGSERIAL PRIMARY KEY,
    test_id        BIGINT REFERENCES tests(id) ON DELETE CASCADE,
    text           TEXT NOT NULL,
    question_order INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Answer options
CREATE TABLE IF NOT EXISTS options (
    id          BIGSERIAL PRIMARY KEY,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    is_correct  BOOLEAN DEFAULT FALSE
);

-- Test sessions (one per student per test attempt)
CREATE TABLE IF NOT EXISTS test_sessions (
    id              BIGSERIAL PRIMARY KEY,
    test_id         BIGINT REFERENCES tests(id) ON DELETE CASCADE,
    student_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
    score           INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- Student answers
CREATE TABLE IF NOT EXISTS session_answers (
    id          BIGSERIAL PRIMARY KEY,
    session_id  BIGINT REFERENCES test_sessions(id) ON DELETE CASCADE,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    option_id   BIGINT REFERENCES options(id) ON DELETE CASCADE,
    is_correct  BOOLEAN DEFAULT FALSE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tests_subject ON tests(subject_id) WHERE is_public = TRUE;
CREATE INDEX IF NOT EXISTS idx_tests_teacher ON tests(teacher_id);
CREATE INDEX IF NOT EXISTS idx_questions_test ON questions(test_id);
CREATE INDEX IF NOT EXISTS idx_options_question ON options(question_id);
CREATE INDEX IF NOT EXISTS idx_sessions_test ON test_sessions(test_id);
CREATE INDEX IF NOT EXISTS idx_sessions_student ON test_sessions(student_id);
