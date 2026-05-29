-- Sample tests for Quiz Bot. Run after creating at least one teacher.
-- Gets teacher_id dynamically from the first teacher in the database.
--
-- Also seeds demo students (telegram_id 900000001–900000008), completed test
-- sessions, and session_answers, plus 30 attempts for telegram_id 6056542025.
-- Re-running the student blocks is safe: their sessions are removed first.

-- Insert all sample subjects if they don't exist
INSERT INTO subjects (name) VALUES
    ('Географія'),
    ('Історія'),
    ('Астрономія'),
    ('Англійська мова'),
    ('Німецька мова'),
    ('Історія України'),
    ('Математика'),
    ('Література'),
    ('Біологія'),
    ('Хімія'),
    ('Фізика')
ON CONFLICT (name) DO NOTHING;

-- Geography test (unlimited attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Столиці світу',
    (SELECT id FROM subjects WHERE name = 'Географія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
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

-- History test (3 attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Історія України',
    (SELECT id FROM subjects WHERE name = 'Історія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Базові знання з історії України',
    true,
    3  -- 3 спроби
) RETURNING id AS test_id;

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

-- Astronomy test (1 attempt, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Планети Сонячної системи',
    (SELECT id FROM subjects WHERE name = 'Астрономія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Базовий тест про планети нашої системи',
    false,
    1  -- 1 спроба
) RETURNING id AS test_id;

-- Questions for Astronomy test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Скільки планет у Сонячній системі?', 0),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета найближча до Сонця?', 1),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета найбільша у Сонячній системі?', 2),
((SELECT id FROM tests WHERE title = 'Планети Сонячної системи'), 'Яка планета відома як "Червона планета"?',3);

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

-- English test (5 attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'English Grammar Basics',
    (SELECT id FROM subjects WHERE name = 'Англійська мова'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Basic English grammar test for beginners',
    true,
    5  -- 5 спроб
) RETURNING id AS test_id;

-- Questions for English test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'What is correct form: "She ___ to school every day"?', 0),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'Choose correct article: "___ apple a day keeps doctor away"', 1),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'What is past tense of "go"?', 2),
((SELECT id FROM tests WHERE title = 'English Grammar Basics'), 'Which word is a noun: run, quickly, house, beautiful?', 3);

-- Options for English questions
-- Question 1: What is correct form: "She ___ to school every day"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'What is correct form: "She ___ to school every day"?'), 'goes', true),
((SELECT id FROM questions WHERE text = 'What is correct form: "She ___ to school every day"?'), 'go', false),
((SELECT id FROM questions WHERE text = 'What is correct form: "She ___ to school every day"?'), 'going', false),
((SELECT id FROM questions WHERE text = 'What is correct form: "She ___ to school every day"?'), 'gone', false);

-- Question 2: Choose correct article: "___ apple a day keeps doctor away"
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Choose correct article: "___ apple a day keeps doctor away"'), 'An', true),
((SELECT id FROM questions WHERE text = 'Choose correct article: "___ apple a day keeps doctor away"'), 'A', false),
((SELECT id FROM questions WHERE text = 'Choose correct article: "___ apple a day keeps doctor away"'), 'The', false),
((SELECT id FROM questions WHERE text = 'Choose correct article: "___ apple a day keeps doctor away"'), 'No article', false);

-- Question 3: What is past tense of "go"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'What is past tense of "go"?'), 'went', true),
((SELECT id FROM questions WHERE text = 'What is past tense of "go"?'), 'goed', false),
((SELECT id FROM questions WHERE text = 'What is past tense of "go"?'), 'gone', false),
((SELECT id FROM questions WHERE text = 'What is past tense of "go"?'), 'going', false);

-- Question 4: Which word is a noun: run, quickly, house, beautiful?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'house', true),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'run', false),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'quickly', false),
((SELECT id FROM questions WHERE text = 'Which word is a noun: run, quickly, house, beautiful?'), 'beautiful', false);

-- German test (2 attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Grundlagen der deutschen Sprache',
    (SELECT id FROM subjects WHERE name = 'Німецька мова'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Grundlegender Deutschtest für Anfänger',
    true,
    2  -- 2 спроби
) RETURNING id AS test_id;

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

-- Ukrainian history test (3 attempts, hides correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Історія України (розширена)',
    (SELECT id FROM subjects WHERE name = 'Історія України'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Тест з історії України (правильні відповіді приховано)',
    false,
    3
) RETURNING id AS test_id;

-- Questions for Ukrainian History test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Історія України (розширена)'), 'Рік проголошення Незалежності України?', 0),
((SELECT id FROM tests WHERE title = 'Історія України (розширена)'), 'Хто був першим Президентом України?', 1),
((SELECT id FROM tests WHERE title = 'Історія України (розширена)'), 'Столиця Київської Русі?', 2),
((SELECT id FROM tests WHERE title = 'Історія України (розширена)'), 'Коли прийнято Конституцію України?', 3);

-- Options for Ukrainian History questions
-- Question 1: Рік проголошення Незалежності України?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Рік проголошення Незалежності України?'), '1991', true),
((SELECT id FROM questions WHERE text = 'Рік проголошення Незалежності України?'), '1990', false),
((SELECT id FROM questions WHERE text = 'Рік проголошення Незалежності України?'), '1992', false),
((SELECT id FROM questions WHERE text = 'Рік проголошення Незалежності України?'), '1989', false);

-- Question 2: Хто був першим Президентом України?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хто був першим Президентом України?'), 'Леонід Кравчук', true),
((SELECT id FROM questions WHERE text = 'Хто був першим Президентом України?'), 'Леонід Кучма', false),
((SELECT id FROM questions WHERE text = 'Хто був першим Президентом України?'), 'Віктор Ющенко', false),
((SELECT id FROM questions WHERE text = 'Хто був першим Президентом України?'), 'Петро Порошенко', false);

-- Question 3: Столиця Київської Русі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Столиця Київської Русі?'), 'Київ', true),
((SELECT id FROM questions WHERE text = 'Столиця Київської Русі?'), 'Львів', false),
((SELECT id FROM questions WHERE text = 'Столиця Київської Русі?'), 'Харків', false),
((SELECT id FROM questions WHERE text = 'Столиця Київської Русі?'), 'Одеса', false);

-- Question 4: Коли прийнято Конституцію України?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Коли прийнято Конституцію України?'), '28 червня 1996', true),
((SELECT id FROM questions WHERE text = 'Коли прийнято Конституцію України?'), '24 серпня 1991', false),
((SELECT id FROM questions WHERE text = 'Коли прийнято Конституцію України?'), '1 грудня 1991', false),
((SELECT id FROM questions WHERE text = 'Коли прийнято Конституцію України?'), '16 липня 1990', false);

-- Math test (unlimited attempts, hides correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Базова математика',
    (SELECT id FROM subjects WHERE name = 'Математика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Базова математика (правильні відповіді приховано)',
    false,
    NULL
) RETURNING id AS test_id;

-- Questions for Mathematics test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Базова математика'), '2 + 2 = ?', 0),
((SELECT id FROM tests WHERE title = 'Базова математика'), '10 × 5 = ?', 1),
((SELECT id FROM tests WHERE title = 'Базова математика'), '√64 = ?', 2),
((SELECT id FROM tests WHERE title = 'Базова математика'), '15 ÷ 3 = ?', 3),
((SELECT id FROM tests WHERE title = 'Базова математика'), '2³ = ?', 4);

-- Options for Mathematics questions
-- Question 1: 2 + 2 = ?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = '2 + 2 = ?'), '4', true),
((SELECT id FROM questions WHERE text = '2 + 2 = ?'), '3', false),
((SELECT id FROM questions WHERE text = '2 + 2 = ?'), '5', false),
((SELECT id FROM questions WHERE text = '2 + 2 = ?'), '2', false);

-- Question 2: 10 × 5 = ?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = '10 × 5 = ?'), '50', true),
((SELECT id FROM questions WHERE text = '10 × 5 = ?'), '15', false),
((SELECT id FROM questions WHERE text = '10 × 5 = ?'), '100', false),
((SELECT id FROM questions WHERE text = '10 × 5 = ?'), '5', false);

-- Question 3: √64 = ?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = '√64 = ?'), '8', true),
((SELECT id FROM questions WHERE text = '√64 = ?'), '6', false),
((SELECT id FROM questions WHERE text = '√64 = ?'), '7', false),
((SELECT id FROM questions WHERE text = '√64 = ?'), '9', false);

-- Question 4: 15 ÷ 3 = ?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = '15 ÷ 3 = ?'), '5', true),
((SELECT id FROM questions WHERE text = '15 ÷ 3 = ?'), '3', false),
((SELECT id FROM questions WHERE text = '15 ÷ 3 = ?'), '12', false),
((SELECT id FROM questions WHERE text = '15 ÷ 3 = ?'), '45', false);

-- Question 5: 2³ = ?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = '2³ = ?'), '8', true),
((SELECT id FROM questions WHERE text = '2³ = ?'), '6', false),
((SELECT id FROM questions WHERE text = '2³ = ?'), '9', false),
((SELECT id FROM questions WHERE text = '2³ = ?'), '12', false);

