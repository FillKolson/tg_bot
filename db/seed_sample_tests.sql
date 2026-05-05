-- Sample Tests for the Quiz Bot
-- This script adds sample tests for different subjects with various attempt limits
--
-- Attempt limits:
-- - Geography: Unlimited attempts (NULL)
-- - History: 3 attempts
-- - Astronomy: 1 attempt
-- - English: 5 attempts
-- - German: 2 attempts

-- Note: You need to have created at least one teacher user first
-- The teacher_id below should be replaced with an actual teacher's ID

-- Insert sample subjects if they don't exist
INSERT INTO subjects (name) VALUES
    ('Географія'),
    ('Історія'),
    ('Астрономія'),
    ('Англійська мова'),
    ('Німецька мова')
ON CONFLICT (name) DO NOTHING;

-- ════════════════════════════════════════════════════════════════════════════
-- GEOGRAPHY TEST - UNLIMITED ATTEMPTS
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Столиці світу',
    (SELECT id FROM subjects WHERE name = 'Географія'),
    778034991,
    true,
    'Тест на знання столиць різних країн світу',
    true,
    NULL  -- Необмежено спроб
) RETURNING id AS test_id;

-- Questions for Geography test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Столиці світу'), 'Яка столиця Франції?', 0),
((SELECT id FROM tests WHERE title = 'Столиці світу'), 'Яка столиця Німеччини?', 1),
((SELECT id FROM tests WHERE title = 'Столиці світу'), 'Яка столиця Італії?', 2),
((SELECT id FROM tests WHERE title = 'Столиці світу'), 'Яка столиця Іспанії?', 3);

-- Options for Geography questions
-- Question 1: Яка столиця Франції?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка столиця Франції?'), 'Париж', true),
((SELECT id FROM questions WHERE text = 'Яка столиця Франції?'), 'Ліон', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Франції?'), 'Марсель', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Франції?'), 'Тулуза', false);

-- Question 2: Яка столиця Німеччини?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка столиця Німеччини?'), 'Берлін', true),
((SELECT id FROM questions WHERE text = 'Яка столиця Німеччини?'), 'Мюнхен', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Німеччини?'), 'Гамбург', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Німеччини?'), 'Кельн', false);

-- Question 3: Яка столиця Італії?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка столиця Італії?'), 'Рим', true),
((SELECT id FROM questions WHERE text = 'Яка столиця Італії?'), 'Мілан', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Італії?'), 'Венеція', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Італії?'), 'Флоренція', false);

-- Question 4: Яка столиця Іспанії?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка столиця Іспанії?'), 'Мадрид', true),
((SELECT id FROM questions WHERE text = 'Яка столиця Іспанії?'), 'Барселона', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Іспанії?'), 'Валенсія', false),
((SELECT id FROM questions WHERE text = 'Яка столиця Іспанії?'), 'Севілья', false);

-- ════════════════════════════════════════════════════════════════════════════
-- HISTORY TEST - 3 ATTEMPTS
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Історія України',
    (SELECT id FROM subjects WHERE name = 'Історія'),
    778034991,
    true,
    'Базові знання з історії України',
    true,
    3  -- 3 спроби
);

-- Questions for History test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Історія України'), 'Коли відбулася Хрещення Русі?', 0),
((SELECT id FROM tests WHERE title = 'Історія України'), 'Хто був гетьманом України у 1648 році?', 1),
((SELECT id FROM tests WHERE title = 'Історія України'), 'Коли Україна проголосила незалежність?', 2),
((SELECT id FROM tests WHERE title = 'Історія України'), 'Яка битва відбулася у 1240 році?', 3);

-- Options for History questions
-- Question 1: Коли відбулася Хрещення Русі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Коли відбулася Хрещення Русі?'), '988 рік', true),
((SELECT id FROM questions WHERE text = 'Коли відбулася Хрещення Русі?'), '1015 рік', false),
((SELECT id FROM questions WHERE text = 'Коли відбулася Хрещення Русі?'), '862 рік', false),
((SELECT id FROM questions WHERE text = 'Коли відбулася Хрещення Русі?'), '1113 рік', false);

-- Question 2: Хто був гетьманом України у 1648 році?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хто був гетьманом України у 1648 році?'), 'Богдан Хмельницький', true),
((SELECT id FROM questions WHERE text = 'Хто був гетьманом України у 1648 році?'), 'Іван Мазепа', false),
((SELECT id FROM questions WHERE text = 'Хто був гетьманом України у 1648 році?'), 'Петро Дорошенко', false),
((SELECT id FROM questions WHERE text = 'Хто був гетьманом України у 1648 році?'), 'Іван Виговський', false);

