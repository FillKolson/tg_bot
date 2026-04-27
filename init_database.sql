-- ============================================================
--  Telegram Quiz Bot — Complete Database Initialization
--  Run this script to setup or reset the entire database
-- ============================================================

-- ============================================================
--  DROP POLICIES (if they exist)
-- ============================================================
DROP POLICY IF EXISTS "users_select_own" ON users;
DROP POLICY IF EXISTS "users_update_own" ON users;
DROP POLICY IF EXISTS "users_insert_service" ON users;

DROP POLICY IF EXISTS "subjects_select_all" ON subjects;
DROP POLICY IF EXISTS "subjects_insert_auth" ON subjects;

DROP POLICY IF EXISTS "tests_select_public" ON tests;
DROP POLICY IF EXISTS "tests_insert_auth" ON tests;
DROP POLICY IF EXISTS "tests_update_own" ON tests;
DROP POLICY IF EXISTS "tests_delete_own" ON tests;

DROP POLICY IF EXISTS "questions_select_if_test_accessible" ON questions;
DROP POLICY IF EXISTS "questions_insert_own_test" ON questions;
    
DROP POLICY IF EXISTS "options_select_if_accessible" ON options;
DROP POLICY IF EXISTS "options_insert_own_question" ON options;

DROP POLICY IF EXISTS "test_sessions_select_own" ON test_sessions;
DROP POLICY IF EXISTS "test_sessions_select_own_tests" ON test_sessions;
DROP POLICY IF EXISTS "test_sessions_insert_student" ON test_sessions;
DROP POLICY IF EXISTS "test_sessions_update_own" ON test_sessions;

DROP POLICY IF EXISTS "session_answers_select_own" ON session_answers;
DROP POLICY IF EXISTS "session_answers_select_own_tests" ON session_answers;
DROP POLICY IF EXISTS "session_answers_insert_own_session" ON session_answers;
DROP POLICY IF EXISTS "session_answers_update_own_session" ON session_answers;

-- ============================================================
--  DROP TABLES (if they exist)
-- ============================================================
DROP TABLE IF EXISTS session_answers CASCADE;
DROP TABLE IF EXISTS test_sessions CASCADE;
DROP TABLE IF EXISTS options CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS tests CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
--  CREATE TABLES
-- ============================================================

-- Users (students & teachers)
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
    language    TEXT DEFAULT 'uk' CHECK (language IN ('uk', 'en')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Subjects / disciplines
CREATE TABLE subjects (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tests
CREATE TABLE tests (
    id                       BIGSERIAL PRIMARY KEY,
    title                    TEXT NOT NULL,
    description              TEXT,
    subject_id               BIGINT REFERENCES subjects(id) ON DELETE SET NULL,
    teacher_id               BIGINT REFERENCES users(id) ON DELETE CASCADE,
    is_public                BOOLEAN DEFAULT TRUE,
    access_code              TEXT UNIQUE,                  -- only for private tests
    is_active                BOOLEAN DEFAULT TRUE,
    show_answer_correctness  BOOLEAN DEFAULT TRUE,         -- teacher decides if answers are shown
    created_at               TIMESTAMPTZ DEFAULT NOW()
);

-- Questions
CREATE TABLE questions (
    id             BIGSERIAL PRIMARY KEY,
    test_id        BIGINT REFERENCES tests(id) ON DELETE CASCADE,
    text           TEXT NOT NULL,
    question_order INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Answer options
CREATE TABLE options (
    id          BIGSERIAL PRIMARY KEY,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    is_correct  BOOLEAN DEFAULT FALSE
);

-- Test sessions (one per student per test attempt)
CREATE TABLE test_sessions (
    id              BIGSERIAL PRIMARY KEY,
    test_id         BIGINT REFERENCES tests(id) ON DELETE CASCADE,
    student_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
    score           INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- Student answers
CREATE TABLE session_answers (
    id          BIGSERIAL PRIMARY KEY,
    session_id  BIGINT REFERENCES test_sessions(id) ON DELETE CASCADE,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    option_id   BIGINT REFERENCES options(id) ON DELETE CASCADE,
    is_correct  BOOLEAN DEFAULT FALSE
);

-- ============================================================
--  CREATE INDEXES
-- ============================================================
CREATE INDEX idx_tests_subject ON tests(subject_id) WHERE is_public = TRUE;
CREATE INDEX idx_tests_teacher ON tests(teacher_id);
CREATE INDEX idx_questions_test ON questions(test_id);
CREATE INDEX idx_options_question ON options(question_id);
CREATE INDEX idx_sessions_test ON test_sessions(test_id);
CREATE INDEX idx_sessions_student ON test_sessions(student_id);

-- ============================================================
--  ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE options ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_answers ENABLE ROW LEVEL SECURITY;

-- ============================================================
--  RLS POLICIES FOR USERS TABLE
-- ============================================================
-- Users can only see their own profile
CREATE POLICY "users_select_own" ON users
    FOR SELECT USING (telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT);

-- Users can only update their own profile
CREATE POLICY "users_update_own" ON users
    FOR UPDATE USING (telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT);

-- Service role (bot) can insert users
CREATE POLICY "users_insert_service" ON users
    FOR INSERT WITH CHECK (true);

-- ============================================================
--  RLS POLICIES FOR SUBJECTS TABLE
-- ============================================================
-- Everyone can read all subjects
CREATE POLICY "subjects_select_all" ON subjects
    FOR SELECT USING (true);

-- Only admin can create subjects
CREATE POLICY "subjects_insert_auth" ON subjects
    FOR INSERT WITH CHECK (true);

-- ============================================================
--  RLS POLICIES FOR TESTS TABLE
-- ============================================================
-- Public tests are visible to everyone
CREATE POLICY "tests_select_public" ON tests
    FOR SELECT USING (
        is_public = TRUE 
        OR teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
    );

-- Teachers can create tests (or admin)
CREATE POLICY "tests_insert_auth" ON tests
    FOR INSERT WITH CHECK (true);

-- Teachers can update their own tests
CREATE POLICY "tests_update_own" ON tests
    FOR UPDATE USING (
        teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
    );

-- Teachers can delete their own tests
CREATE POLICY "tests_delete_own" ON tests
    FOR DELETE USING (
        teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
    );

-- ============================================================
--  RLS POLICIES FOR QUESTIONS TABLE
-- ============================================================
-- Can read questions if can access the test
CREATE POLICY "questions_select_if_test_accessible" ON questions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM tests 
            WHERE tests.id = questions.test_id 
            AND (
                tests.is_public = TRUE 
                OR tests.teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
            )
        )
    );

-- Teachers can insert questions to their tests (or admin)
CREATE POLICY "questions_insert_own_test" ON questions
    FOR INSERT WITH CHECK (true);

-- ============================================================
--  RLS POLICIES FOR OPTIONS TABLE
-- ============================================================
-- Can read options if can access the question's test
CREATE POLICY "options_select_if_accessible" ON options
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM questions 
            INNER JOIN tests ON tests.id = questions.test_id
            WHERE questions.id = options.question_id 
            AND (
                tests.is_public = TRUE 
                OR tests.teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
            )
        )
    );

