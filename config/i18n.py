"""
Internationalization system for the bot.
Usage: i18n(key, lang='uk', **kwargs)
"""

# Ukrainian translations
UK = {
    # Auth
    "welcome": "👋 *Вітаємо в боті для тестування знань!*\n\nБудь ласка, оберіть вашу роль:",
    "role_student": "🎓 Студент / Учень",
    "role_teacher": "👨‍🏫 Вчитель",
    "role_selected": "Ви обрали роль: *{role}*\n\nТепер введіть ваше повне ім'я (воно буде відображатися в строчці автора тесту):",
    "name_too_short": "⚠️ Ім'я занадто коротке. Введіть щонайменше 2 символи:",
    "name_too_long": "⚠️ Ім'я занадто довге. Введіть не більше 64 символів:",
    "registration_complete": "✅ *Реєстрацію завершено!*\n\nІм'я: *{name}*\nРоль: *{role}*\n\n{tip}",
    "teacher_tip": "Натисніть *➕ Створити тест*, щоб розпочати роботу.\nВведіть /help для перегляду можливостей.",
    "student_tip": "Натисніть *📚 Предмети*, щоб знайти тест,\nабо *🔑 Ввести код*, якщо маєте код приватного тесту.",
    "language_select": "🌐 *Виберіть мову / Select language:*",
    "lang_uk": "🇺🇦 Українська",
    "lang_en": "🇬🇧 English",
    
    # Welcome back
    "welcome_back": "👋 З поверненням, *{name}*!\nРоль: _{role}_",
    
    # Help
    "help_teacher": "📖 *Довідка для вчителя*\n\n➕ *Створити тест* — запуск майстра створення тесту\n📋 *Мої тести та результати* — перегляд тестів та результатів студентів\n\nПри створенні тесту можна обрати:\n• *Публічний* — студенти знайдуть через меню «Предмети»\n• *Приватний* — доступний лише за унікальним кодом\n• *Обмежені спроби* — контроль кількості повторних проходжень\n\n/cancel — скасувати поточну дію",
    "help_student": "📖 *Довідка для студента*\n\n📚 *Предмети* — перегляд публічних тестів по предметах\n🔑 *Ввести код* — доступ до приватного тесту за кодом\n📈 *Мої результати* — ваша статистика\n\n/cancel — скасувати поточну дію",
    
    # Teacher: Create test
    "create_test_wizard": "📝 *Майстер створення тесту*\n\n*Крок 1/6* — Введіть назву тесту:\n\n_/cancel — скасувати_",
    "title_confirmed": "✅ Назва: *{title}*\n\n*Крок 2/6* — Оберіть предмет або створіть новий:",
    "no_subjects": "✅ Назва: *{title}*\n\n*Крок 2/6* — Предметів ще немає. Введіть назву нового предмету:",
    "subject_confirmed": "✅ Предмет: *{subject}*\n\n*Крок 3/6* — Введіть короткий опис тесту\n_(або надішліть /skip, щоб пропустити)_",
    "new_subject_prompt": "📖 Введіть назву нового предмету:",
    "subject_created": "✅ Предмет *«{name}»* створено!\n\n*Крок 3/6* — Введіть короткий опис тесту\n_(або /skip для пропуску)_",
    "subject_too_short": "⚠️ Занадто коротка назва. Спробуйте ще раз:",
    "description_confirmed": "✅ Опис: _{description}_\n\n*Крок 4/6* — Чи показувати студентам правильність відповідей?",
    "description_skipped": "⏭ Опис пропущено.\n\n*Крок 4/6* — Чи показувати студентам правильність відповідей?",
    "visibility_public": "🌐 Публічний",
    "visibility_private": "🔒 Приватний",
    "show_answers_yes": "✅ Показувати",
    "show_answers_no": "❌ Приховувати",
    "answers_visibility_confirmed": "✅ Правильність відповідей: {visibility}\n\n*Крок 5/6* — Можливість повторного проходження тесту:",
    "attempts_unlimited": "♾️ Необмежено",
    "attempts_limited": "⏱️ Обмежити спроби",
    "attempts_unlimited_confirmed": "✅ Студенти можуть повторно проходити цей тест необмежену кількість разів.\n\n*Крок 6/6* — Тип доступу:",
    "attempts_limited_prompt": "Скільки спроб дозволити студентам?",
    "attempts_limit_confirmed": "✅ Максимум спроб: *{attempts}*\n\n*Крок 6/6* — Тип доступу:",
    "visibility_step_prompt": "*Крок 6/6* — Тип доступу:",
    "attempts_btn_1": "1️⃣ 1 спроба",
    "attempts_btn_2": "2️⃣ 2 спроби",
    "attempts_btn_3": "3️⃣ 3 спроби",
    "attempts_btn_5": "5️⃣ 5 спроб",
    "attempts_btn_10": "🔟 10 спроб",
    "new_subject": "➕ Новий предмет",
    "back": "⬅️ Назад",
    "visibility_note_public": "🌐 Тест буде публічним — студенти знайдуть його в меню.",
    "visibility_note_private": "🔒 Тест буде приватним.\nКод доступу: `{code}`\n_(поділіться ним зі студентами)_",
    "add_questions_prompt": "✏️ *Тепер додайте питання.*\n\nВведіть текст *першого питання*:",
    "enter_question_text": "✏️ Введіть текст *питання {num}*:",
    
    # Question creation
    "question_too_short": "⚠️ Текст питання занадто короткий:",
    "question_confirmed": "❓ Питання: *{text}*\n\nВведіть *варіант відповіді 1* (максимум {max}):",
    "option_empty": "⚠️ Варіант не може бути порожнім:",
    "options_list": "📋 Варіанти:\n{options}",
    "options_max_reached": "📋 Варіанти:\n{options}\n\n*Максимум варіантів досягнуто.*\n🎯 Оберіть *правильну відповідь*:",
    "option_prompt": "➕ Введіть варіант {num}",
    "option_prompt_or_done": "➕ Введіть варіант {num} (або натисніть «Готово», якщо варіантів достатньо):",
    "done_options": "✅ Варіанти додано, обрати правильний",
    "min_options_error": "⚠️ Потрібно щонайменше 2 варіанти!",
    "mark_correct": "🎯 Оберіть *правильну відповідь*:",
    
    # Question saved
    "question_saved": "✅ *Питання {num} збережено!*\nПравильна відповідь: _{correct}_\n\nЩо далі?",
    "add_more_questions": "➕ Додати ще питання",
    "finish_test": "✅ Завершити тест",
    "saved_notification": "Збережено!",
    "cancelled": "❌ Скасовано.",
    "not_author": "⛔ Ви не є автором цього тесту.",
    "no_tests_in_subject_teacher": "Немає тестів у цьому предметі",
    "error_test_not_found": "⚠️ Помилка: тест не знайдено.",
    "error_generic": "⚠️ Помилка.",
    
    # Test finish
    "no_questions_error": "⚠️ Додайте хоча б одне питання!",
    "test_created": "🎉 *Тест успішно створено!*\n\n📝 Назва: *{title}*\n📖 Предмет: *{subject}*\n❓ Питань: *{count}*\n{access_line}{public_note}",
    "back_to_menu": "Повернення до меню:",
    
    # My tests
    "my_tests": "📋 *Ваші тести* ({count}):\n\nНатисніть назву — переглянути результати.\n🗑 — видалити тест.",
    "no_tests": "📭 У вас ще немає жодного тесту.\nСтворіть перший через *➕ Створити тест*.",
    "test_deleted": "🗑 Тест видалено.",
    "delete_error": "⚠️ Помилка видалення.",
    "no_tests_left": "📭 Тестів більше немає.",
    
    # Results
    "results_menu": "📊 *Оберіть тест для перегляду результатів:*",
    "no_results": "📊 *{title}*\n\nЖоден студент ще не проходив цей тест.",
    "results_title": "📊 *Результати: {title}*\n",
    "results_line": "{num}. *{name}*\n   {bar} {pct}% ({score}/{total})\n",
    "results_list": "📈 *Ваші результати* ({count} тестів):\n",
    "no_results_student": "📭 Ви ще не проходили жодного тесту.",
    
    # Student: Browse
    "no_public_tests": "😔 Публічних предметів ще немає.\nСпробуйте ввести код приватного тесту через 🔑.",
    "select_subject": "📚 *Оберіть предмет:*",
    "tests_in_subject": "📖 *{subject}* — тести ({count}):",
    "no_tests_in_subject": "😔 У цьому предметі ще немає публічних тестів.",
    "back_to_subjects": "⬅️ Назад до предметів",
    
    # Private test
    "enter_code_prompt": "🔑 Введіть код доступу до приватного тесту:\n\n_/cancel — скасувати_",
    "code_not_found": "❌ Тест із таким кодом не знайдено. Перевірте код та спробуйте ще раз:",
    "test_found": "✅ Знайдено тест:\n\n📝 *{title}*\n📖 Предмет: {subject}\n👨‍🏫 Вчитель: {teacher}\n❓ Питань: {count}\n{description}",
    "test_found_description": "📄 {description}\n",
    "start_test": "▶️ Розпочати тест",
    "test_preview": "📝 *{title}*\n👨‍🏫 Вчитель: {teacher}\n❓ Питань: {count}\n{attempts}{description}{confirm}",
    "test_preview_description": "📄 {description}\n",
    "test_start_confirm": "Натисніть *▶️ Розпочати тест*, коли будете готові.",
    
    # Taking test
    "test_no_questions": "⚠️ У цьому тесті немає питань.",
    "test_started": "🚀 *{title}* розпочато!\n❓ Всього питань: {count}\n\nВідповідайте на питання нижче:",
    "question_counter": "*Питання {current} / {total}*",
    "correct_answer": "✅ *Правильно!*",
    "wrong_answer": "❌ *Неправильно.*\nПравильна відповідь: _{correct}_",
    "answer_hidden": "❌ *Неправильно!*",
    "answer_saved": "✅ Відповідь збережено",
    "test_finished": "🏁 *Тест завершено!*\n\n📊 Результат: *{score} / {total}* ({pct}%)\n{bar}\n{grade}\n\nПовернення до меню:",
    "grade_excellent": "🏆 Відмінно! Бездоганний результат!",
    "grade_good": "🥇 Добре! Ви добре знаєте матеріал.",
    "grade_satisfactory": "🥈 Задовільно. Є що покращити.",
    "grade_weak": "🥉 Слабо. Варто повторити тему.",
    "grade_poor": "📚 Потрібно більше вчитись.",

    # Search
    "search_title": "🔍 *Пошук тестів*\n\nОберіть як шукати:",
    "search_by_name_prompt": "🔍 Введіть назву тесту для пошуку:",
    "search_query_too_short": "⚠️ Запит занадто короткий (мін. 2 символи):",
    "search_not_found": "😔 Тестів з назвою *{query}* не знайдено.",
    "search_results": "🔍 *Результати пошуку за \"{query}\"* ({count}):",
    "no_subjects_yet": "😔 Предметів ще немає.",
    "no_teachers_yet": "😔 Вчителів ще немає.",
    "select_teacher": "👨‍🏫 *Оберіть вчителя:*",
    "no_tests_for_teacher": "😔 У вчителя {name} ще немає публічних тестів.",
    "teacher_tests_title": "👨‍🏫 *Тести вчителя {name}* ({count}):",
    "student_menu_title": "📚 *Меню студента*",

    # Attempts info
    "attempts_left": "⏱️ Спроб залишилось: {remaining}/{max}",
    "attempts_exhausted": "❌ Спроби вичерпані ({max}/{max})",
    "attempts_unlimited_info": "♾️ Спроби: необмежено",
    "attempts_all_used_alert": "❌ Ви вичерпали всі спроби ({attempts}) для цього тесту.",
    
    # Menu items
    "menu_create_test": "➕ Створити тест",
    "menu_my_tests": "📋 Мої тести",
    "menu_results": "📊 Результати",
    "menu_statistics": "📊 Статистика",
    "menu_subjects": "📚 Предмети",
    "menu_enter_code": "🔑 Ввести код",
    "menu_my_results": "📈 Мої результати",
    "menu_search": "🔍 Пошук",
    "menu_profile": "👤 Профіль",
    
    # Profile
    "profile_title": "👤 *Ваш профіль*\n\n📝 *Ім'я:* {name}\n🌐 *Мова:* {language}\n",
    "profile_change_language": "🌐 Змінити мову",
    "profile_change_name": "📝 Змінити ім'я",
    "profile_name_prompt": "Введіть нове ім'я (2-64 символи):",
    "profile_name_changed": "✅ Ім'я змінено на *{name}*",
    "profile_language_changed": "✅ Мова змінена на _{language}_",
    
    # Timer for tests
    "time_limit_prompt": "⏱️ Введіть обмеження часу для тесту в хвилинах (ціле число), або надішліть /skip для відсутності обмеження:",
    "time_limit_invalid": "⚠️ Невірний формат. Введіть число хвилин або /skip:",
    "time_limit_set": "✅ Обмеження часу встановлено: {minutes} хв.",
    "time_up": "⏰ Час закінчився! Тест завершено.",
    
    # Errors and validation
    "title_too_short": "⚠️ Назва занадто коротка (мін. 3 символи):",
    "title_too_short_subject": "⚠️ Занадто коротка назва. Спробуйте ще раз:",
    "question_too_short": "⚠️ Текст питання занадто короткий:",
    "option_empty": "⚠️ Варіант не може бути порожнім:",
    "min_options": "⚠️ Потрібно щонайменше 2 варіанти!",
    "max_options_reached": "Максимум варіантів досягнуто.",
    "option_number": "➕ Введіть варіант {num}",
    "option_or_done": "(або натисніть «Готово», якщо варіантів достатньо)",
    "enter_option_first": "Введіть *варіант відповіді 1* (максимум {max}):",
    "options_list_title": "Варіанти:",
    
    # Teacher-only
    "teacher_only": "⛔ Ця функція доступна лише для вчителів.",
    "student_only": "⛔ Ця функція доступна лише для студентів.",
    "not_registered": "Використайте /start для реєстрації.",
    "cancel_no_action": "Немає активних дій для скасування.",
    "cancel_confirmed": "❌ Дію скасовано.",
    "test_not_found": "⚠️ Тест не знайдено.",
    "answer_error": "⚠️ Помилка вибору. Спробуйте ще раз.",
}

