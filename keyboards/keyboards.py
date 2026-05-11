from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

from config.i18n import i18n

from .callbacks import (
    RoleCallback, LangCallback, SubjectCallback, TestCallback,
    VisibilityCallback, OptionCallback, QuestionNextCallback,
    DoneOptionsCallback, BackCallback, NewSubjectCallback,
    AnswerVisibilityCallback, AttemptsCallback, LimitedAttemptsCallback,
    EditTestCallback, EditQuestionCallback, EditOptionCallback,
    SearchCallback, TeacherFilterCallback, StatisticsCallback, ConfirmDeleteCallback,
)


# Role selection

def role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🎓 Студент / Учень",
                             callback_data=RoleCallback(value="student").pack()),
        InlineKeyboardButton(text="👨‍🏫 Вчитель",
                             callback_data=RoleCallback(value="teacher").pack()),
    ]])

# Language selection

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇦 Українська",
                             callback_data=LangCallback(value="uk").pack()),
        InlineKeyboardButton(text="🇬🇧 English",
                             callback_data=LangCallback(value="en").pack()),
    ]])

# Main menus (Reply)

def teacher_menu(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("menu_create_test", lang))],
            [KeyboardButton(text=i18n("menu_my_tests", lang))],
            [KeyboardButton(text="📊 Статистика")],
        ],
        resize_keyboard=True,
    )


def student_menu(lang: str = "uk") -> ReplyKeyboardMarkup:
    from config.i18n import i18n
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("menu_subjects", lang))],
            [KeyboardButton(text=i18n("menu_enter_code", lang)), KeyboardButton(text=i18n("menu_my_results", lang))],
            [KeyboardButton(text="🔍 Пошук")],
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# Subject list

def subjects_keyboard(subjects: list[dict], for_teacher: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📖 {s['name']}",
                              callback_data=SubjectCallback(id=s["id"]).pack())]
        for s in subjects
    ]
    if for_teacher:
        rows.append([InlineKeyboardButton(text="➕ Новий предмет",
                                          callback_data=NewSubjectCallback().pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Test list (student browsing)

def tests_keyboard(tests: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"📝 {t['title']}",
            callback_data=TestCallback(id=t["id"], action="preview").pack()
        )]
        for t in tests
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Назад до предметів",
                                      callback_data=BackCallback(to="subjects").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Teacher: my tests

def my_tests_keyboard(tests: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for t in tests:
        badge = "🌐" if t["is_public"] else "🔒"
        rows.append([
            InlineKeyboardButton(
                text=f"{badge} {t['title']}",
                callback_data=TestCallback(id=t["id"], action="results").pack()
            ),
            InlineKeyboardButton(
                text="✏️",
                callback_data=EditTestCallback(id=t["id"], action="menu").pack()
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=TestCallback(id=t["id"], action="delete").pack()
            ),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Visibility choice

def visibility_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🌐 Публічний",
                             callback_data=VisibilityCallback(value="public").pack()),
        InlineKeyboardButton(text="🔒 Приватний",
                             callback_data=VisibilityCallback(value="private").pack()),
    ], [
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

# Answer visibility choice

def answer_visibility_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Показувати",
                             callback_data=AnswerVisibilityCallback(value="yes").pack()),
        InlineKeyboardButton(text="❌ Приховувати",
                             callback_data=AnswerVisibilityCallback(value="no").pack()),
    ]])

# Attempts choice

def attempts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="♾️ Необмежено",
                             callback_data=AttemptsCallback(value="unlimited").pack()),
        InlineKeyboardButton(text="⏱️ Обмежити спроби",
                             callback_data=AttemptsCallback(value="limited").pack()),
    ], [
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

def limited_attempts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="1️⃣ 1 спроба",
                             callback_data=LimitedAttemptsCallback(count=1).pack()),
        InlineKeyboardButton(text="2️⃣ 2 спроби",
                             callback_data=LimitedAttemptsCallback(count=2).pack()),
        InlineKeyboardButton(text="3️⃣ 3 спроби",
                             callback_data=LimitedAttemptsCallback(count=3).pack()),
    ], [
        InlineKeyboardButton(text="5️⃣ 5 спроб",
                             callback_data=LimitedAttemptsCallback(count=5).pack()),
        InlineKeyboardButton(text="🔟 10 спроб",
                             callback_data=LimitedAttemptsCallback(count=10).pack()),
    ], [
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

# Options input during question creation

def options_input_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    """Shows current options + 'Done' button (enabled when >= 2 options)."""
    rows = []
    for i, text in enumerate(options, start=1):
        rows.append([InlineKeyboardButton(text=f"  {i}. {text}", callback_data="noop")])

    if len(options) >= 2:
        rows.append([InlineKeyboardButton(
            text="✅ Варіанти додано, обрати правильний",
            callback_data=DoneOptionsCallback().pack()
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Correct option selection

def correct_option_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{i + 1}. {text}",
            callback_data=OptionCallback(index=i).pack()
        )]
        for i, text in enumerate(options)
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# After saving a question

def question_next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Додати ще питання",
                             callback_data=QuestionNextCallback(action="add").pack()),
        InlineKeyboardButton(text="✅ Завершити тест",
                             callback_data=QuestionNextCallback(action="finish").pack()),
    ]])