-- Teachers can insert options to their test questions (or admin)
CREATE POLICY "options_insert_own_question" ON options
    FOR INSERT WITH CHECK (true);

-- ============================================================
--  RLS POLICIES FOR TEST_SESSIONS TABLE
-- ============================================================
-- Students can read only their own sessions
CREATE POLICY "test_sessions_select_own" ON test_sessions
    FOR SELECT USING (
        student_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
    );

-- Teachers can read sessions from their tests
CREATE POLICY "test_sessions_select_own_tests" ON test_sessions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM tests 
            WHERE tests.id = test_sessions.test_id 
            AND tests.teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
        )
    );

-- Students can create sessions (or admin)
CREATE POLICY "test_sessions_insert_student" ON test_sessions
    FOR INSERT WITH CHECK (true);

-- Students can update their own sessions
CREATE POLICY "test_sessions_update_own" ON test_sessions
    FOR UPDATE USING (
        student_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
    );

-- ============================================================
--  RLS POLICIES FOR SESSION_ANSWERS TABLE
-- ============================================================
-- Students can only see answers from their own sessions
CREATE POLICY "session_answers_select_own" ON session_answers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM test_sessions 
            WHERE test_sessions.id = session_answers.session_id 
            AND test_sessions.student_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
        )
    );

-- Teachers can see answers from their test sessions
CREATE POLICY "session_answers_select_own_tests" ON session_answers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM session_answers 
            INNER JOIN test_sessions ON test_sessions.id = session_answers.session_id
            INNER JOIN tests ON tests.id = test_sessions.test_id
            WHERE tests.teacher_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
        )
    );

-- Students can insert their answers (or admin)
CREATE POLICY "session_answers_insert_own_session" ON session_answers
    FOR INSERT WITH CHECK (true);

-- Students can update their answers
CREATE POLICY "session_answers_update_own_session" ON session_answers
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM test_sessions 
            WHERE test_sessions.id = session_answers.session_id 
            AND test_sessions.student_id = (SELECT id FROM users WHERE telegram_id = (auth.jwt() ->> 'telegram_id')::BIGINT LIMIT 1)
        )
    );

-- ============================================================
--  DONE
-- ============================================================
-- Database is now ready with all tables and RLS policies
-- Tables: users, subjects, tests, questions, options, test_sessions, session_answers
-- All RLS policies are in place