# English translations
EN = {
    # Auth
    "welcome": "👋 *Welcome to the Quiz Bot!*\n\nPlease select your role:",
    "role_student": "🎓 Student",
    "role_teacher": "👨‍🏫 Teacher",
    "role_selected": "You selected role: *{role}*\n\nNow enter your full name (It will be added to the lines of the author of the test):",
    "name_too_short": "⚠️ Name is too short. Enter at least 2 characters:",
    "name_too_long": "⚠️ Name is too long. Enter no more than 64 characters:",
    "registration_complete": "✅ *Registration complete!*\n\nName: *{name}*\nRole: *{role}*\n\n{tip}",
    "teacher_tip": "Click *➕ Create Test* to start.\nType /help for features.",
    "student_tip": "Click *📚 Subjects* to find a test,\nor *🔑 Enter Code* if you have a private test code.",
    "language_select": "🌐 *Select your language / Виберіть мову:*",
    "lang_uk": "🇺🇦 Українська",
    "lang_en": "🇬🇧 English",
    
    # Welcome back
    "welcome_back": "👋 Welcome back, *{name}*!\nRole: _{role}_",
    
    # Help
    "help_teacher": "📖 *Teacher Help*\n\n➕ *Create Test* — start test creation wizard\n📋 *My Tests & Results* — view your tests and student results\n\nWhen creating a test, you can choose:\n• *Public* — students will find it in the Subjects menu\n• *Private* — only accessible via unique code\n• *Limited Attempts* — control how many times students can retake\n\n/cancel — cancel current action",
    "help_student": "📖 *Student Help*\n\n📚 *Subjects* — browse public tests by subject\n🔑 *Enter Code* — access private test via code\n📈 *My Results* — your statistics\n\n/cancel — cancel current action",
    
    # Teacher: Create test
    "create_test_wizard": "📝 *Test Creation Wizard*\n\n*Step 1/6* — Enter test name:\n\n_/cancel — cancel_",
    "title_confirmed": "✅ Name: *{title}*\n\n*Step 2/6* — Select subject or create new:",
    "no_subjects": "✅ Name: *{title}*\n\n*Step 2/6* — No subjects yet. Enter new subject name:",
    "subject_confirmed": "✅ Subject: *{subject}*\n\n*Step 3/6* — Enter short test description\n_(or /skip to skip)_",
    "new_subject_prompt": "📖 Enter subject name:",
    "subject_created": "✅ Subject *«{name}»* created!\n\n*Step 3/6* — Enter test description\n_(or /skip to skip)_",
    "subject_too_short": "⚠️ Name too short. Try again:",
    "description_confirmed": "✅ Description: _{description}_\n\n*Step 4/6* — Show answer correctness to students?",
    "description_skipped": "⏭ Description skipped.\n\n*Step 4/6* — Show answer correctness to students?",
    "visibility_public": "🌐 Public",
    "visibility_private": "🔒 Private",
    "show_answers_yes": "✅ Show",
    "show_answers_no": "❌ Hide",
    "answers_visibility_confirmed": "✅ Show answers: {visibility}\n\n*Step 5/6* — Retake attempts:",
    "attempts_unlimited": "♾️ Unlimited",
    "attempts_limited": "⏱️ Limit attempts",
    "attempts_unlimited_confirmed": "✅ Students can retake this test unlimited times.\n\n*Step 6/6* — Access type:",
    "attempts_limited_prompt": "How many attempts to allow?",
    "attempts_limit_confirmed": "✅ Max attempts: *{attempts}*\n\n*Step 6/6* — Access type:",
    "visibility_step_prompt": "*Step 6/6* — Access type:",
    "attempts_btn_1": "1️⃣ 1 attempt",
    "attempts_btn_2": "2️⃣ 2 attempts",
    "attempts_btn_3": "3️⃣ 3 attempts",
    "attempts_btn_5": "5️⃣ 5 attempts",
    "attempts_btn_10": "🔟 10 attempts",
    "new_subject": "➕ New subject",
    "back": "⬅️ Back",
    "visibility_note_public": "🌐 Test will be public — students will find it in the menu.",
    "visibility_note_private": "🔒 Test will be private.\nAccess code: `{code}`\n_(share it with students)_",
    "add_questions_prompt": "✏️ *Now add questions.*\n\nEnter *first question* text:",
    "enter_question_text": "✏️ Enter *question {num}* text:",
    
    # Question creation
    "question_too_short": "⚠️ Question text too short:",
    "question_confirmed": "❓ Question: *{text}*\n\nEnter *answer option 1* (max {max}):",
    "option_empty": "⚠️ Option cannot be empty:",
    "options_list": "📋 Options:\n{options}",
    "options_max_reached": "📋 Options:\n{options}\n\n*Maximum options reached.*\n🎯 Select *correct answer*:",
    "option_prompt": "➕ Enter option {num}",
    "option_prompt_or_done": "➕ Enter option {num} (or click Done if enough):",
    "done_options": "✅ Options added, select correct one",
    "min_options_error": "⚠️ Need at least 2 options!",
    "mark_correct": "🎯 Select *correct answer*:",
    
    # Question saved
    "question_saved": "✅ *Question {num} saved!*\nCorrect answer: _{correct}_\n\nWhat next?",
    "add_more_questions": "➕ Add another question",
    "finish_test": "✅ Finish test",
    "saved_notification": "Saved!",
    "cancelled": "❌ Cancelled.",
    "not_author": "⛔ You are not the author of this test.",
    "no_tests_in_subject_teacher": "No tests in this subject",
    "error_test_not_found": "⚠️ Error: test not found.",
    "error_generic": "⚠️ Error.",
    
    # Test finish
    "no_questions_error": "⚠️ Add at least one question!",
    "test_created": "🎉 *Test created successfully!*\n\n📝 Name: *{title}*\n📖 Subject: *{subject}*\n❓ Questions: *{count}*\n{access_line}{public_note}",
    "back_to_menu": "Back to menu:",
    
    # My tests
    "my_tests": "📋 *Your Tests* ({count}):\n\nClick name to view results.\n🗑 — delete test.",
    "no_tests": "📭 You don't have any tests yet.\nCreate your first via *➕ Create Test*.",
    "test_deleted": "🗑 Test deleted.",
    "delete_error": "⚠️ Deletion error.",
    "no_tests_left": "📭 No tests left.",
    
    # Results
    "results_menu": "📊 *Select test to view results:*",
    "no_results": "📊 *{title}*\n\nNo student has taken this test yet.",
    "results_title": "📊 *Results: {title}*\n",
    "results_line": "{num}. *{name}*\n   {bar} {pct}% ({score}/{total})\n",
    "results_list": "📈 *Your Results* ({count} tests):\n",
    "no_results_student": "📭 You haven't taken any tests yet.",
    
    # Student: Browse
    "no_public_tests": "😔 No public subjects yet.\nTry entering a private test code via 🔑.",
    "select_subject": "📚 *Select subject:*",
    "tests_in_subject": "📖 *{subject}* — tests ({count}):",
    "no_tests_in_subject": "😔 No public tests in this subject.",
    "back_to_subjects": "⬅️ Back to subjects",
    
    # Private test
    "enter_code_prompt": "🔑 Enter private test access code:\n\n_/cancel — cancel_",
    "code_not_found": "❌ Test with this code not found. Check and try again:",
    "test_found": "✅ Test found:\n\n📝 *{title}*\n📖 Subject: {subject}\n👨‍🏫 Teacher: {teacher}\n❓ Questions: {count}\n{description}",
    "test_found_description": "📄 {description}\n",
    "start_test": "▶️ Start Test",
    "test_preview": "📝 *{title}*\n👨‍🏫 Teacher: {teacher}\n❓ Questions: {count}\n{attempts}{description}{confirm}",
    "test_preview_description": "📄 {description}\n",
    "test_start_confirm": "Click *▶️ Start Test* when ready.",
    
    # Taking test
    "test_no_questions": "⚠️ This test has no questions.",
    "test_started": "🚀 *{title}* started!\n❓ Total questions: {count}\n\nAnswer the questions below:",
    "question_counter": "*Question {current} / {total}*",
    "correct_answer": "✅ *Correct!*",
    "wrong_answer": "❌ *Wrong.*\nCorrect answer: _{correct}_",
    "answer_hidden": "❌ *Wrong!*",
    "answer_saved": "✅ Answer saved",
    "test_finished": "🏁 *Test finished!*\n\n📊 Result: *{score} / {total}* ({pct}%)\n{bar}\n{grade}\n\nBack to menu:",
    "grade_excellent": "🏆 Excellent! Perfect score!",
    "grade_good": "🥇 Good! You know the material well.",
    "grade_satisfactory": "🥈 Satisfactory. Room to improve.",
    "grade_weak": "🥉 Weak. Review the topic.",
    "grade_poor": "📚 Need to study more.",

    # Search
    "search_title": "🔍 *Test search*\n\nChoose how to search:",
    "search_by_name_prompt": "🔍 Enter test name to search:",
    "search_query_too_short": "⚠️ Query too short (min 2 characters):",
    "search_not_found": "😔 No tests found with name *{query}*.",
    "search_results": "🔍 *Search results for \"{query}\"* ({count}):",
    "no_subjects_yet": "😔 No subjects yet.",
    "no_teachers_yet": "😔 No teachers yet.",
    "select_teacher": "👨‍🏫 *Select teacher:*",
    "no_tests_for_teacher": "😔 Teacher {name} has no public tests yet.",
    "teacher_tests_title": "👨‍🏫 *Teacher {name} tests* ({count}):",
    "student_menu_title": "📚 *Student menu*",

    # Attempts info
    "attempts_left": "⏱️ Attempts left: {remaining}/{max}",
    "attempts_exhausted": "❌ Attempts exhausted ({max}/{max})",
    "attempts_unlimited_info": "♾️ Attempts: unlimited",
    "attempts_all_used_alert": "❌ You have used all attempts ({attempts}) for this test.",
    
    # Menu items
    "menu_create_test": "➕ Create Test",
    "menu_my_tests": "📋 My Tests",
    "menu_results": "📊 Results",
    "menu_statistics": "📊 Statistics",
    "menu_subjects": "📚 Subjects",
    "menu_enter_code": "🔑 Enter Code",
    "menu_my_results": "📈 My Results",
    "menu_search": "🔍 Search",
    "menu_profile": "👤 Profile",
    
    # Profile
    "profile_title": "👤 *Your Profile*\n\n📝 *Name:* {name}\n🌐 *Language:* {language}\n",
    "profile_change_language": "🌐 Change Language",
    "profile_change_name": "📝 Change Name",
    "profile_name_prompt": "Enter new name (2-64 characters):",
    "profile_name_changed": "✅ Name changed to *{name}*",
    "profile_language_changed": "✅ Language changed to _{language}_",
    
    # Timer for tests
    "time_limit_prompt": "⏱️ Enter a time limit for the test in minutes (integer), or send /skip for no limit:",
    "time_limit_invalid": "⚠️ Invalid format. Enter number of minutes or /skip:",
    "time_limit_set": "✅ Time limit set: {minutes} minutes.",
    "time_up": "⏰ Time's up! Test finished.",
    
    # Errors and validation
    "title_too_short": "⚠️ Name too short (minimum 3 characters):",
    "title_too_short_subject": "⚠️ Name too short. Try again:",
    "question_too_short": "⚠️ Question text too short:",
    "option_empty": "⚠️ Option cannot be empty:",
    "min_options": "⚠️ Need at least 2 options!",
    "max_options_reached": "Maximum options reached.",
    "option_number": "➕ Enter option {num}",
    "option_or_done": "(or click Done if enough):",
    "enter_option_first": "Enter *answer option 1* (max {max}):",
    "options_list_title": "Options:",
    
    # Teacher-only
    "teacher_only": "⛔ This feature is only for teachers.",
    "student_only": "⛔ This feature is only for students.",
    "not_registered": "Use /start to register.",
    "cancel_no_action": "No active actions to cancel.",
    "cancel_confirmed": "❌ Action cancelled.",
    "test_not_found": "⚠️ Test not found.",
    "answer_error": "⚠️ Selection error. Try again.",
}

# Language to dictionary mapping
LANGUAGES = {
    "uk": UK,
    "en": EN,
}


def i18n(key: str, lang: str = "uk", **kwargs) -> str:
    """
    Get translated string by key.
    
    Args:
        key: Translation key (e.g. "welcome", "test_finished")
        lang: Language code ('uk' or 'en')
        **kwargs: Format arguments (e.g. name="John", score=95)
    
    Returns:
        Translated and formatted string
    """
    if lang not in LANGUAGES:
        lang = "uk"
    
    dictionary = LANGUAGES[lang]
    text = dictionary.get(key, f"[{key}]")
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError as e:
            return f"{text}\n[Missing: {e}]"
    
    return text