-- Literature test (3 attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Українська література',
    (SELECT id FROM subjects WHERE name = 'Література'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Українська література (показує правильні відповіді)',
    true,
    3
) RETURNING id AS test_id;

-- Questions for Literature test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Українська література'), 'Хто написав "Кобзар"?', 0),
((SELECT id FROM tests WHERE title = 'Українська література'), 'Автор "Захар Беркут"?', 1),
((SELECT id FROM tests WHERE title = 'Українська література'), 'Хто написав "Лісова пісня"?', 2);

-- Options for Literature questions
-- Question 1: Хто написав "Кобзар"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хто написав "Кобзар"?'), 'Тарас Шевченко', true),
((SELECT id FROM questions WHERE text = 'Хто написав "Кобзар"?'), 'Іван Франко', false),
((SELECT id FROM questions WHERE text = 'Хто написав "Кобзар"?'), 'Леся Українка', false),
((SELECT id FROM questions WHERE text = 'Хто написав "Кобзар"?'), 'Михайло Коцюбинський', false);

-- Question 2: Автор "Захар Беркут"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Автор "Захар Беркут"?'), 'Іван Франко', true),
((SELECT id FROM questions WHERE text = 'Автор "Захар Беркут"?'), 'Тарас Шевченко', false),
((SELECT id FROM questions WHERE text = 'Автор "Захар Беркут"?'), 'Панас Мирний', false),
((SELECT id FROM questions WHERE text = 'Автор "Захар Беркут"?'), 'Ольга Кобилянська', false);

-- Question 3: Хто написав "Лісова пісня"?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хто написав "Лісова пісня"?'), 'Леся Українка', true),
((SELECT id FROM questions WHERE text = 'Хто написав "Лісова пісня"?'), 'Марко Вовчок', false),
((SELECT id FROM questions WHERE text = 'Хто написав "Лісова пісня"?'), 'Олена Пчілка', false),
((SELECT id FROM questions WHERE text = 'Хто написав "Лісова пісня"?'), 'Неофіти', false);

-- Biology test (4 attempts, hides correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Основи біології',
    (SELECT id FROM subjects WHERE name = 'Біологія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Основи біології (правильні відповіді приховано)',
    false,
    4
) RETURNING id AS test_id;

-- Questions for Biology test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Основи біології'), 'Найбільша кістка в людському тілі?', 0),
((SELECT id FROM tests WHERE title = 'Основи біології'), 'Скільки камер у серці людини?', 1),
((SELECT id FROM tests WHERE title = 'Основи біології'), 'Найбільший мозок у людському тілі?', 2),
((SELECT id FROM tests WHERE title = 'Основи біології'), 'Хто відкрив пеніцилін?', 3);

-- Options for Biology questions
-- Question 1: Найбільша кістка в людському тілі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Найбільша кістка в людському тілі?'), 'Стегнова кістка', true),
((SELECT id FROM questions WHERE text = 'Найбільша кістка в людському тілі?'), 'Череп', false),
((SELECT id FROM questions WHERE text = 'Найбільша кістка в людському тілі?'), 'Хребет', false),
((SELECT id FROM questions WHERE text = 'Найбільша кістка в людському тілі?'), 'Ребра', false);

-- Question 2: Скільки камер у серці людини?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Скільки камер у серці людини?'), '4', true),
((SELECT id FROM questions WHERE text = 'Скільки камер у серці людини?'), '2', false),
((SELECT id FROM questions WHERE text = 'Скільки камер у серці людини?'), '3', false),
((SELECT id FROM questions WHERE text = 'Скільки камер у серці людини?'), '5', false);

-- Question 3: Найбільший мозок у людському тілі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Найбільший мозок у людському тілі?'), 'Головний мозок', true),
((SELECT id FROM questions WHERE text = 'Найбільший мозок у людському тілі?'), 'Спинний мозок', false),
((SELECT id FROM questions WHERE text = 'Найбільший мозок у людському тілі?'), 'Мозочок', false),
((SELECT id FROM questions WHERE text = 'Найбільший мозок у людському тілі?'), 'Проміжний мозок', false);

-- Question 4: Хто відкрив пеніцилін?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хто відкрив пеніцилін?'), 'Олександр Флемінг', true),
((SELECT id FROM questions WHERE text = 'Хто відкрив пеніцилін?'), 'Луї Пастер', false),
((SELECT id FROM questions WHERE text = 'Хто відкрив пеніцилін?'), 'Роберт Кох', false),
((SELECT id FROM questions WHERE text = 'Хто відкрив пеніцилін?'), 'Іван Павлов', false);

-- Chemistry test (2 attempts, shows correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Основи хімії',
    (SELECT id FROM subjects WHERE name = 'Хімія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Основи хімії (показує правильні відповіді)',
    true,
    2
) RETURNING id AS test_id;

-- Questions for Chemistry test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Основи хімії'), 'Хімічна формула води?', 0),
((SELECT id FROM tests WHERE title = 'Основи хімії'), 'Атомний номер водню?', 1),
((SELECT id FROM tests WHERE title = 'Основи хімії'), 'Що таке pH 7?', 2);

-- Options for Chemistry questions
-- Question 1: Хімічна формула води?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хімічна формула води?'), 'H₂O', true),
((SELECT id FROM questions WHERE text = 'Хімічна формула води?'), 'CO₂', false),
((SELECT id FROM questions WHERE text = 'Хімічна формула води?'), 'O₂', false),
((SELECT id FROM questions WHERE text = 'Хімічна формула води?'), 'H₂O₂', false);

-- Question 2: Атомний номер водню?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Атомний номер водню?'), '1', true),
((SELECT id FROM questions WHERE text = 'Атомний номер водню?'), '2', false),
((SELECT id FROM questions WHERE text = 'Атомний номер водню?'), '8', false),
((SELECT id FROM questions WHERE text = 'Атомний номер водню?'), '6', false);

-- Question 3: Що таке pH 7?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Що таке pH 7?'), 'Нейтральний', true),
((SELECT id FROM questions WHERE text = 'Що таке pH 7?'), 'Кислий', false),
((SELECT id FROM questions WHERE text = 'Що таке pH 7?'), 'Лужний', false),
((SELECT id FROM questions WHERE text = 'Що таке pH 7?'), 'Солоний', false);

-- Physics test (1 attempt, hides correct answers)

INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts)
VALUES (
    'Основи фізики',
    (SELECT id FROM subjects WHERE name = 'Фізика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Основи фізики (правильні відповіді приховано)',
    false,
    1
) RETURNING id AS test_id;

-- Questions for Physics test
INSERT INTO questions (test_id, text, question_order) VALUES
((SELECT id FROM tests WHERE title = 'Основи фізики'), 'Швидкість світла у вакуумі?', 0),
((SELECT id FROM tests WHERE title = 'Основи фізики'), 'Що вимірюється в Ньютонах?', 1),
((SELECT id FROM tests WHERE title = 'Основи фізики'), 'Що таке гравітація?', 2),
((SELECT id FROM tests WHERE title = 'Основи фізики'), 'Темперура кипіння води за нормальних умов?', 3);

-- Options for Physics questions
-- Question 1: Швидкість світла у вакуумі?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Швидкість світла у вакуумі?'), '300,000 км/с', true),
((SELECT id FROM questions WHERE text = 'Швидкість світла у вакуумі?'), '150,000 км/с', false),
((SELECT id FROM questions WHERE text = 'Швидкість світла у вакуумі?'), '1,000,000 км/с', false),
((SELECT id FROM questions WHERE text = 'Швидкість світла у вакуумі?'), '30,000 км/с', false);

-- Question 2: Що вимірюється в Ньютонах?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Що вимірюється в Ньютонах?'), 'Сила', true),
((SELECT id FROM questions WHERE text = 'Що вимірюється в Ньютонах?'), 'Маса', false),
((SELECT id FROM questions WHERE text = 'Що вимірюється в Ньютонах?'), 'Швидкість', false),
((SELECT id FROM questions WHERE text = 'Що вимірюється в Ньютонах?'), 'Температура', false);

-- Question 3: Що таке гравітація?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Що таке гравітація?'), 'Сила притягання між масами', true),
((SELECT id FROM questions WHERE text = 'Що таке гравітація?'), 'Сила відштовхування', false),
((SELECT id FROM questions WHERE text = 'Що таке гравітація?'), 'Електрична сила', false),
((SELECT id FROM questions WHERE text = 'Що таке гравітація?'), 'Магнітна сила', false);

-- Question 4: Темперура кипіння води за нормальних умов?
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Темперура кипіння води за нормальних умов?'), '100°C', true),
((SELECT id FROM questions WHERE text = 'Темперура кипіння води за нормальних умов?'), '0°C', false),
((SELECT id FROM questions WHERE text = 'Темперура кипіння води за нормальних умов?'), '50°C', false),
((SELECT id FROM questions WHERE text = 'Темперура кипіння води за нормальних умов?'), '200°C', false);


-- ============================================================
--  Additional diverse tests (re-run safe: removes by title first)
-- ============================================================

DELETE FROM tests WHERE title IN (
    'Клімат та біоми',
    'Європейські річки (приватний)',
    'Швидкий квіз: арифметика',
    'Алгебра: кілька правильних',
    'Друга світова війна',
    'Сонячна система (розширено)',
    'Phrasal verbs B1',
    'Deutsche Farben und Formen',
    'Гетьманщина XVII ст.',
    'Українські письменники XX ст.',
    'Клітина (приватний)',
    'Реакції та розчини',
    'Механіка: базовий курс',
    'Електрика експрес'
);

-- Географія: 2 питання × 2 варіанти, 15 хв, 5 спроб, показ відповідей
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Клімат та біоми',
    (SELECT id FROM subjects WHERE name = 'Географія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Короткий квіз про кліматичні зони.',
    true, 5, 15, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Клімат та біоми'), 'Клімат: Який клімат у Сахарі?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Клімат та біоми'), 'Клімат: Що таке тундра?', 1, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Клімат: Який клімат у Сахарі?'), 'Тропічний пустельний', true),
((SELECT id FROM questions WHERE text = 'Клімат: Який клімат у Сахарі?'), 'Помірний морський', false),
((SELECT id FROM questions WHERE text = 'Клімат: Що таке тундра?'), 'Зона вічної мерзлоти з рідкісною рослинністю', true),
((SELECT id FROM questions WHERE text = 'Клімат: Що таке тундра?'), 'Вологий субтропічний ліс', false);

-- Географія: приватний, код, 1 спроба, 10 хв, без показу правильних, 3×5 варіантів
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Європейські річки (приватний)',
    (SELECT id FROM subjects WHERE name = 'Географія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    false,
    'Приватний тест за кодом RIVR24.',
    false, 1, 10, 'RIVR24'
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Європейські річки (приватний)'), 'Річки: Найдовша річка Європи?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Європейські річки (приватний)'), 'Річки: Яка річка тече через Київ?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Європейські річки (приватний)'), 'Річки: Де впадає Дунай?', 2, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Річки: Найдовша річка Європи?'), 'Волга', true),
((SELECT id FROM questions WHERE text = 'Річки: Найдовша річка Європи?'), 'Дунай', false),
((SELECT id FROM questions WHERE text = 'Річки: Найдовша річка Європи?'), 'Рейн', false),
((SELECT id FROM questions WHERE text = 'Річки: Найдовша річка Європи?'), 'Сена', false),
((SELECT id FROM questions WHERE text = 'Річки: Найдовша річка Європи?'), 'Ельба', false),
((SELECT id FROM questions WHERE text = 'Річки: Яка річка тече через Київ?'), 'Дніпро', true),
((SELECT id FROM questions WHERE text = 'Річки: Яка річка тече через Київ?'), 'Дністер', false),
((SELECT id FROM questions WHERE text = 'Річки: Яка річка тече через Київ?'), 'Південний Буг', false),
((SELECT id FROM questions WHERE text = 'Річки: Яка річка тече через Київ?'), 'Тиса', false),
((SELECT id FROM questions WHERE text = 'Річки: Яка річка тече через Київ?'), 'Сіверський Дінець', false),
((SELECT id FROM questions WHERE text = 'Річки: Де впадає Дунай?'), 'Чорне море', true),
((SELECT id FROM questions WHERE text = 'Річки: Де впадає Дунай?'), 'Балтійське море', false),
((SELECT id FROM questions WHERE text = 'Річки: Де впадає Дунай?'), 'Середземне море', false),
((SELECT id FROM questions WHERE text = 'Річки: Де впадає Дунай?'), 'Північне море', false),
((SELECT id FROM questions WHERE text = 'Річки: Де впадає Дунай?'), 'Каспійське море', false);

-- Математика: 2×3, 5 хв, 2 спроби, приховані відповіді
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Швидкий квіз: арифметика',
    (SELECT id FROM subjects WHERE name = 'Математика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Експрес-перевірка арифметики за 5 хвилин.',
    false, 2, 5, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Швидкий квіз: арифметика'), 'Арифм: 12 + 8 = ?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Швидкий квіз: арифметика'), 'Арифм: 9 × 7 = ?', 1, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Арифм: 12 + 8 = ?'), '20', true),