-- Question 3: Коли Україна проголосила незалежність?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Коли Україна проголосила незалежність?'), '24 серпня 1991 року', true),
((SELECT id FROM questions WHERE text = 'Коли Україна проголосила незалежність?'), '1 грудня 1991 року', false),
((SELECT id FROM questions WHERE text = 'Коли Україна проголосила незалежність?'), '16 липня 1990 року', false),
((SELECT id FROM questions WHERE text = 'Коли Україна проголосила незалежність?'), '28 червня 1996 року', false);

-- Question 4: Яка битва відбулася у 1240 році?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка битва відбулася у 1240 році?'), 'Битва на Калці', true),
((SELECT id FROM questions WHERE text = 'Яка битва відбулася у 1240 році?'), 'Битва під Конотопом', false),
((SELECT id FROM questions WHERE text = 'Яка битва відбулася у 1240 році?'), 'Битва під Берестечком', false),
((SELECT id FROM questions WHERE text = 'Яка битва відбулася у 1240 році?'), 'Битва під Полтавою', false);

-- ════════════════════════════════════════════════════════════════════════════
-- ASTRONOMY TEST - 1 ATTEMPT
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Планети Сонячної системи',
    (SELECT id FROM subjects WHERE name = 'Астрономія'),
    778034991,
    true,
    'Базовий тест про планети нашої системи',
    true,
    1  -- 1 спроба
);

-- Questions for Astronomy test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Скільки планет у Сонячній системі?', 0),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета найближча до Сонця?', 1),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета найбільша у Сонячній системі?', 2),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета відома як "Червона планета"?', 3);

-- Options for Astronomy questions
-- Question 1: Скільки планет у Сонячній системі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Скільки планет у Сонячній системі?'), '8', true),
((SELECT id FROM questions WHERE text = 'Скільки планет у Сонячній системі?'), '9', false),
((SELECT id FROM questions WHERE text = 'Скільки планет у Сонячній системі?'), '7', false),
((SELECT id FROM questions WHERE text = 'Скільки планет у Сонячній системі?'), '10', false);

-- Question 2: Яка планета найближча до Сонця?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка планета найближча до Сонця?'), 'Меркурій', true),
((SELECT id FROM questions WHERE text = 'Яка планета найближча до Сонця?'), 'Венера', false),
((SELECT id FROM questions WHERE text = 'Яка планета найближча до Сонця?'), 'Земля', false),
((SELECT id FROM questions WHERE text = 'Яка планета найближча до Сонця?'), 'Марс', false);

-- Question 3: Яка планета найбільша у Сонячній системі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка планета найбільша у Сонячній системі?'), 'Юпітер', true),
((SELECT id FROM questions WHERE text = 'Яка планета найбільша у Сонячній системі?'), 'Сатурн', false),
((SELECT id FROM questions WHERE text = 'Яка планета найбільша у Сонячній системі?'), 'Уран', false),
((SELECT id FROM questions WHERE text = 'Яка планета найбільша у Сонячній системі?'), 'Нептун', false);

-- Question 4: Яка планета відома як "Червона планета"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Яка планета відома як "Червона планета"?'), 'Марс', true),
((SELECT id FROM questions WHERE text = 'Яка планета відома як "Червона планета"?'), 'Венера', false),
((SELECT id FROM questions WHERE text = 'Яка планета відома як "Червона планета"?'), 'Юпітер', false),
((SELECT id FROM questions WHERE text = 'Яка планета відома як "Червона планета"?'), 'Сатурн', false);

-- ════════════════════════════════════════════════════════════════════════════
-- ENGLISH TEST - 5 ATTEMPTS
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'English Grammar Basics',
    (SELECT id FROM subjects WHERE name = 'Англійська мова'),
    778034991,
    true,
    'Basic English grammar test for beginners',
    true,
    5  -- 5 спроб
);

-- Questions for English test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'What is the correct form: "She ___ to school every day"?', 0),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'Choose the correct article: "___ apple a day keeps the doctor away"', 1),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'What is the past tense of "go"?', 2),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'Which word is a noun: run, quickly, house, beautiful?', 3);