# Answer options during test

def answer_keyboard(question_id: int, options: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=opt["text"],
            callback_data=f"ans:{question_id}:{opt['id']}"
        )]
        for opt in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Confirm test start

def start_test_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="▶️ Розпочати тест",
                             callback_data=TestCallback(id=test_id, action="start").pack()),
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="subjects").pack()),
    ]])


# Edit test

def edit_test_menu_keyboard(test_id: int) -> InlineKeyboardMarkup:
    """Menu to choose what to edit: title, description, visibility, attempts, questions."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Назва тесту",
                              callback_data=EditTestCallback(id=test_id, action="title").pack())],
        [InlineKeyboardButton(text="📄 Опис",
                              callback_data=EditTestCallback(id=test_id, action="desc").pack())],
        [InlineKeyboardButton(text="🔍 Видимість (публічний/приватний)",
                              callback_data=EditTestCallback(id=test_id, action="vis").pack())],
        [InlineKeyboardButton(text="⏱️ Кількість спроб",
                              callback_data=EditTestCallback(id=test_id, action="attempts").pack())],
        [InlineKeyboardButton(text="❓ Редагувати питання",
                              callback_data=EditTestCallback(id=test_id, action="questions").pack())],
        [InlineKeyboardButton(text="⬅️ Назад",
                              callback_data=BackCallback(to="teacher_menu").pack())],
    ])


def edit_questions_list_keyboard(test_id: int, questions: list[dict]) -> InlineKeyboardMarkup:
    """List of questions with edit/delete options."""
    rows = []
    for q in questions:
        rows.append([
            InlineKeyboardButton(
                text=f"❓ {q['text'][:30]}..." if len(q['text']) > 30 else f"❓ {q['text']}",
                callback_data=EditQuestionCallback(id=q["id"], action="edit").pack()
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=EditQuestionCallback(id=q["id"], action="delete").pack()
            ),
        ])
    rows.append([InlineKeyboardButton(text="⬅️ Назад",
                                     callback_data=EditTestCallback(id=test_id, action="menu").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def edit_options_list_keyboard(question_id: int, options: list[dict]) -> InlineKeyboardMarkup:
    """List of options with edit/delete and mark correct."""
    rows = []
    for opt in options:
        correct_mark = "✅" if opt["is_correct"] else "⭕"
        rows.append([
            InlineKeyboardButton(
                text=f"{correct_mark} {opt['text'][:25]}...",
                callback_data=EditOptionCallback(id=opt["id"], action="edit").pack()
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=EditOptionCallback(id=opt["id"], action="delete").pack()
            ),
        ])
    rows.append([InlineKeyboardButton(text="⬅️ Назад",
                                     callback_data=EditQuestionCallback(id=question_id, action="edit").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Search tests

def search_menu_keyboard() -> InlineKeyboardMarkup:
    """Search options for students."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 По назві",
                             callback_data=SearchCallback(action="by_name").pack()),
        InlineKeyboardButton(text="📖 По предмету",
                             callback_data=SearchCallback(action="by_subject").pack())],
        [InlineKeyboardButton(text="👨‍🏫 По авторові",
                             callback_data=SearchCallback(action="by_teacher").pack())],
        [InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="student_menu").pack())],
    ])


def teachers_list_keyboard(teachers: list[dict]) -> InlineKeyboardMarkup:
    """List of teachers for filter."""
    rows = [
        [InlineKeyboardButton(text=f"👨‍🏫 {t['name']}",
                              callback_data=TeacherFilterCallback(id=t["id"]).pack())]
        for t in teachers
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Назад",
                                     callback_data=BackCallback(to="search").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Back button

def back_keyboard(to: str) -> InlineKeyboardMarkup:
    """Generic back button."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to=to).pack()),
    ]])


# Statistics

def statistics_keyboard() -> InlineKeyboardMarkup:
    """Button to view statistics."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📊 Переглянути статистику",
                             callback_data=StatisticsCallback(action="view").pack()),
    ]])


# Delete confirmation

def confirm_delete_keyboard(test_id: int) -> InlineKeyboardMarkup:
    """Confirm deletion of a test."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Так, видалити",
                             callback_data=ConfirmDeleteCallback(action="yes").pack()),
        InlineKeyboardButton(text="❌ Скасувати",
                             callback_data=ConfirmDeleteCallback(action="no").pack()),
    ]])