((SELECT id FROM questions WHERE text = 'Арифм: 12 + 8 = ?'), '19', false),
((SELECT id FROM questions WHERE text = 'Арифм: 12 + 8 = ?'), '21', false),
((SELECT id FROM questions WHERE text = 'Арифм: 9 × 7 = ?'), '63', true),
((SELECT id FROM questions WHERE text = 'Арифм: 9 × 7 = ?'), '56', false),
((SELECT id FROM questions WHERE text = 'Арифм: 9 × 7 = ?'), '72', false);

-- Математика: multiple choice, необмежено спроб, без ліміту часу
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Алгебра: кілька правильних',
    (SELECT id FROM subjects WHERE name = 'Математика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Питання з кількома правильними відповідями.',
    true, NULL, NULL, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Алгебра: кілька правильних'), 'Алгебра: Позначте парні числа', 0, 'multiple_choice'),
((SELECT id FROM tests WHERE title = 'Алгебра: кілька правильних'), 'Алгебра: Скільки буде 7 × 8?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Алгебра: кілька правильних'), 'Алгебра: Позначте прості числа', 2, 'multiple_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '2', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '4', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '5', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '7', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '8', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте парні числа'), '11', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Скільки буде 7 × 8?'), '56', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Скільки буде 7 × 8?'), '54', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Скільки буде 7 × 8?'), '64', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте прості числа'), '2', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте прості числа'), '3', true),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте прості числа'), '4', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте прості числа'), '9', false),
((SELECT id FROM questions WHERE text = 'Алгебра: Позначте прості числа'), '15', false);

-- Історія: приватний, 3 спроби, 25 хв, 6 питань
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Друга світова війна',
    (SELECT id FROM subjects WHERE name = 'Історія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    false,
    'Приватний тест за кодом WW2UKR.',
    true, 3, 25, 'WW2UKR'
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Рік початку Другої світової?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Дата перемоги в Європі (VE Day)?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Хто був лідером нацистської Німеччини?', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Битва на Волзі — місто?', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Коли відкрили другий фронт у Нормандії?', 4, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Друга світова війна'), 'ДСВ: Яка країна скинула атомні бомби?', 5, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'ДСВ: Рік початку Другої світової?'), '1939', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Рік початку Другої світової?'), '1914', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Рік початку Другої світової?'), '1945', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Рік початку Другої світової?'), '1936', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Дата перемоги в Європі (VE Day)?'), '8 травня 1945', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Дата перемоги в Європі (VE Day)?'), '9 травня 1945', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Дата перемоги в Європі (VE Day)?'), '1 вересня 1939', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Дата перемоги в Європі (VE Day)?'), '22 червня 1941', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Хто був лідером нацистської Німеччини?'), 'Адольф Гітлер', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Хто був лідером нацистської Німеччини?'), 'Беніто Муссоліні', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Хто був лідером нацистської Німеччини?'), 'Франклін Рузвельт', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Хто був лідером нацистської Німеччини?'), 'Вінстон Черчілль', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Битва на Волзі — місто?'), 'Сталінград', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Битва на Волзі — місто?'), 'Берлін', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Битва на Волзі — місто?'), 'Париж', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Битва на Волзі — місто?'), 'Варшава', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Коли відкрили другий фронт у Нормандії?'), '6 червня 1944', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Коли відкрили другий фронт у Нормандії?'), '22 червня 1941', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Коли відкрили другий фронт у Нормандії?'), '8 травня 1945', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Коли відкрили другий фронт у Нормандії?'), '1 грудня 1918', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Яка країна скинула атомні бомби?'), 'США', true),
((SELECT id FROM questions WHERE text = 'ДСВ: Яка країна скинула атомні бомби?'), 'Велика Британія', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Яка країна скинула атомні бомби?'), 'СРСР', false),
((SELECT id FROM questions WHERE text = 'ДСВ: Яка країна скинула атомні бомби?'), 'Японія', false);

-- Астрономія: 8 питань, без ліміту спроб, 30 хв
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Сонячна система (розширено)',
    (SELECT id FROM subjects WHERE name = 'Астрономія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Розширений курс по планетах і малих тілах.',
    true, NULL, 30, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Яка зірка в центрі Сонячної системи?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Супутник Землі?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Пояс між Марсом і Юпітером?', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Найменша планета?', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Планета з кільцями?', 4, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Комета склається переважно з?', 5, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Скільки супутників у Землі?', 6, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Сонячна система (розширено)'), 'Астро: Найдалі від Сонця планета?', 7, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Астро: Яка зірка в центрі Сонячної системи?'), 'Сонце', true),
((SELECT id FROM questions WHERE text = 'Астро: Яка зірка в центрі Сонячної системи?'), 'Полярна', false),
((SELECT id FROM questions WHERE text = 'Астро: Яка зірка в центрі Сонячної системи?'), 'Сіріус', false),
((SELECT id FROM questions WHERE text = 'Астро: Супутник Землі?'), 'Місяць', true),
((SELECT id FROM questions WHERE text = 'Астро: Супутник Землі?'), 'Титан', false),
((SELECT id FROM questions WHERE text = 'Астро: Супутник Землі?'), 'Європа', false),
((SELECT id FROM questions WHERE text = 'Астро: Пояс між Марсом і Юпітером?'), 'Пояс астероїдів', true),
((SELECT id FROM questions WHERE text = 'Астро: Пояс між Марсом і Юпітером?'), 'Пояс Койпера', false),
((SELECT id FROM questions WHERE text = 'Астро: Пояс між Марсом і Юпітером?'), 'Орбіта Плутона', false),
((SELECT id FROM questions WHERE text = 'Астро: Найменша планета?'), 'Меркурій', true),
((SELECT id FROM questions WHERE text = 'Астро: Найменша планета?'), 'Марс', false),
((SELECT id FROM questions WHERE text = 'Астро: Найменша планета?'), 'Венера', false),
((SELECT id FROM questions WHERE text = 'Астро: Планета з кільцями?'), 'Сатурн', true),
((SELECT id FROM questions WHERE text = 'Астро: Планета з кільцями?'), 'Меркурій', false),
((SELECT id FROM questions WHERE text = 'Астро: Планета з кільцями?'), 'Венера', false),
((SELECT id FROM questions WHERE text = 'Астро: Комета склається переважно з?'), 'Льоду та пилу', true),
((SELECT id FROM questions WHERE text = 'Астро: Комета склається переважно з?'), 'Рідкого заліза', false),
((SELECT id FROM questions WHERE text = 'Астро: Комета склається переважно з?'), 'Метану в газі', false),
((SELECT id FROM questions WHERE text = 'Астро: Скільки супутників у Землі?'), '1', true),
((SELECT id FROM questions WHERE text = 'Астро: Скільки супутників у Землі?'), '2', false),
((SELECT id FROM questions WHERE text = 'Астро: Скільки супутників у Землі?'), '0', false),
((SELECT id FROM questions WHERE text = 'Астро: Найдалі від Сонця планета?'), 'Нептун', true),
((SELECT id FROM questions WHERE text = 'Астро: Найдалі від Сонця планета?'), 'Уран', false),
((SELECT id FROM questions WHERE text = 'Астро: Найдалі від Сонця планета?'), 'Юпітер', false);

-- English: приватний, 2 спроби, 12 хв, 4 питання (одне з 8 варіантів)
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Phrasal verbs B1',
    (SELECT id FROM subjects WHERE name = 'Англійська мова'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    false,
    'Приватний тест за кодом ENPHR24.',
    false, 2, 12, 'ENPHR24'
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Phrasal verbs B1'), 'Phrasal: give ___ = surrender', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Phrasal verbs B1'), 'Phrasal: look ___ = investigate', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Phrasal verbs B1'), 'Phrasal: turn ___ = arrive', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Phrasal verbs B1'), 'Phrasal: put ___ = postpone', 3, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'up', true),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'in', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'on', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'off', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'away', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'over', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'out', false),
((SELECT id FROM questions WHERE text = 'Phrasal: give ___ = surrender'), 'down', false),
((SELECT id FROM questions WHERE text = 'Phrasal: look ___ = investigate'), 'into', true),
((SELECT id FROM questions WHERE text = 'Phrasal: look ___ = investigate'), 'at', false),
((SELECT id FROM questions WHERE text = 'Phrasal: look ___ = investigate'), 'for', false),
((SELECT id FROM questions WHERE text = 'Phrasal: look ___ = investigate'), 'after', false),
((SELECT id FROM questions WHERE text = 'Phrasal: turn ___ = arrive'), 'up', true),
((SELECT id FROM questions WHERE text = 'Phrasal: turn ___ = arrive'), 'down', false),
((SELECT id FROM questions WHERE text = 'Phrasal: turn ___ = arrive'), 'off', false),
((SELECT id FROM questions WHERE text = 'Phrasal: put ___ = postpone'), 'off', true),
((SELECT id FROM questions WHERE text = 'Phrasal: put ___ = postpone'), 'on', false),
((SELECT id FROM questions WHERE text = 'Phrasal: put ___ = postpone'), 'up', false);

