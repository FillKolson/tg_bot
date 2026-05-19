import random

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
    TeacherTestsSubjectCallback,
)


# Role selection

def role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("role_student", "uk"),
                             callback_data=RoleCallback(value="student").pack()),
        InlineKeyboardButton(text=i18n("role_teacher", "uk"),
                             callback_data=RoleCallback(value="teacher").pack()),
    ]])

# Language selection

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("lang_uk", "uk"),
                             callback_data=LangCallback(value="uk").pack()),
        InlineKeyboardButton(text=i18n("lang_en", "uk"),
                             callback_data=LangCallback(value="en").pack()),
    ]])

# Main menus (Reply)

def teacher_menu(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("menu_create_test", lang))],
            [KeyboardButton(text=i18n("menu_my_tests", lang))],
            [KeyboardButton(text=i18n("menu_statistics", lang))],
        ],
        resize_keyboard=True,
    )


def student_menu(lang: str = "uk") -> ReplyKeyboardMarkup:
    from config.i18n import i18n
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("menu_subjects", lang))],
            [KeyboardButton(text=i18n("menu_enter_code", lang)), KeyboardButton(text=i18n("menu_my_results", lang))],
            [KeyboardButton(text=i18n("menu_search", lang))],
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# Subject list

def subjects_keyboard(subjects: list[dict], for_teacher: bool = False, lang: str = "uk") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📖 {s['name']}",
                              callback_data=SubjectCallback(id=s["id"]).pack())]
        for s in subjects
    ]
    if for_teacher:
        rows.append([InlineKeyboardButton(text=i18n("new_subject", lang),
                                          callback_data=NewSubjectCallback().pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subject_tests_list_keyboard(tests: list[dict]) -> InlineKeyboardMarkup:
    """Inline keyboard with one full-width button per test (for a selected subject)."""
    rows = []
    for t in tests:
        badge = "🌐" if t.get("is_public") else "🔒"
        rows.append([
            InlineKeyboardButton(
                text=f"{badge} {t.get('title', '—')}",
                callback_data=TestCallback(id=t.get("id"), action="open").pack(),
            )
        ])
    # Back button to subjects
    rows.append([
        InlineKeyboardButton(
            text="⬅️ До предметів",
            callback_data=BackCallback(to="teacher_tests").pack(),
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Test list (student browsing)

def tests_keyboard(tests: list[dict], lang: str = "uk") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"📝 {t['title']}",
            callback_data=TestCallback(id=t["id"], action="preview").pack()
        )]
        for t in tests
    ]
    rows.append([InlineKeyboardButton(text=i18n("back_to_subjects", lang),
                                      callback_data=BackCallback(to="subjects").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Teacher: my tests (grouped by subject)



def my_tests_subjects_keyboard(tests: list[dict]) -> InlineKeyboardMarkup:
    subject_counts: dict[int, dict[str, object]] = {}
    for test in tests:
        subject_id = test.get("subject_id") or 0
        subject_name = test.get("subjects", {}).get("name", "Без предмету")
        if subject_id not in subject_counts:
            subject_counts[subject_id] = {"name": subject_name, "count": 0}
        subject_counts[subject_id]["count"] += 1

    rows = [
        [InlineKeyboardButton(
            text=f"📖 {info['name']} ({info['count']})",
            callback_data=SubjectCallback(id=subject_id).pack(),
        )]
        for subject_id, info in sorted(subject_counts.items(), key=lambda item: item[1]["name"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Visibility choice

def visibility_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("visibility_public", lang),
                             callback_data=VisibilityCallback(value="public").pack()),
        InlineKeyboardButton(text=i18n("visibility_private", lang),
                             callback_data=VisibilityCallback(value="private").pack()),
    ], [
        InlineKeyboardButton(text=i18n("back", lang),
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

# Answer visibility choice

def answer_visibility_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("show_answers_yes", lang),
                             callback_data=AnswerVisibilityCallback(value="yes").pack()),
        InlineKeyboardButton(text=i18n("show_answers_no", lang),
                             callback_data=AnswerVisibilityCallback(value="no").pack()),
    ]])

# Attempts choice

def attempts_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("attempts_unlimited", lang),
                             callback_data=AttemptsCallback(value="unlimited").pack()),
        InlineKeyboardButton(text=i18n("attempts_limited", lang),
                             callback_data=AttemptsCallback(value="limited").pack()),
    ], [
        InlineKeyboardButton(text=i18n("back", lang),
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

def limited_attempts_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("attempts_btn_1", lang),
                             callback_data=LimitedAttemptsCallback(count=1).pack()),
        InlineKeyboardButton(text=i18n("attempts_btn_2", lang),
                             callback_data=LimitedAttemptsCallback(count=2).pack()),
        InlineKeyboardButton(text=i18n("attempts_btn_3", lang),
                             callback_data=LimitedAttemptsCallback(count=3).pack()),
    ], [
        InlineKeyboardButton(text=i18n("attempts_btn_5", lang),
                             callback_data=LimitedAttemptsCallback(count=5).pack()),
        InlineKeyboardButton(text=i18n("attempts_btn_10", lang),
                             callback_data=LimitedAttemptsCallback(count=10).pack()),
    ], [
        InlineKeyboardButton(text=i18n("back", lang),
                             callback_data=BackCallback(to="edit_menu").pack()),
    ]])

# Options input during question creation

def options_input_keyboard(options: list[str], lang: str = "uk") -> InlineKeyboardMarkup:
    """Shows current options + 'Done' button (enabled when >= 2 options)."""
    rows = []
    for i, text in enumerate(options, start=1):
        rows.append([InlineKeyboardButton(text=f"  {i}. {text}", callback_data="noop")])

    if len(options) >= 2:
        rows.append([InlineKeyboardButton(
            text=i18n("done_options", lang),
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

def question_next_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("add_more_questions", lang),
                             callback_data=QuestionNextCallback(action="add").pack()),
        InlineKeyboardButton(text=i18n("finish_test", lang),
                             callback_data=QuestionNextCallback(action="finish").pack()),
    ]])


