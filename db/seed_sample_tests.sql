-- Sample Tests for the Quiz Bot
-- This script adds sample tests for different subjects

-- Note: You need to have created at least one teacher user first
-- The teacher_id below should be replaced with an actual teacher's ID

-- Insert sample subjects if they don't exist
INSERT INTO subjects (name) VALUES
    ('Географія'),
    ('Астрономія'),
    ('Англійська мова'),
    ('Німецька мова')
ON CONFLICT (name) DO NOTHING;

-- Get the IDs for these subjects (you'll need to check these after subjects are created)
-- For now, assuming they get IDs 1-4 in order

-- ════════════════════════════════════════════════════════════════════════════
-- GEOGRAPHY TEST
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness)
VALUES (
    'Столиці світу',
    (SELECT id FROM subjects WHERE name = 'Географія'),
    1,  -- Replace with actual teacher_id
    true,
    'Тест на знання столиць різних країн світу',
    true
) RETURNING id AS test_id;

-- Note: You'll need to get the test_id from above and use it for questions

-- For demonstration, here's the structure (you may need to run this manually or via your app):
-- INSERT INTO questions (test_id, text, question_order) VALUES
-- (TEST_ID, 'Яка столиця Франції?', 0);
-- INSERT INTO options (question_id, text, is_correct) VALUES
-- (Q_ID, 'Париж', true),
-- (Q_ID, 'Ліон', false),
-- (Q_ID, 'Марсель', false),
-- (Q_ID, 'Тулуза', false);

-- ════════════════════════════════════════════════════════════════════════════
-- ASTRONOMY TEST
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness)
VALUES (
    'Планети Сонячної системи',
    (SELECT id FROM subjects WHERE name = 'Астрономія'),
    1,  -- Replace with actual teacher_id
    true,
    'Базовий тест про планети нашої системи',
    true
);

-- ════════════════════════════════════════════════════════════════════════════
-- ENGLISH TEST
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness)
VALUES (
    'English Grammar Basics',
    (SELECT id FROM subjects WHERE name = 'Англійська мова'),
    1,  -- Replace with actual teacher_id
    true,
    'Basic English grammar test for beginners',
    true
);

-- ════════════════════════════════════════════════════════════════════════════
-- GERMAN TEST
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness)
VALUES (
    'Grundlagen der deutschen Sprache',
    (SELECT id FROM subjects WHERE name = 'Німецька мова'),
    1,  -- Replace with actual teacher_id
    true,
    'Grundlegender Deutschtest für Anfänger',
    true
);