-- Німецька: 5 спроб, 3 питання (одне з 10 варіантів)
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Deutsche Farben und Formen',
    (SELECT id FROM subjects WHERE name = 'Німецька мова'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Кольори та базові слова.',
    true, 5, NULL, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Deutsche Farben und Formen'), 'DE: rot = ?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Deutsche Farben und Formen'), 'DE: blau = ?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Deutsche Farben und Formen'), 'DE: das Buch — артикль?', 2, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'червоний', true),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'синій', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'зелений', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'жовтий', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'чорний', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'білий', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'рожевий', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'коричневий', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'фіолетовий', false),
((SELECT id FROM questions WHERE text = 'DE: rot = ?'), 'сірий', false),
((SELECT id FROM questions WHERE text = 'DE: blau = ?'), 'синій', true),
((SELECT id FROM questions WHERE text = 'DE: blau = ?'), 'червоний', false),
((SELECT id FROM questions WHERE text = 'DE: blau = ?'), 'зелений', false),
((SELECT id FROM questions WHERE text = 'DE: das Buch — артикль?'), 'das', true),
((SELECT id FROM questions WHERE text = 'DE: das Buch — артикль?'), 'der', false),
((SELECT id FROM questions WHERE text = 'DE: das Buch — артикль?'), 'die', false);

-- Історія України: 1 спроба, 5 питань
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Гетьманщина XVII ст.',
    (SELECT id FROM subjects WHERE name = 'Історія України'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Гетьманська доба — одна офіційна спроба.',
    false, 1, NULL, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Гетьманщина XVII ст.'), 'Гетьм: Перший гетьман? (1648)', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Гетьманщина XVII ст.'), 'Гетьм: Столиця Гетьманщини?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Гетьманщина XVII ст.'), 'Гетьм: Договір 1654 з…', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Гетьманщина XVII ст.'), 'Гетьм: Битва під Полтавою — рік?', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Гетьманщина XVII ст.'), 'Гетьм: Гетьман за Мазепи?', 4, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Гетьм: Перший гетьман? (1648)'), 'Богдан Хмельницький', true),
((SELECT id FROM questions WHERE text = 'Гетьм: Перший гетьман? (1648)'), 'Іван Мазепа', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Перший гетьман? (1648)'), 'Петро Дорошенко', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Столиця Гетьманщини?'), 'Чигирин / Батурин', true),
((SELECT id FROM questions WHERE text = 'Гетьм: Столиця Гетьманщини?'), 'Київ', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Столиця Гетьманщини?'), 'Львів', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Договір 1654 з…'), 'Росією', true),
((SELECT id FROM questions WHERE text = 'Гетьм: Договір 1654 з…'), 'Польщею', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Договір 1654 з…'), 'Туреччиною', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Битва під Полтавою — рік?'), '1709', true),
((SELECT id FROM questions WHERE text = 'Гетьм: Битва під Полтавою — рік?'), '1648', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Битва під Полтавою — рік?'), '1654', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Гетьман за Мазепи?'), 'Іван Мазепа', true),
((SELECT id FROM questions WHERE text = 'Гетьм: Гетьман за Мазепи?'), 'Богдан Хмельницький', false),
((SELECT id FROM questions WHERE text = 'Гетьм: Гетьман за Мазепи?'), 'Петро Сагайдачний', false);

-- Література: 7 питань × 3 варіанти, без обмежень
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Українські письменники XX ст.',
    (SELECT id FROM subjects WHERE name = 'Література'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Автори та твори XX століття.',
    true, NULL, NULL, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: Автор «Лісової пісні»?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Місто» — автор?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Тигролови» — автор?', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Земля» — автор?', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Собор» — автор?', 4, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Кайдашева сім’я»?', 5, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Українські письменники XX ст.'), 'Літ XX: «Майстер і Маргарита» українською?', 6, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Літ XX: Автор «Лісової пісні»?'), 'Леся Українка', true),
((SELECT id FROM questions WHERE text = 'Літ XX: Автор «Лісової пісні»?'), 'Тарас Шевченко', false),
((SELECT id FROM questions WHERE text = 'Літ XX: Автор «Лісової пісні»?'), 'Іван Франко', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Місто» — автор?'), 'Валеріян Підмогильний', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Місто» — автор?'), 'Ольга Кобилянська', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Місто» — автор?'), 'Михайло Коцюбинський', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Тигролови» — автор?'), 'Іван Багряний', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Тигролови» — автор?'), 'Юрій Яновський', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Тигролови» — автор?'), 'Василь Стус', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Земля» — автор?'), 'Ольга Кобилянська', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Земля» — автор?'), 'Леся Українка', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Земля» — автор?'), 'Панас Мирний', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Собор» — автор?'), 'Олесь Гончар', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Собор» — автор?'), 'Іван Драч', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Собор» — автор?'), 'Ліна Костенко', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Кайдашева сім’я»?'), 'Іван Нечуй-Левицький', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Кайдашева сім’я»?'), 'Іван Франко', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Кайдашева сім’я»?'), 'Марко Вовчок', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Майстер і Маргарита» українською?'), 'Немає (Булгаков, рос.)', true),
((SELECT id FROM questions WHERE text = 'Літ XX: «Майстер і Маргарита» українською?'), 'Юрій Андрухович', false),
((SELECT id FROM questions WHERE text = 'Літ XX: «Майстер і Маргарита» українською?'), 'Василь Симоненко', false);

