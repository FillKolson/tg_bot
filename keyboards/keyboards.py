from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

from .callbacks import (
    RoleCallback, SubjectCallback, TestCallback,
    VisibilityCallback, OptionCallback, QuestionNextCallback,
    DoneOptionsCallback, BackCallback, NewSubjectCallback,
)


# ── Role selection ──────────────────────────────────────────────────────────

def role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🎓 Студент / Учень",
                             callback_data=RoleCallback(value="student").pack()),
        InlineKeyboardButton(text="👨‍🏫 Вчитель",
                             callback_data=RoleCallback(value="teacher").pack()),
    ]])


# ── Main menus (Reply) ──────────────────────────────────────────────────────

def teacher_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Створити тест")],
            [KeyboardButton(text="📋 Мої тести"), KeyboardButton(text="📊 Результати")],
        ],
        resize_keyboard=True,
    )


def student_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Предмети")],
            [KeyboardButton(text="🔑 Ввести код"), KeyboardButton(text="📈 Мої результати")],
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ── Subject list ────────────────────────────────────────────────────────────

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


# ── Test list (student browsing) ────────────────────────────────────────────

def tests_keyboard(tests: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"📝 {t['title']}",
            callback_data=TestCallback(id=t["id"], action="start").pack()
        )]
        for t in tests
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Назад до предметів",
                                      callback_data=BackCallback(to="subjects").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Teacher: my tests ───────────────────────────────────────────────────────

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
                text="🗑",
                callback_data=TestCallback(id=t["id"], action="delete").pack()
            ),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Visibility choice ───────────────────────────────────────────────────────

def visibility_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🌐 Публічний",
                             callback_data=VisibilityCallback(value="public").pack()),
        InlineKeyboardButton(text="🔒 Приватний",
                             callback_data=VisibilityCallback(value="private").pack()),
    ]])


# ── Options input during question creation ──────────────────────────────────

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


# ── Correct option selection ────────────────────────────────────────────────

def correct_option_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{i + 1}. {text}",
            callback_data=OptionCallback(index=i).pack()
        )]
        for i, text in enumerate(options)
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── After saving a question ─────────────────────────────────────────────────

def question_next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Додати ще питання",
                             callback_data=QuestionNextCallback(action="add").pack()),
        InlineKeyboardButton(text="✅ Завершити тест",
                             callback_data=QuestionNextCallback(action="finish").pack()),
    ]])


# ── Answer options during test ──────────────────────────────────────────────

def answer_keyboard(question_id: int, options: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=opt["text"],
            callback_data=f"ans:{question_id}:{opt['id']}"
        )]
        for opt in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Confirm test start ──────────────────────────────────────────────────────

def start_test_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="▶️ Розпочати тест",
                             callback_data=TestCallback(id=test_id, action="start").pack()),
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=BackCallback(to="subjects").pack()),
    ]])