# Answer options during test

def answer_keyboard(question_id: int, options: list[dict]) -> InlineKeyboardMarkup:
    shuffled_options = random.sample(options, k=len(options))
    rows = [
        [InlineKeyboardButton(
            text=opt["text"],
            callback_data=f"ans:{question_id}:{opt['id']}"
        )]
        for opt in shuffled_options
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Confirm test start

def start_test_keyboard(test_id: int, lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=i18n("start_test", lang),
                             callback_data=TestCallback(id=test_id, action="start").pack()),
        InlineKeyboardButton(text=i18n("back", lang),
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

def search_menu_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    """Search options for students."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 " + ("By name" if lang == "en" else "По назві"),
                             callback_data=SearchCallback(action="by_name").pack()),
        InlineKeyboardButton(text="📖 " + ("By subject" if lang == "en" else "По предмету"),
                             callback_data=SearchCallback(action="by_subject").pack())],
        [InlineKeyboardButton(text="👨‍🏫 " + ("By teacher" if lang == "en" else "По авторові"),
                             callback_data=SearchCallback(action="by_teacher").pack())],
        [InlineKeyboardButton(text=i18n("back", lang),
                             callback_data=BackCallback(to="student_menu").pack())],
    ])


def teachers_list_keyboard(teachers: list[dict], lang: str = "uk") -> InlineKeyboardMarkup:
    """List of teachers for filter."""
    rows = [
        [InlineKeyboardButton(text=f"👨‍🏫 {t['name']}",
                              callback_data=TeacherFilterCallback(id=t["id"]).pack())]
        for t in teachers
    ]
    rows.append([InlineKeyboardButton(text=i18n("back", lang),
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