-- Біологія: приватний BIOCEL, 4 спроби, 18 хв, 4 питання (1 multiple choice)
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Клітина (приватний)',
    (SELECT id FROM subjects WHERE name = 'Біологія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    false,
    'Приватний тест за кодом BIOCEL.',
    true, 4, 18, 'BIOCEL'
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Клітина (приватний)'), 'Біо: Основна енергетична станція клітини?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Клітина (приватний)'), 'Біо: ДНК знаходиться в…', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Клітина (приватний)'), 'Біо: Органели рослинної клітини', 2, 'multiple_choice'),
((SELECT id FROM tests WHERE title = 'Клітина (приватний)'), 'Біо: Скільки хромосом у людини?', 3, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Біо: Основна енергетична станція клітини?'), 'Мітохондрія', true),
((SELECT id FROM questions WHERE text = 'Біо: Основна енергетична станція клітини?'), 'Ядро', false),
((SELECT id FROM questions WHERE text = 'Біо: Основна енергетична станція клітини?'), 'Рибосома', false),
((SELECT id FROM questions WHERE text = 'Біо: ДНК знаходиться в…'), 'Ядрі', true),
((SELECT id FROM questions WHERE text = 'Біо: ДНК знаходиться в…'), 'Лізосомі', false),
((SELECT id FROM questions WHERE text = 'Біо: ДНК знаходиться в…'), 'Центріолі', false),
((SELECT id FROM questions WHERE text = 'Біо: Органели рослинної клітини'), 'Хлоропласт', true),
((SELECT id FROM questions WHERE text = 'Біо: Органели рослинної клітини'), 'Клітинна стінка', true),
((SELECT id FROM questions WHERE text = 'Біо: Органели рослинної клітини'), 'Мітохондрія', false),
((SELECT id FROM questions WHERE text = 'Біо: Органели рослинної клітини'), 'Центріоль', false),
((SELECT id FROM questions WHERE text = 'Біо: Органели рослинної клітини'), 'Рибосома', false),
((SELECT id FROM questions WHERE text = 'Біо: Скільки хромосом у людини?'), '46', true),
((SELECT id FROM questions WHERE text = 'Біо: Скільки хромосом у людини?'), '23', false),
((SELECT id FROM questions WHERE text = 'Біо: Скільки хромосом у людини?'), '48', false);

-- Хімія: 6×5, 2 спроби, 15 хв
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Реакції та розчини',
    (SELECT id FROM subjects WHERE name = 'Хімія'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Розчини, кислоти та основи.',
    false, 2, 15, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: Формула соляної кислоти?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: pH < 7 означає…', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: Найлегший газ?', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: Символ заліза?', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: Кисень у повітрі ≈', 4, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Реакції та розчини'), 'Хім: NaCl — це…', 5, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Хім: Формула соляної кислоти?'), 'HCl', true),
((SELECT id FROM questions WHERE text = 'Хім: Формула соляної кислоти?'), 'H₂SO₄', false),
((SELECT id FROM questions WHERE text = 'Хім: Формула соляної кислоти?'), 'HNO₃', false),
((SELECT id FROM questions WHERE text = 'Хім: Формула соляної кислоти?'), 'NaOH', false),
((SELECT id FROM questions WHERE text = 'Хім: Формула соляної кислоти?'), 'CH₄', false),
((SELECT id FROM questions WHERE text = 'Хім: pH < 7 означає…'), 'Кисле середовище', true),
((SELECT id FROM questions WHERE text = 'Хім: pH < 7 означає…'), 'Лужне', false),
((SELECT id FROM questions WHERE text = 'Хім: pH < 7 означає…'), 'Нейтральне', false),
((SELECT id FROM questions WHERE text = 'Хім: pH < 7 означає…'), 'Солоне', false),
((SELECT id FROM questions WHERE text = 'Хім: pH < 7 означає…'), 'Окисне', false),
((SELECT id FROM questions WHERE text = 'Хім: Найлегший газ?'), 'Водень (H₂)', true),
((SELECT id FROM questions WHERE text = 'Хім: Найлегший газ?'), 'Кисень', false),
((SELECT id FROM questions WHERE text = 'Хім: Найлегший газ?'), 'Азот', false),
((SELECT id FROM questions WHERE text = 'Хім: Найлегший газ?'), 'CO₂', false),
((SELECT id FROM questions WHERE text = 'Хім: Найлегший газ?'), 'Гелій', false),
((SELECT id FROM questions WHERE text = 'Хім: Символ заліза?'), 'Fe', true),
((SELECT id FROM questions WHERE text = 'Хім: Символ заліза?'), 'Zn', false),
((SELECT id FROM questions WHERE text = 'Хім: Символ заліза?'), 'Cu', false),
((SELECT id FROM questions WHERE text = 'Хім: Символ заліза?'), 'Ag', false),
((SELECT id FROM questions WHERE text = 'Хім: Символ заліза?'), 'Au', false),
((SELECT id FROM questions WHERE text = 'Хім: Кисень у повітрі ≈'), '21%', true),
((SELECT id FROM questions WHERE text = 'Хім: Кисень у повітрі ≈'), '78%', false),
((SELECT id FROM questions WHERE text = 'Хім: Кисень у повітрі ≈'), '50%', false),
((SELECT id FROM questions WHERE text = 'Хім: Кисень у повітрі ≈'), '10%', false),
((SELECT id FROM questions WHERE text = 'Хім: Кисень у повітрі ≈'), '5%', false),
((SELECT id FROM questions WHERE text = 'Хім: NaCl — це…'), 'Сіль', true),
((SELECT id FROM questions WHERE text = 'Хім: NaCl — це…'), 'Цукор', false),
((SELECT id FROM questions WHERE text = 'Хім: NaCl — це…'), 'Кислота', false),
((SELECT id FROM questions WHERE text = 'Хім: NaCl — це…'), 'Спирт', false),
((SELECT id FROM questions WHERE text = 'Хім: NaCl — це…'), 'Вода', false);

-- Фізика: 10 питань, 3 спроби, 20 хв
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Механіка: базовий курс',
    (SELECT id FROM subjects WHERE name = 'Фізика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Довший тест з механіки.',
    true, 3, 20, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: v = s / t — це…', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Одиниця сили?', 1, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: F = m × a — закон…', 2, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: g на Землі ≈', 3, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Інерція — це…', 4, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Кінетична енергія залежить від…', 5, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Потужність P = …', 6, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Щільність ρ = …', 7, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Тертя сповільнює…', 8, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Механіка: базовий курс'), 'Мех: Вага тіла P = …', 9, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Мех: v = s / t — це…'), 'Швидкість', true),
((SELECT id FROM questions WHERE text = 'Мех: v = s / t — це…'), 'Прискорення', false),
((SELECT id FROM questions WHERE text = 'Мех: v = s / t — це…'), 'Сила', false),
((SELECT id FROM questions WHERE text = 'Мех: v = s / t — це…'), 'Імпульс', false),
((SELECT id FROM questions WHERE text = 'Мех: Одиниця сили?'), 'Ньютон', true),
((SELECT id FROM questions WHERE text = 'Мех: Одиниця сили?'), 'Джоуль', false),
((SELECT id FROM questions WHERE text = 'Мех: Одиниця сили?'), 'Ват', false),
((SELECT id FROM questions WHERE text = 'Мех: Одиниця сили?'), 'Паскаль', false),
((SELECT id FROM questions WHERE text = 'Мех: F = m × a — закон…'), 'Ньютона II', true),
((SELECT id FROM questions WHERE text = 'Мех: F = m × a — закон…'), 'Архімеда', false),
((SELECT id FROM questions WHERE text = 'Мех: F = m × a — закон…'), 'Гука', false),
((SELECT id FROM questions WHERE text = 'Мех: F = m × a — закон…'), 'Кулона', false),
((SELECT id FROM questions WHERE text = 'Мех: g на Землі ≈'), '9,8 м/с²', true),
((SELECT id FROM questions WHERE text = 'Мех: g на Землі ≈'), '10 м/с', false),
((SELECT id FROM questions WHERE text = 'Мех: g на Землі ≈'), '1,6 м/с²', false),
((SELECT id FROM questions WHERE text = 'Мех: g на Землі ≈'), '0 м/с²', false),
((SELECT id FROM questions WHERE text = 'Мех: Інерція — це…'), 'Властивість зберігати рух', true),
((SELECT id FROM questions WHERE text = 'Мех: Інерція — це…'), 'Сила тяжіння', false),
((SELECT id FROM questions WHERE text = 'Мех: Інерція — це…'), 'Електричний заряд', false),
((SELECT id FROM questions WHERE text = 'Мех: Інерція — це…'), 'Тиск рідини', false),
((SELECT id FROM questions WHERE text = 'Мех: Кінетична енергія залежить від…'), 'Маси та швидкості', true),
((SELECT id FROM questions WHERE text = 'Мех: Кінетична енергія залежить від…'), 'Обʼєму', false),
((SELECT id FROM questions WHERE text = 'Мех: Кінетична енергія залежить від…'), 'Температури', false),
((SELECT id FROM questions WHERE text = 'Мех: Кінетична енергія залежить від…'), 'Кольору', false),
((SELECT id FROM questions WHERE text = 'Мех: Потужність P = …'), 'W / t', true),
((SELECT id FROM questions WHERE text = 'Мех: Потужність P = …'), 'm × v', false),
((SELECT id FROM questions WHERE text = 'Мех: Потужність P = …'), 'F / s', false),
((SELECT id FROM questions WHERE text = 'Мех: Потужність P = …'), 'ρ × g', false),
((SELECT id FROM questions WHERE text = 'Мех: Щільність ρ = …'), 'm / V', true),
((SELECT id FROM questions WHERE text = 'Мех: Щільність ρ = …'), 'V / m', false),
((SELECT id FROM questions WHERE text = 'Мех: Щільність ρ = …'), 'F × a', false),
((SELECT id FROM questions WHERE text = 'Мех: Щільність ρ = …'), 's × t', false),
((SELECT id FROM questions WHERE text = 'Мех: Тертя сповільнює…'), 'Рух', true),
((SELECT id FROM questions WHERE text = 'Мех: Тертя сповільнює…'), 'Світло', false),
((SELECT id FROM questions WHERE text = 'Мех: Тертя сповільнює…'), 'Звук у вакуумі', false),
((SELECT id FROM questions WHERE text = 'Мех: Тертя сповільнює…'), 'Гравітацію', false),
((SELECT id FROM questions WHERE text = 'Мех: Вага тіла P = …'), 'm × g', true),
((SELECT id FROM questions WHERE text = 'Мех: Вага тіла P = …'), 'm / g', false),
((SELECT id FROM questions WHERE text = 'Мех: Вага тіла P = …'), 'F × t', false),
((SELECT id FROM questions WHERE text = 'Мех: Вага тіла P = …'), 'ρ × V', false);

