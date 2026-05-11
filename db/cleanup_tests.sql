-- ============================================================
-- Cleanup script: remove all tests, subjects and related data
-- Leaves only users in the database.
-- Run this script with a privileged connection (service role or admin)
-- ============================================================

BEGIN;

-- Remove answers from old sessions
DELETE FROM session_answers;

-- Remove test session history
DELETE FROM test_sessions;

-- Remove answer options
DELETE FROM options;

-- Remove questions
DELETE FROM questions;

-- Remove tests
DELETE FROM tests;

-- Remove subjects
DELETE FROM subjects;

-- Reset sequences for cleaned tables
ALTER SEQUENCE IF EXISTS session_answers_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS test_sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS options_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS questions_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS tests_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS subjects_id_seq RESTART WITH 1;

COMMIT;
