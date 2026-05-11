-- Sample tests for Quiz Bot. Run after creating at least one teacher.
-- Gets teacher_id dynamically from the first teacher in the database.

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