-- Фізика: 2×6, 1 спроба, 8 хв
INSERT INTO tests (title, subject_id, teacher_id, is_public, description, show_answer_correctness, max_attempts, time_limit_minutes, access_code)
VALUES (
    'Електрика експрес',
    (SELECT id FROM subjects WHERE name = 'Фізика'),
    (SELECT id FROM users WHERE role = 'teacher' LIMIT 1),
    true,
    'Короткий тест з електрики.',
    false, 1, 8, NULL
);
INSERT INTO questions (test_id, text, question_order, question_type) VALUES
((SELECT id FROM tests WHERE title = 'Електрика експрес'), 'Ел: Одиниця струму?', 0, 'single_choice'),
((SELECT id FROM tests WHERE title = 'Електрика експрес'), 'Ел: Закон Ома: U = …', 1, 'single_choice');
INSERT INTO options (question_id, text, is_correct) VALUES
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Ампер', true),
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Вольт', false),
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Ом', false),
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Ват', false),
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Кулон', false),
((SELECT id FROM questions WHERE text = 'Ел: Одиниця струму?'), 'Тесла', false),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'I × R', true),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'I / R', false),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'R / I', false),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'I + R', false),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'I² × R', false),
((SELECT id FROM questions WHERE text = 'Ел: Закон Ома: U = …'), 'R² × I', false);


-- ============================================================
--  Sample students, sessions, and answers
-- ============================================================

DELETE FROM session_answers
WHERE session_id IN (
    SELECT ts.id
    FROM test_sessions ts
    JOIN users u ON u.id = ts.student_id
    WHERE u.telegram_id BETWEEN 900000001 AND 900000099
);

DELETE FROM test_sessions
WHERE student_id IN (
    SELECT id FROM users WHERE telegram_id BETWEEN 900000001 AND 900000099
);

DELETE FROM users WHERE telegram_id BETWEEN 900000001 AND 900000099;

INSERT INTO users (telegram_id, name, role, language) VALUES
    (900000001, 'Олена Коваленко', 'student', 'uk'),
    (900000002, 'Іван Петренко', 'student', 'uk'),
    (900000003, 'Марія Шевченко', 'student', 'uk'),
    (900000004, 'Андрій Бондаренко', 'student', 'uk'),
    (900000005, 'Софія Мельник', 'student', 'uk'),
    (900000006, 'Дмитро Іваненко', 'student', 'uk'),
    (900000007, 'Катерина Лисенко', 'student', 'uk'),
    (900000008, 'Максим Ткаченко', 'student', 'en');


-- Helper: insert one completed session and answers for single-choice tests.
-- p_wrong: array of question texts answered incorrectly (empty = all correct).
DO $seed$
DECLARE
    v_sid BIGINT;
    v_tid BIGINT;
    v_uid BIGINT;
    v_wrong TEXT[] := ARRAY[]::TEXT[];