-- Options for English questions
-- Question 1: What is the correct form: "She ___ to school every day"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'What is the correct form: "She ___ to school every day"?'), 'goes', true),
((SELECT id FROM questions WHERE text = 'What is the correct form: "She ___ to school every day"?'), 'go', false),
((SELECT id FROM questions WHERE text = 'What is the correct form: "She ___ to school every day"?'), 'going', false),
((SELECT id FROM questions WHERE text = 'What is the correct form: "She ___ to school every day"?'), 'gone', false);

-- Question 2: Choose the correct article: "___ apple a day keeps the doctor away"
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Choose the correct article: "___ apple a day keeps the doctor away"'), 'An', true),
((SELECT id FROM questions WHERE text = 'Choose the correct article: "___ apple a day keeps the doctor away"'), 'A', false),
((SELECT id FROM questions WHERE text = 'Choose the correct article: "___ apple a day keeps the doctor away"'), 'The', false),
((SELECT id FROM questions WHERE text = 'Choose the correct article: "___ apple a day keeps the doctor away"'), 'No article', false);

-- Question 3: What is the past tense of "go"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'What is the past tense of "go"?'), 'went', true),
((SELECT id FROM questions WHERE text = 'What is the past tense of "go"?'), 'goed', false),
((SELECT id FROM questions WHERE text = 'What is the past tense of "go"?'), 'gone', false),
((SELECT id FROM questions WHERE text = 'What is the past tense of "go"?'), 'going', false);

-- Question 4: Which word is a noun: run, quickly, house, beautiful?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'house', true),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'run', false),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'quickly', false),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'beautiful', false);

-- ════════════════════════════════════════════════════════════════════════════
-- GERMAN TEST - 2 ATTEMPTS
-- ════════════════════════════════════════════════════════════════════════════

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Grundlagen der deutschen Sprache',
    (SELECT id FROM subjects WHERE name = 'Німецька мова'),
    778034991,
    true,
    'Grundlegender Deutschtest für Anfänger',
    true,
    2  -- 2 спроби
);

-- Questions for German test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Grundlagen der deutschen Sprache'), 'Wie sagt man "Hallo" auf Deutsch?', 0),
((SELECT id FROM tests WHERE title = 'Grundlagen der deutschen Sprache'), 'Was bedeutet "Haus" auf Englisch?', 1),
((SELECT id FROM tests WHERE title = 'Grundlagen der deutschen Sprache'), 'Welcher Artikel gehört zu "Buch"?', 2),
((SELECT id FROM tests WHERE title = 'Grundlagen der deutschen Sprache'), 'Wie heißt "cat" auf Deutsch?', 3);

-- Options for German questions
-- Question 1: Wie sagt man "Hallo" auf Deutsch?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Wie sagt man "Hallo" auf Deutsch?'), 'Hallo', true),
((SELECT id FROM questions WHERE text = 'Wie sagt man "Hallo" auf Deutsch?'), 'Guten Tag', false),
((SELECT id FROM questions WHERE text = 'Wie sagt man "Hallo" auf Deutsch?'), 'Auf Wiedersehen', false),
((SELECT id FROM questions WHERE text = 'Wie sagt man "Hallo" auf Deutsch?'), 'Danke', false);

-- Question 2: Was bedeutet "Haus" auf Englisch?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Was bedeutet "Haus" auf Englisch?'), 'house', true),
((SELECT id FROM questions WHERE text = 'Was bedeutet "Haus" auf Englisch?'), 'home', false),
((SELECT id FROM questions WHERE text = 'Was bedeutet "Haus" auf Englisch?'), 'building', false),
((SELECT id FROM questions WHERE text = 'Was bedeutet "Haus" auf Englisch?'), 'room', false);

-- Question 3: Welcher Artikel gehört zu "Buch"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Welcher Artikel gehört zu "Buch"?'), 'das', true),
((SELECT id FROM questions WHERE text = 'Welcher Artikel gehört zu "Buch"?'), 'der', false),
((SELECT id FROM questions WHERE text = 'Welcher Artikel gehört zu "Buch"?'), 'die', false),
((SELECT id FROM questions WHERE text = 'Welcher Artikel gehört zu "Buch"?'), 'den', false);

-- Question 4: Wie heißt "cat" auf Deutsch?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Wie heißt "cat" auf Deutsch?'), 'Katze', true),
((SELECT id FROM questions WHERE text = 'Wie heißt "cat" auf Deutsch?'), 'Hund', false),
((SELECT id FROM questions WHERE text = 'Wie heißt "cat" auf Deutsch?'), 'Maus', false),
((SELECT id FROM questions WHERE text = 'Wie heißt "cat" auf Deutsch?'), 'Vogel', false);