BEGIN
    -- ── Столиці світу (4 питання) ──────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Столиці світу' LIMIT 1;

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '6 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid
      AND NOT (q.text = ANY (v_wrong));

    v_wrong := ARRAY['Яка столиця Іспанії?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false
    FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Барселона'
    WHERE q.test_id = v_tid AND q.text = 'Яка столиця Іспанії?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '5 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));

    v_wrong := ARRAY['Яка столиця Франції?', 'Яка столиця Німеччини?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Ліон'
    WHERE q.test_id = v_tid AND q.text = 'Яка столиця Франції?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Мюнхен'
    WHERE q.test_id = v_tid AND q.text = 'Яка столиця Німеччини?';

    v_wrong := ARRAY['Яка столиця Італії?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '7 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Мілан'
    WHERE q.test_id = v_tid AND q.text = 'Яка столиця Італії?';

    -- ── Історія України (4) ─────────────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Історія України' LIMIT 1;

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '12 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));

    v_wrong := ARRAY['Коли відбулася Хрещення Русі?', 'Коли Україна проголосила незалежність?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days' + INTERVAL '14 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1015 рік'
    WHERE q.test_id = v_tid AND q.text = 'Коли відбулася Хрещення Русі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1 грудня 1991 року'
    WHERE q.test_id = v_tid AND q.text = 'Коли Україна проголосила незалежність?';

    -- Друга спроба Івана (покращення)
    v_wrong := ARRAY['Яка битва відбулася у 1240 році?'];
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Битва під Полтавою'
    WHERE q.test_id = v_tid AND q.text = 'Яка битва відбулася у 1240 році?';

    v_wrong := ARRAY['Хто був гетьманом України у 1648 році?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '13 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Іван Мазепа'
    WHERE q.test_id = v_tid AND q.text = 'Хто був гетьманом України у 1648 році?';

    v_wrong := ARRAY[
        'Коли відбулася Хрещення Русі?',
        'Хто був гетьманом України у 1648 році?',
        'Коли Україна проголосила незалежність?'
    ];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000008;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 4, 25, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '15 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1015 рік'
    WHERE q.test_id = v_tid AND q.text = 'Коли відбулася Хрещення Русі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Іван Мазепа'
    WHERE q.test_id = v_tid AND q.text = 'Хто був гетьманом України у 1648 році?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1 грудня 1991 року'
    WHERE q.test_id = v_tid AND q.text = 'Коли Україна проголосила незалежність?';

    -- ── Планети Сонячної системи (4) ───────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Планети Сонячної системи' LIMIT 1;

    v_wrong := ARRAY['Скільки планет у Сонячній системі?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '9'
    WHERE q.test_id = v_tid AND q.text = 'Скільки планет у Сонячній системі?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000007;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '6 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid;

    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000008;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 0, 4, 0, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '9'
    WHERE q.test_id = v_tid AND q.text = 'Скільки планет у Сонячній системі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Земля'
    WHERE q.test_id = v_tid AND q.text = 'Яка планета найближча до Сонця?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Сатурн'
    WHERE q.test_id = v_tid AND q.text = 'Яка планета найбільша у Сонячній системі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Венера'
    WHERE q.test_id = v_tid AND q.text = 'Яка планета відома як "Червона планета"?';

    -- ── English Grammar Basics (4) ─────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'English Grammar Basics' LIMIT 1;

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid;

    v_wrong := ARRAY['What is past tense of "go"?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'goed'
    WHERE q.test_id = v_tid AND q.text = 'What is past tense of "go"?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '7 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY[
        'What is correct form: "She ___ to school every day"?',
        'Choose correct article: "___ apple a day keeps doctor away"'
    ];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'go'
    WHERE q.test_id = v_tid AND q.text = 'What is correct form: "She ___ to school every day"?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'A'
    WHERE q.test_id = v_tid
      AND q.text = 'Choose correct article: "___ apple a day keeps doctor away"';

    v_wrong := ARRAY[
        'What is correct form: "She ___ to school every day"?',
        'Choose correct article: "___ apple a day keeps doctor away"',
        'What is past tense of "go"?'
    ];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 4, 25, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '12 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'go'
    WHERE q.test_id = v_tid AND q.text = 'What is correct form: "She ___ to school every day"?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'A'
    WHERE q.test_id = v_tid
      AND q.text = 'Choose correct article: "___ apple a day keeps doctor away"';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'goed'
    WHERE q.test_id = v_tid AND q.text = 'What is past tense of "go"?';

    -- ── Grundlagen der deutschen Sprache (4) ───────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Grundlagen der deutschen Sprache' LIMIT 1;

    v_wrong := ARRAY['Welcher Artikel gehört zu "Buch"?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000007;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'der'
    WHERE q.test_id = v_tid AND q.text = 'Welcher Artikel gehört zu "Buch"?';

    v_wrong := ARRAY['Was bedeutet "Haus" auf Englisch?', 'Wie heißt "cat" auf Deutsch?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'home'
    WHERE q.test_id = v_tid AND q.text = 'Was bedeutet "Haus" auf Englisch?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Hund'
    WHERE q.test_id = v_tid AND q.text = 'Wie heißt "cat" auf Deutsch?';

    -- ── Історія України (розширена) (4) ────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Історія України (розширена)' LIMIT 1;

    v_wrong := ARRAY['Коли прийнято Конституцію України?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '24 серпня 1991'
    WHERE q.test_id = v_tid AND q.text = 'Коли прийнято Конституцію України?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['Рік проголошення Незалежності України?', 'Хто був першим Президентом України?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000008;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '13 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1990'
    WHERE q.test_id = v_tid AND q.text = 'Рік проголошення Незалежності України?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Леонід Кучма'
    WHERE q.test_id = v_tid AND q.text = 'Хто був першим Президентом України?';

    -- ── Базова математика (5) ──────────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Базова математика' LIMIT 1;

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 5, 5, 100, NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['√64 = ?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 5, 80, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '6'
    WHERE q.test_id = v_tid AND q.text = '√64 = ?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 5, 5, 100, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '7 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['10 × 5 = ?', '2³ = ?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 5, 60, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '12 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '15'
    WHERE q.test_id = v_tid AND q.text = '10 × 5 = ?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '6'
    WHERE q.test_id = v_tid AND q.text = '2³ = ?';

    v_wrong := ARRAY['15 ÷ 3 = ?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 5, 80, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '12'
    WHERE q.test_id = v_tid AND q.text = '15 ÷ 3 = ?';

    v_wrong := ARRAY['2 + 2 = ?', '10 × 5 = ?', '√64 = ?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 5, 40, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '14 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '3'
    WHERE q.test_id = v_tid AND q.text = '2 + 2 = ?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '15'
    WHERE q.test_id = v_tid AND q.text = '10 × 5 = ?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '6'
    WHERE q.test_id = v_tid AND q.text = '√64 = ?';

    -- ── Українська література (3) ──────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Українська література' LIMIT 1;

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 3, 100, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '6 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['Хто написав "Лісова пісня"?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000007;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 3, 67, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Марко Вовчок'
    WHERE q.test_id = v_tid AND q.text = 'Хто написав "Лісова пісня"?';

    v_wrong := ARRAY['Хто написав "Кобзар"?', 'Автор "Захар Беркут"?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 3, 33, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '7 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Іван Франко'
    WHERE q.test_id = v_tid AND q.text = 'Хто написав "Кобзар"?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Тарас Шевченко'
    WHERE q.test_id = v_tid AND q.text = 'Автор "Захар Беркут"?';

    -- ── Основи біології (4) ─────────────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Основи біології' LIMIT 1;

    v_wrong := ARRAY['Хто відкрив пеніцилін?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Луї Пастер'
    WHERE q.test_id = v_tid AND q.text = 'Хто відкрив пеніцилін?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['Найбільша кістка в людському тілі?', 'Скільки камер у серці людини?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Череп'
    WHERE q.test_id = v_tid AND q.text = 'Найбільша кістка в людському тілі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '2'
    WHERE q.test_id = v_tid AND q.text = 'Скільки камер у серці людини?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    -- ── Основи хімії (3) ────────────────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Основи хімії' LIMIT 1;

    v_wrong := ARRAY['Атомний номер водню?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 3, 67, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '7 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '2'
    WHERE q.test_id = v_tid AND q.text = 'Атомний номер водню?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 3, 100, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '6 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['Хімічна формула води?', 'Що таке pH 7?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000008;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 3, 33, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '8 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'CO₂'
    WHERE q.test_id = v_tid AND q.text = 'Хімічна формула води?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Кислий'
    WHERE q.test_id = v_tid AND q.text = 'Що таке pH 7?';

    -- ── Основи фізики (4) ───────────────────────────────────────────────────
    SELECT id INTO v_tid FROM tests WHERE title = 'Основи фізики' LIMIT 1;

    v_wrong := ARRAY['Швидкість світла у вакуумі?', 'Що вимірюється в Ньютонах?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 4, 50, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '12 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '150,000 км/с'
    WHERE q.test_id = v_tid AND q.text = 'Швидкість світла у вакуумі?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Маса'
    WHERE q.test_id = v_tid AND q.text = 'Що вимірюється в Ньютонах?';

    v_wrong := ARRAY['Темперура кипіння води за нормальних умов?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000007;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '0°C'
    WHERE q.test_id = v_tid
      AND q.text = 'Темперура кипіння води за нормальних умов?';

    v_wrong := ARRAY['Що таке гравітація?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct
    FROM questions q JOIN options o ON o.question_id = q.id AND o.is_correct
    WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Сила відштовхування'
    WHERE q.test_id = v_tid AND q.text = 'Що таке гравітація?';

    -- ── Нові тести: проходження демо-студентами ─────────────────────────────

    -- Клімат та біоми (2)
    SELECT id INTO v_tid FROM tests WHERE title = 'Клімат та біоми' LIMIT 1;
    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 2, 100, NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days' + INTERVAL '4 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    v_wrong := ARRAY['Клімат: Що таке тундра?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 2, 50, NOW() - INTERVAL '13 days', NOW() - INTERVAL '13 days' + INTERVAL '5 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Вологий субтропічний ліс'
    WHERE q.test_id = v_tid AND q.text = 'Клімат: Що таке тундра?';

    -- Європейські річки (приватний) (3)
    SELECT id INTO v_tid FROM tests WHERE title = 'Європейські річки (приватний)' LIMIT 1;
    v_wrong := ARRAY['Річки: Де впадає Дунай?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 3, 67, NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Середземне море'
    WHERE q.test_id = v_tid AND q.text = 'Річки: Де впадає Дунай?';

    -- Швидкий квіз: арифметика (2)
    SELECT id INTO v_tid FROM tests WHERE title = 'Швидкий квіз: арифметика' LIMIT 1;
    v_wrong := ARRAY['Арифм: 9 × 7 = ?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 2, 50, NOW() - INTERVAL '11 days', NOW() - INTERVAL '11 days' + INTERVAL '3 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '56'
    WHERE q.test_id = v_tid AND q.text = 'Арифм: 9 × 7 = ?';

    -- Друга світова війна (6)
    SELECT id INTO v_tid FROM tests WHERE title = 'Друга світова війна' LIMIT 1;
    v_wrong := ARRAY['ДСВ: Битва на Волзі — місто?', 'ДСВ: Яка країна скинула атомні бомби?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 6, 67, NOW() - INTERVAL '16 days', NOW() - INTERVAL '16 days' + INTERVAL '22 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Берлін'
    WHERE q.test_id = v_tid AND q.text = 'ДСВ: Битва на Волзі — місто?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Японія'
    WHERE q.test_id = v_tid AND q.text = 'ДСВ: Яка країна скинула атомні бомби?';

    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 6, 6, 100, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '20 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    -- Сонячна система (розширено) (8)
    SELECT id INTO v_tid FROM tests WHERE title = 'Сонячна система (розширено)' LIMIT 1;
    v_wrong := ARRAY['Астро: Комета склається переважно з?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000007;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 7, 8, 88, NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days' + INTERVAL '25 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Рідкого заліза'
    WHERE q.test_id = v_tid AND q.text = 'Астро: Комета склається переважно з?';

    -- Phrasal verbs B1 (4)
    SELECT id INTO v_tid FROM tests WHERE title = 'Phrasal verbs B1' LIMIT 1;
    v_wrong := ARRAY['Phrasal: put ___ = postpone'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days' + INTERVAL '11 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'on'
    WHERE q.test_id = v_tid AND q.text = 'Phrasal: put ___ = postpone';

    -- Deutsche Farben (3)
    SELECT id INTO v_tid FROM tests WHERE title = 'Deutsche Farben und Formen' LIMIT 1;
    v_wrong := ARRAY[]::TEXT[];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000005;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 3, 100, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '6 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid;

    -- Гетьманщина (5)
    SELECT id INTO v_tid FROM tests WHERE title = 'Гетьманщина XVII ст.' LIMIT 1;
    v_wrong := ARRAY['Гетьм: Битва під Полтавою — рік?', 'Гетьм: Договір 1654 з…', 'Гетьм: Столиця Гетьманщини?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000008;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 5, 40, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '12 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = '1648'
    WHERE q.test_id = v_tid AND q.text = 'Гетьм: Битва під Полтавою — рік?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Польщею'
    WHERE q.test_id = v_tid AND q.text = 'Гетьм: Договір 1654 з…';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Львів'
    WHERE q.test_id = v_tid AND q.text = 'Гетьм: Столиця Гетьманщини?';

    -- Українські письменники XX ст. (7)
    SELECT id INTO v_tid FROM tests WHERE title = 'Українські письменники XX ст.' LIMIT 1;
    v_wrong := ARRAY['Літ XX: «Земля» — автор?', 'Літ XX: «Тигролови» — автор?'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 5, 7, 71, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '14 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Леся Українка'
    WHERE q.test_id = v_tid AND q.text = 'Літ XX: «Земля» — автор?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Юрій Яновський'
    WHERE q.test_id = v_tid AND q.text = 'Літ XX: «Тигролови» — автор?';

    -- Реакції та розчини (6)
    SELECT id INTO v_tid FROM tests WHERE title = 'Реакції та розчини' LIMIT 1;
    v_wrong := ARRAY['Хім: Символ заліза?', 'Хім: NaCl — це…'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 6, 67, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '13 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Zn'
    WHERE q.test_id = v_tid AND q.text = 'Хім: Символ заліза?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'Цукор'
    WHERE q.test_id = v_tid AND q.text = 'Хім: NaCl — це…';

    -- Механіка: базовий курс (10)
    SELECT id INTO v_tid FROM tests WHERE title = 'Механіка: базовий курс' LIMIT 1;
    v_wrong := ARRAY['Мех: Потужність P = …', 'Мех: Щільність ρ = …'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 8, 10, 80, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '18 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'm × v'
    WHERE q.test_id = v_tid AND q.text = 'Мех: Потужність P = …';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'V / m'
    WHERE q.test_id = v_tid AND q.text = 'Мех: Щільність ρ = …';

    -- Електрика експрес (2)
    SELECT id INTO v_tid FROM tests WHERE title = 'Електрика експрес' LIMIT 1;
    v_wrong := ARRAY['Ел: Закон Ома: U = …'];
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000006;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 1, 2, 50, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '4 minutes')
    RETURNING id INTO v_sid;
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, o.is_correct FROM questions q
    JOIN options o ON o.question_id = q.id AND o.is_correct WHERE q.test_id = v_tid AND NOT (q.text = ANY (v_wrong));
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, q.id, o.id, false FROM questions q
    JOIN options o ON o.question_id = q.id AND o.text = 'I / R'
    WHERE q.test_id = v_tid AND q.text = 'Ел: Закон Ома: U = …';

END $seed$;


-- Multiple-choice tests: explicit sessions (не single-choice цикл)
DO $seed_mc$
DECLARE
    v_uid BIGINT;
    v_sid BIGINT;
    v_tid BIGINT;
    v_qid BIGINT;
BEGIN
    -- Алгебра: кілька правильних — Олена 100% (усі 3 питання)
    SELECT id INTO v_tid FROM tests WHERE title = 'Алгебра: кілька правильних' LIMIT 1;
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000001;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 3, 100, NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days' + INTERVAL '10 minutes')
    RETURNING id INTO v_sid;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Позначте парні числа';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Скільки буде 7 × 8?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Позначте прості числа';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct;

    -- Алгебра — Іван 67% (2/3)
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000002;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 2, 3, 67, NOW() - INTERVAL '11 days', NOW() - INTERVAL '11 days' + INTERVAL '9 minutes')
    RETURNING id INTO v_sid;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Позначте парні числа';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.text = '2';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, false FROM options o WHERE o.question_id = v_qid AND o.text = '5';
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Скільки буде 7 × 8?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Алгебра: Позначте прості числа';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct;

    -- Клітина (приватний) — Марія: MC + single
    SELECT id INTO v_tid FROM tests WHERE title = 'Клітина (приватний)' LIMIT 1;
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000003;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 3, 4, 75, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '15 minutes')
    RETURNING id INTO v_sid;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Основна енергетична станція клітини?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: ДНК знаходиться в…';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Органели рослинної клітини';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Скільки хромосом у людини?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, false FROM options o WHERE o.question_id = v_qid AND o.text = '23';

    -- Клітина — Андрій 100%
    SELECT id INTO v_uid FROM users WHERE telegram_id = 900000004;
    INSERT INTO test_sessions (test_id, student_id, score, total_questions, percentage, started_at, completed_at)
    VALUES (v_tid, v_uid, 4, 4, 100, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '14 minutes')
    RETURNING id INTO v_sid;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Основна енергетична станція клітини?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: ДНК знаходиться в…';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Органели рослинної клітини';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct;
    SELECT id INTO v_qid FROM questions WHERE test_id = v_tid AND text = 'Біо: Скільки хромосом у людини?';
    INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
    SELECT v_sid, v_qid, o.id, true FROM options o WHERE o.question_id = v_qid AND o.is_correct LIMIT 1;
END $seed_mc$;


-- ============================================================
--  30 completed attempts for telegram_id 6056542025
-- ============================================================

DELETE FROM session_answers
WHERE session_id IN (
    SELECT ts.id
    FROM test_sessions ts
    JOIN users u ON u.id = ts.student_id
    WHERE u.telegram_id = 6056542025
);

DELETE FROM test_sessions
WHERE student_id IN (SELECT id FROM users WHERE telegram_id = 6056542025);

/*
INSERT INTO users (telegram_id, name, role, language)
VALUES (6056542025, 'Тестовий студент', 'student', 'uk')
ON CONFLICT (telegram_id) DO UPDATE SET
    role = EXCLUDED.role,
    language = EXCLUDED.language;
*/

DO $seed_6056542025$
DECLARE
    v_uid BIGINT;
    v_sid BIGINT;
    v_tid BIGINT;
    v_total INT;
    v_wrong INT;
    v_pct REAL;
    r RECORD;
BEGIN
    SELECT id INTO v_uid FROM users WHERE telegram_id = 6056542025;

    FOR r IN
        SELECT * FROM (VALUES
            ('Столиці світу', 4, 40),
            ('Столиці світу', 3, 38),
            ('Столиці світу', 4, 35),
            ('Столиці світу', 2, 32),
            ('Історія України', 4, 39),
            ('Історія України', 3, 36),
            ('Історія України', 4, 30),
            ('Планети Сонячної системи', 4, 37),
            ('Планети Сонячної системи', 3, 33),
            ('English Grammar Basics', 4, 35),
            ('English Grammar Basics', 3, 32),
            ('English Grammar Basics', 2, 28),
            ('Grundlagen der deutschen Sprache', 4, 34),
            ('Grundlagen der deutschen Sprache', 3, 30),
            ('Історія України (розширена)', 4, 33),
            ('Історія України (розширена)', 3, 29),
            ('Історія України (розширена)', 2, 25),
            ('Базова математика', 5, 40),
            ('Базова математика', 4, 36),
            ('Базова математика', 5, 32),
            ('Базова математика', 3, 27),
            ('Українська література', 3, 31),
            ('Українська література', 2, 28),
            ('Українська література', 3, 24),
            ('Основи біології', 4, 30),
            ('Основи біології', 3, 26),
            ('Основи хімії', 3, 29),
            ('Основи хімії', 2, 23),
            ('Основи фізики', 4, 28),
            ('Основи фізики', 3, 22),
            ('Клімат та біоми', 2, 20),
            ('Європейські річки (приватний)', 2, 19),
            ('Швидкий квіз: арифметика', 2, 18),
            ('Друга світова війна', 5, 17),
            ('Сонячна система (розширено)', 7, 16),
            ('Phrasal verbs B1', 3, 15),
            ('Deutsche Farben und Formen', 3, 14),
            ('Українські письменники XX ст.', 6, 13),
            ('Реакції та розчини', 5, 12),
            ('Механіка: базовий курс', 9, 11),
            ('Електрика експрес', 2, 10),
            ('Гетьманщина XVII ст.', 3, 9)
        ) AS attempts(test_title, score, days_ago)
    LOOP
        SELECT id INTO v_tid FROM tests WHERE title = r.test_title LIMIT 1;
        IF v_tid IS NULL THEN
            RAISE NOTICE 'Test not found: %', r.test_title;
            CONTINUE;
        END IF;

        SELECT COUNT(*)::INT INTO v_total FROM questions WHERE test_id = v_tid;
        IF v_total = 0 THEN
            CONTINUE;
        END IF;

        v_wrong := GREATEST(0, LEAST(v_total, v_total - r.score));
        v_pct := ROUND((r.score::REAL / v_total) * 100);

        INSERT INTO test_sessions (
            test_id, student_id, score, total_questions, percentage,
            started_at, completed_at
        )
        VALUES (
            v_tid, v_uid, r.score, v_total, v_pct,
            NOW() - (r.days_ago || ' days')::INTERVAL,
            NOW() - (r.days_ago || ' days')::INTERVAL + INTERVAL '8 minutes'
        )
        RETURNING id INTO v_sid;

        IF v_wrong > 0 THEN
            INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
            SELECT v_sid, q.id, o.id, false
            FROM (
                SELECT q2.id, q2.question_order
                FROM questions q2
                WHERE q2.test_id = v_tid
                ORDER BY q2.question_order
                LIMIT v_wrong
            ) wq
            JOIN questions q ON q.id = wq.id
            JOIN LATERAL (
                SELECT opt.id
                FROM options opt
                WHERE opt.question_id = q.id AND NOT opt.is_correct
                LIMIT 1
            ) o ON true;
        END IF;

        INSERT INTO session_answers (session_id, question_id, option_id, is_correct)
        SELECT v_sid, q.id, o.id, true
        FROM questions q
        JOIN options o ON o.question_id = q.id AND o.is_correct
        WHERE q.test_id = v_tid
          AND q.question_order >= v_wrong;
    END LOOP;
END $seed_6056542025$;

-- Scoring scale backfill (see init_database.sql — SCORING SCALE section)
UPDATE tests t
SET max_points = sub.cnt
FROM (
    SELECT test_id, COUNT(*)::REAL AS cnt
    FROM questions
    GROUP BY test_id
) sub
WHERE t.id = sub.test_id AND t.max_points IS NULL;

UPDATE test_sessions ts
SET max_points = COALESCE(
    (SELECT t.max_points FROM tests t WHERE t.id = ts.test_id),
    ts.total_questions::REAL
)
WHERE ts.max_points IS NULL AND ts.completed_at IS NOT NULL;
