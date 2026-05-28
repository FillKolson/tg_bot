"""
Teacher handlers - create tests, manage questions, view results.
"""
import logging
import random
import string
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from db import queries
from config.i18n import i18n
from keyboards.callbacks import (
    SubjectCallback, VisibilityCallback, OptionCallback,
    QuestionNextCallback, DoneOptionsCallback, NewSubjectCallback,
    TestCallback, BackCallback, AnswerVisibilityCallback,
    AttemptsCallback, LimitedAttemptsCallback,
    EditTestCallback, EditQuestionCallback, EditOptionCallback,
    StatisticsCallback, ConfirmDeleteCallback,
)
from keyboards.keyboards import (
    teacher_menu, subjects_keyboard, visibility_keyboard,
    options_input_keyboard, correct_option_keyboard,
    question_next_keyboard, my_tests_subjects_keyboard,
    subject_tests_list_keyboard,
    answer_visibility_keyboard, attempts_keyboard, limited_attempts_keyboard,
    edit_test_menu_keyboard, edit_questions_list_keyboard, edit_options_list_keyboard,
    question_edit_menu_keyboard, statistics_keyboard, confirm_delete_keyboard, back_keyboard,
)
from states.states import TeacherStates

logger = logging.getLogger(__name__)
router = Router()

MAX_OPTIONS = 4  # per question


# Auth check - reject non-teachers

async def _require_teacher(message_or_cq) -> Optional[dict]:
    tid = (
        message_or_cq.from_user.id
        if isinstance(message_or_cq, (Message, CallbackQuery))
        else None
    )
    user = await queries.get_user(tid)
    if not user or user["role"] != "teacher":
        lang = user.get("language", "uk") if user else "uk"
        text = i18n("teacher_only", lang)
        if isinstance(message_or_cq, CallbackQuery):
            await message_or_cq.answer(text, show_alert=True)
        else:
            await message_or_cq.answer(text)
        return None
    return user


# Helpers

def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _question_summary(data: dict) -> str:
    qs = data.get("questions", [])
    cq = data.get("current_question", {})
    total = len(qs) + (1 if cq else 0)
    return f"Питань збережено: {len(qs)}"


def _rating_for_average(avg: float) -> str:
    if avg >= 90:
        return "✅ Високий рівень знань"
    if avg >= 75:
        return "👍 Добре"
    if avg >= 60:
        return "⚠️ Потрібно покращити"
    return "📌 Є над чим працювати"


def _format_subject_statistics(stats: list[dict]) -> str:
    total_subjects = len(stats)
    total_tests = sum(s["test_count"] for s in stats)
    total_sessions = sum(s["total_sessions"] for s in stats)
    weighted_avg = (
        round(
            sum(s["average_score"] * s["total_sessions"] for s in stats) / total_sessions,
            1,
        )
        if total_sessions else 0
    )

    lines = ["📊 *Статистика по предметах*", ""]
    for stat in stats:
        avg_text = f"{stat['average_score']}%" if stat["total_sessions"] else "—"
        summary = (
            _rating_for_average(stat["average_score"])
            if stat["total_sessions"] else "📌 Ще немає проходжень"
        )
        lines.extend([
            f"*{stat['subject_name']}*",
            f"   • Тестів: {stat['test_count']}",
            f"   • Проходжень: {stat['total_sessions']}",
            f"   • Середній бал: {avg_text}",
            f"   {summary}",
            "",
        ])

    overall_average = f"{weighted_avg}%" if total_sessions else "—"
    lines.extend([
        "🧾 *Усього*",
        f"   • Предметів: {total_subjects}",
        f"   • Тестів: {total_tests}",
        f"   • Проходжень: {total_sessions}",
        f"   • Середній бал: {overall_average}",
    ])
    return "\n".join(lines)


# Step 1 - Enter title

@router.message(F.text.in_(["➕ Створити тест", "➕ Create Test"]))
async def create_test_start(message: Message, state: FSMContext) -> None:
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    await state.set_state(TeacherStates.entering_title)
    lang = user.get("language", "uk")
    await message.answer(
        i18n("create_test_wizard", lang),
        parse_mode="Markdown",
    )


@router.message(TeacherStates.entering_title, F.text)
async def enter_title(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    title = message.text.strip()
    if len(title) < 3:
        await message.answer(i18n("title_too_short", lang))
        return
    await state.update_data(title=title, questions=[])

    subjects = await queries.get_subjects()
    await state.set_state(TeacherStates.selecting_subject)

    if subjects:
        await message.answer(
            i18n("title_confirmed", lang, title=title),
            reply_markup=subjects_keyboard(subjects, for_teacher=True, lang=lang),
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            i18n("no_subjects", lang, title=title),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.creating_subject)


# Step 2 - Select or create subject

@router.callback_query(TeacherStates.selecting_subject, SubjectCallback.filter())
async def select_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subject = await queries.get_subject(callback_data.id)
    await state.update_data(subject_id=callback_data.id, subject_name=subject["name"])
    await callback.message.edit_text(
        i18n("subject_confirmed", lang, subject=subject["name"]),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_description)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_subject, NewSubjectCallback.filter())
async def new_subject_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await callback.message.edit_text(i18n("new_subject_prompt", lang))
    await state.set_state(TeacherStates.creating_subject)
    await callback.answer()


@router.message(TeacherStates.creating_subject, F.text)
async def create_new_subject(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    name = message.text.strip()
    if len(name) < 2:
        await message.answer(i18n("title_too_short_subject", lang))
        return
    subject = await queries.create_subject(name)
    await state.update_data(subject_id=subject["id"], subject_name=subject["name"])
    await message.answer(
        i18n("subject_created", lang, name=name),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_description)


# Step 3 - Description

@router.message(TeacherStates.entering_description, F.text)
async def enter_description(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    desc: Optional[str] = None
    if message.text.strip().lower() != "/skip":
        desc = message.text.strip()

    await state.update_data(description=desc)
    if desc:
        text = i18n("description_confirmed", lang, description=desc)
    else:
        text = i18n("description_skipped", lang)
    await message.answer(
        text,
        reply_markup=answer_visibility_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_answer_visibility)


# Step 4 - Answer visibility

@router.callback_query(TeacherStates.choosing_answer_visibility, AnswerVisibilityCallback.filter())
async def choose_answer_visibility(callback: CallbackQuery, callback_data: AnswerVisibilityCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    show_answers = callback_data.value == "yes"
    await state.update_data(show_answer_correctness=show_answers)
    
    visibility_text = i18n("show_answers_yes", lang) if show_answers else i18n("show_answers_no", lang)
    await callback.message.edit_text(
        i18n("answers_visibility_confirmed", lang, visibility=visibility_text),
        reply_markup=attempts_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_attempts)
    await callback.answer()


# Step 5 - Attempts configuration

@router.callback_query(TeacherStates.choosing_attempts, AttemptsCallback.filter())
async def choose_attempts(callback: CallbackQuery, callback_data: AttemptsCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    if callback_data.value == "unlimited":
        await state.update_data(max_attempts=None)
        await callback.message.edit_text(
            i18n("attempts_unlimited_confirmed", lang),
            reply_markup=visibility_keyboard(lang),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.choosing_visibility)
    else:
        await callback.message.edit_text(
            i18n("attempts_limited_prompt", lang),
            reply_markup=limited_attempts_keyboard(lang),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.choosing_limited_attempts)
    await callback.answer()


@router.callback_query(TeacherStates.choosing_limited_attempts, LimitedAttemptsCallback.filter())
async def choose_limited_attempts(callback: CallbackQuery, callback_data: LimitedAttemptsCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    max_att = callback_data.count
    await state.update_data(max_attempts=max_att)
    
    attempts_text = "1 спроба" if max_att == 1 else f"{max_att} спроб"
    await callback.message.edit_text(
        i18n("attempts_limit_confirmed", lang, attempts=attempts_text),
        reply_markup=visibility_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_visibility)
    await callback.answer()


# Step 6 - Visibility

@router.callback_query(TeacherStates.choosing_visibility, VisibilityCallback.filter())
async def choose_visibility(callback: CallbackQuery, callback_data: VisibilityCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    is_public = callback_data.value == "public"
    access_code = None if is_public else _generate_code()
    await state.update_data(is_public=is_public, access_code=access_code)

    if is_public:
        note = i18n("visibility_note_public", lang)
    else:
        note = i18n("visibility_note_private", lang, code=access_code)

    await callback.message.edit_text(
        f"{note}\n\n"
        + i18n("add_questions_prompt", lang),
        parse_mode="Markdown",
    )
    # Ask for optional time limit before adding questions
    await callback.message.edit_text(i18n("time_limit_prompt", lang), parse_mode="Markdown")
    await state.set_state(TeacherStates.choosing_time_limit)
    await callback.answer()



@router.message(TeacherStates.choosing_time_limit, F.text)
async def choose_time_limit(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    text = message.text.strip()
    if text.lower() == "/skip":
        await state.update_data(time_limit_minutes=None)
        await message.answer(i18n("add_questions_prompt", lang), parse_mode="Markdown")
        await state.set_state(TeacherStates.entering_question_text)
        return

    try:
        minutes = int(text)
        if minutes <= 0:
            raise ValueError()
    except Exception:
        await message.answer(i18n("time_limit_invalid", lang))
        return

    await state.update_data(time_limit_minutes=minutes)
    await message.answer(i18n("time_limit_set", lang, minutes=minutes), parse_mode="Markdown")
    await message.answer(i18n("add_questions_prompt", lang), parse_mode="Markdown")
    await state.set_state(TeacherStates.entering_question_text)


# Questions loop - question text

@router.message(TeacherStates.entering_question_text, F.text)
async def enter_question_text(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    q_text = message.text.strip()
    if len(q_text) < 3:
        await message.answer(i18n("question_too_short", lang))
        return
    await state.update_data(current_question={"text": q_text, "options": []})
    await message.answer(
        i18n("question_confirmed", lang, text=q_text, max=MAX_OPTIONS),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_option)


# Questions loop - collecting options

@router.message(TeacherStates.entering_option, F.text)
async def enter_option(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    cq = data.get("current_question", {})
    opts: list[str] = cq.get("options", [])

    opt_text = message.text.strip()
    if not opt_text:
        await message.answer(i18n("option_empty", lang))
        return

    opts.append(opt_text)
    cq["options"] = opts
    await state.update_data(current_question=cq)

    n = len(opts)

    if n >= MAX_OPTIONS:
        # Auto-proceed to marking correct
        await message.answer(
            i18n("options_max_reached", lang, options=_options_list(opts).replace("📋 Варіанти:\n", "")),
            reply_markup=correct_option_keyboard(opts),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.marking_correct)
    else:
        await message.answer(
            _options_list(opts)
            + "\n\n"
            + i18n("option_prompt_or_done", lang, num=n + 1),
            reply_markup=options_input_keyboard(opts, lang),
            parse_mode="Markdown",
        )


@router.callback_query(TeacherStates.entering_option, DoneOptionsCallback.filter())
async def done_options(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    opts = data["current_question"]["options"]
    if len(opts) < 2:
        await callback.answer(i18n("min_options", lang), show_alert=True)
        return
    await callback.message.edit_text(
        _options_list(opts) + "\n\n🎯 Оберіть *правильну відповідь*:",
        reply_markup=correct_option_keyboard(opts),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.marking_correct)
    await callback.answer()


# Questions loop - mark correct answer

@router.callback_query(TeacherStates.marking_correct, OptionCallback.filter())
async def mark_correct(callback: CallbackQuery, callback_data: OptionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    cq = data["current_question"]
    opts = cq["options"]
    correct_idx = callback_data.index

    # Build option dicts
    option_dicts = [
        {"text": text, "is_correct": (i == correct_idx)}
        for i, text in enumerate(opts)
    ]
    cq["options"] = option_dicts

    # Append to questions list
    questions: list = data.get("questions", [])
    questions.append(cq)
    await state.update_data(questions=questions, current_question=None)

    correct_text = opts[correct_idx]
    q_num = len(questions)

    await callback.message.edit_text(
        i18n("question_saved", lang, num=q_num, correct=correct_text),
        reply_markup=question_next_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer(i18n("saved_notification", lang))


# Questions loop - continue or finish

@router.callback_query(TeacherStates.marking_correct, QuestionNextCallback.filter())
@router.callback_query(QuestionNextCallback.filter())
async def question_next(callback: CallbackQuery, callback_data: QuestionNextCallback, state: FSMContext) -> None:
    if callback_data.action == "add":
        user = await queries.get_user(callback.from_user.id)
        lang = user.get("language", "uk") if user else "uk"
        data = await state.get_data()
        n = len(data.get("questions", []))
        await callback.message.edit_text(
            i18n("enter_question_text", lang, num=n + 1),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.entering_question_text)
        await callback.answer()
    else:
        await _finish_test(callback, state)


async def _finish_test(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("questions", [])
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    if not questions:
        await callback.answer(i18n("no_questions_error", lang), show_alert=True)
        return

    # Save test to DB
    test = await queries.create_test(
        title=data["title"],
        subject_id=data["subject_id"],
        teacher_id=(await queries.get_user(callback.from_user.id))["id"],
        is_public=data["is_public"],
        access_code=data.get("access_code"),
        description=data.get("description"),
        show_answer_correctness=data.get("show_answer_correctness", True),
        max_attempts=data.get("max_attempts"),
        time_limit_minutes=data.get("time_limit_minutes"),
    )
    await queries.bulk_insert_questions_options(test["id"], questions)
    await state.clear()

    code_line = ""
    if not data["is_public"]:
        code_line = f"🔑 Код доступу: `{data['access_code']}`\n"

    attempts_info = ""
    if data.get("max_attempts"):
        attempts_text = "1 спроба" if data["max_attempts"] == 1 else f"{data['max_attempts']} спроб"
        attempts_info = f"⏱️ Спроб: *{attempts_text}*\n"
    else:
        attempts_info = "♾️ Спроби: *Необмежено*\n"

    time_limit_line = ""
    if data.get("time_limit_minutes") is not None:
        time_limit_line = f"⏱️ Ліміт часу: *{data['time_limit_minutes']} хв.*\n"

    await callback.message.edit_text(
        i18n(
            "test_created",
            lang,
            title=data["title"],
            subject=data["subject_name"],
            count=len(questions),
            access_line=("🌐 Публічний\n" if data["is_public"] else "🔒 Приватний\n") + attempts_info + time_limit_line + code_line,
            public_note="",
        ),
        parse_mode="Markdown",
    )
    await callback.message.answer(i18n("back_to_menu", lang), reply_markup=teacher_menu(lang))
    await callback.answer()


# Tests and Results

@router.message(F.text.in_([
    "📋 Мої тести",
    "📊 Результати",
    "📋 Мої тести та результати",
    "📋 My Tests",
    "📊 Results",
    "📋 My Tests & Results",
]))
async def view_tests_and_results(message: Message, state: FSMContext) -> None:
    """Combined handler for both 'Мої тести' and 'Результати' buttons."""
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    tests = await queries.get_teacher_tests(user["id"], message.from_user.id)

    if not tests:
        await message.answer(
            "📭 У вас ще немає тестів.\n"
            "Створіть перший тест через *➕ Створити тест*.",
            parse_mode="Markdown"
        )
        return

    # Store tests in state for filtering later
    await state.update_data(all_tests=tests)
    
    await message.answer(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Оберіть предмет, щоб переглянути тести:",
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)



@router.message(F.text == "📊 Статистика")
async def view_statistics(message: Message, state: FSMContext) -> None:
    """Show subject statistics directly."""
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    
    stats = await queries.get_subject_statistics(user["id"])
    
    if not stats:
        await message.answer(
            "📊 *Статистика по предметах*\n\n"
            "У вас ще немає завершених тестів для статистики.",
            parse_mode="Markdown",
        )
        return
    
    text = _format_subject_statistics(stats)
    await message.answer(text, parse_mode="Markdown")


@router.callback_query(TeacherStates.viewing_tests_and_results, SubjectCallback.filter())
async def view_tests_by_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    """Show tests for a selected subject."""
    user = await _require_teacher(callback)
    if not user:
        return

    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    subject_tests = [t for t in tests if t.get("subject_id") == callback_data.id]
    if not subject_tests:
        await callback.answer("⚠️ Тести для цього предмету не знайдено.", show_alert=True)
        return

    subject_name = subject_tests[0].get("subjects", {}).get("name", "—")
    keyboard = subject_tests_list_keyboard(subject_tests)

    await callback.message.edit_text(
        f"📋 *Тести з предмету* {subject_name} ({len(subject_tests)}):\n\n"
        "Натисніть назву — відкрити меню дій для тесту.",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)
    await callback.answer()


@router.callback_query(TeacherStates.viewing_tests_and_results, BackCallback.filter(F.to == "teacher_tests"))
async def back_to_test_subjects(callback: CallbackQuery, state: FSMContext) -> None:
    user = await _require_teacher(callback)
    if not user:
        return

    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    await callback.message.edit_text(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Оберіть предмет, щоб переглянути тести:",
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)
    await callback.answer()


@router.callback_query(TeacherStates.viewing_statistics, StatisticsCallback.filter())
async def show_statistics(callback: CallbackQuery, callback_data: StatisticsCallback, state: FSMContext) -> None:
    """Display subject statistics."""
    user = await queries.get_user(callback.from_user.id)
    stats = await queries.get_subject_statistics(user["id"])
    
    if not stats:
        await callback.message.edit_text(
            "📊 *Статистика по предметах*\n\n"
            "У вас ще немає завершених тестів для статистики.",
            reply_markup=back_keyboard("teacher_menu"),
            parse_mode="Markdown",
        )
        await callback.answer()
        return
    
    text = _format_subject_statistics(stats)
    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard("teacher_menu"),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(TeacherStates.viewing_statistics, BackCallback.filter())
async def back_from_statistics(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to teacher menu from statistics."""
    await callback.message.edit_text(
        "Оберіть дію:",
        reply_markup=teacher_menu(),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(TeacherStates.viewing_tests_and_results, TestCallback.filter())
async def handle_test_action(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    if callback_data.action == "results":
        await _show_results(callback, callback_data.id, state)
    elif callback_data.action == "delete":
        await _delete_test(callback, callback_data.id, state)
    elif callback_data.action == "open":
        # Show action menu for the selected test
        test = await queries.get_test(callback_data.id)
        if not test:
            await callback.answer("⚠️ Тест не знайдено.", show_alert=True)
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Переглянути результати", callback_data=TestCallback(id=callback_data.id, action="results").pack())],
            [InlineKeyboardButton(text="✏️ Редагувати", callback_data=EditTestCallback(id=callback_data.id, action="menu").pack())],
            [InlineKeyboardButton(text="🗑 Видалити", callback_data=TestCallback(id=callback_data.id, action="delete").pack())],
            [InlineKeyboardButton(text="⬅️ До списку предметів", callback_data=BackCallback(to="teacher_tests").pack())],
        ])
        await callback.message.edit_text(
            f"📝 *{test['title']}*\n\nОберіть дію:",
            reply_markup=kb,
            parse_mode="Markdown",
        )
    await callback.answer()


async def _show_results(callback: CallbackQuery, test_id: int, state: FSMContext) -> None:
    test = await queries.get_test(test_id)
    sessions = await queries.get_test_results(test_id, callback.from_user.id)

    if not sessions:
        await callback.message.edit_text(
            f"📊 *{test['title']}*\n\nЖоден студент ще не проходив цей тест.",
            parse_mode="Markdown",
        )
        return

    lines = [f"📊 *Результати: {test['title']}*\n"]
    for i, s in enumerate(sessions, 1):
        pct = round(s.get("percentage", 0))
        bar = _progress_bar(pct)
        name = s["users"]["name"] if s.get("users") else "—"
        lines.append(f"{i}. *{name}*\n   {bar} {pct}% ({s['score']}/{s['total_questions']})\n")

    await callback.message.edit_text("\n".join(lines), parse_mode="Markdown")


async def _delete_test(callback: CallbackQuery, test_id: int, state: FSMContext) -> None:
    """Show delete confirmation."""
    test = await queries.get_test(test_id)
    await callback.message.edit_text(
        f"🗑 *Видалення тесту*\n\n"
        f"Тест: *{test['title']}*\n"
        f"Предмет: {test['subjects']['name']}\n\n"
        f"⚠️ Цю дію неможливо скасувати. Всі результати будуть втрачені.\n\n"
        f"Видалити тест?",
        reply_markup=confirm_delete_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.update_data(deleting_test_id=test_id)
    await state.set_state(TeacherStates.confirming_delete_test)


@router.callback_query(TeacherStates.confirming_delete_test, ConfirmDeleteCallback.filter())
async def confirm_delete_action(callback: CallbackQuery, callback_data: ConfirmDeleteCallback, state: FSMContext) -> None:
    """Handle delete confirmation."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    test_id = data.get("deleting_test_id")
    
    if not test_id:
        await callback.answer(i18n("error_test_not_found", lang), show_alert=True)
        return
    
    if callback_data.action == "yes":
        user = await queries.get_user(callback.from_user.id)
        deleted = await queries.deactivate_test(test_id, user["id"])
        if deleted:
            user = await queries.get_user(callback.from_user.id)
            tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
            await state.update_data(all_tests=tests)
            await callback.message.edit_text(
                f"📋 *Ваші тести* ({len(tests)}):\n\n"
                "Оберіть предмет, щоб переглянути тести:",
                reply_markup=my_tests_subjects_keyboard(tests),
                parse_mode="Markdown",
            )
            await callback.answer(i18n("test_deleted", lang))
            await state.set_state(TeacherStates.viewing_tests_and_results)
        else:
            user = await queries.get_user(callback.from_user.id)
            tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
            await state.update_data(all_tests=tests)
            await callback.message.edit_text(
                f"📋 *Ваші тести* ({len(tests)}):\n\n"
                "Оберіть предмет, щоб переглянути тести:",
                reply_markup=my_tests_subjects_keyboard(tests),
                parse_mode="Markdown",
            )
            await callback.answer(i18n("delete_error", lang))
            await state.set_state(TeacherStates.viewing_tests_and_results)
    else:
        # Cancel deletion
        user = await queries.get_user(callback.from_user.id)
        tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
        await state.update_data(all_tests=tests)
        await callback.message.edit_text(
            f"📋 *Ваші тести* ({len(tests)}):\n\n"
            "Оберіть предмет, щоб переглянути тести:",
            reply_markup=my_tests_subjects_keyboard(tests),
            parse_mode="Markdown",
        )
        await callback.answer(i18n("cancelled", lang))
        await state.set_state(TeacherStates.viewing_tests_and_results)


@router.callback_query(TeacherStates.confirming_delete_test, BackCallback.filter())
async def back_from_delete_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to tests list from delete confirmation."""
    user = await queries.get_user(callback.from_user.id)
    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    await state.update_data(all_tests=tests)
    await callback.message.edit_text(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Оберіть предмет, щоб переглянути тести:",
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)
    await callback.answer()


# Helpers

def _group_teacher_tests_by_subject_text(tests: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for test in tests:
        subject = test.get("subjects", {}).get("name", "Без предмету")
        grouped.setdefault(subject, []).append(test)

    lines = [f"📋 *Ваші тести* ({len(tests)}):", ""]
    for subject in sorted(grouped):
        subject_tests = sorted(grouped[subject], key=lambda t: t.get("title", ""))
        lines.append(f"📖 *{subject}* — {len(subject_tests)} тест(ів)")
        for test in subject_tests:
            badge = "🌐" if test.get("is_public") else "🔒"
            lines.append(f"   {badge} *{test.get('title', '—')}*")
        lines.append("")

    lines.append("Натисніть назву — переглянути результати.")
    lines.append("🗑 — видалити тест.")
    return "\n".join(lines)

def _options_list(opts: list[str]) -> str:
    return "📋 Варіанти:\n" + "\n".join(f"  {i + 1}. {o}" for i, o in enumerate(opts))


def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)


async def _handle_delete_test_question(
    callback: CallbackQuery,
    callback_data: EditQuestionCallback,
    state: FSMContext,
    lang: str,
) -> None:
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    if not test_id:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)
        return

    test = await queries.get_test_with_questions(test_id)
    if not test:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)
        return

    if len(test.get("questions", [])) <= 1:
        await callback.answer(i18n("cannot_delete_last_question", lang), show_alert=True)
        return

    deleted = await queries.delete_question(callback_data.id)
    if not deleted:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)
        return

    test = await queries.get_test_with_questions(test_id)
    questions = test.get("questions", []) if test else []
    await callback.message.edit_text(
        f"❓ *Питання тесту: {test['title']}*\n\n"
        "Оберіть питання для редагування:",
        reply_markup=edit_questions_list_keyboard(test_id, questions),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_questions_menu)
    await callback.answer("✅ Питання видалено.")


# Edit test

@router.callback_query(EditTestCallback.filter(F.action == "menu"))
async def edit_test_menu(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Open edit test menu."""
    user = await _require_teacher(callback)
    if not user:
        return
    
    test = await queries.get_test(callback_data.id)
    if not test or test["teacher_id"] != user["id"]:
        await callback.answer("⛔ Ви не є автором цього тесту.", show_alert=True)
        return
    
    badge = "🌐" if test["is_public"] else "🔒"
    vis_text = "Публічний" if test["is_public"] else "Приватний"
    att_text = f"{test['max_attempts']} спроб" if test['max_attempts'] else "Необмежено"
    time_text = f"{test['time_limit_minutes']} хв." if test.get("time_limit_minutes") is not None else "Немає"
    
    await callback.message.edit_text(
        f"✏️ *Редагування тесту*\n\n"
        f"📝 Назва: *{test['title']}*\n"
        f"🔍 Видимість: {badge} {vis_text}\n"
        f"⏱️ Спроби: {att_text}\n"
        f"⏱️ Ліміт часу: {time_text}\n\n"
        "Оберіть що редагувати:",
        reply_markup=edit_test_menu_keyboard(callback_data.id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "title"))
async def edit_test_title_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new title."""
    test = await queries.get_test(callback_data.id)
    await callback.message.edit_text(
        f"✏️ Поточна назва: *{test['title']}*\n\n"
        "Введіть нову назву:",
        reply_markup=back_keyboard("edit_menu"),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_title)
    await callback.answer()


@router.message(TeacherStates.editing_test_title, F.text)
async def edit_test_title_save(message: Message, state: FSMContext) -> None:
    """Save new title."""
    new_title = message.text.strip()
    if len(new_title) < 3:
        await message.answer("⚠️ Назва занадто коротка (мін. 3 символи):")
        return
    
    data = await state.get_data()
    test_id = data["editing_test_id"]
    
    await queries.update_test(test_id, title=new_title)
    await message.answer(
        f"✅ Назву оновлено на *{new_title}*",
        parse_mode="Markdown",
    )
    
    # Return to edit test menu
    await message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "desc"))
async def edit_test_description_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new description."""
    test = await queries.get_test(callback_data.id)
    current_desc = test.get("description") or "_(немає)_"
    await callback.message.edit_text(
        f"📄 Поточний опис: {current_desc}\n\n"
        "Введіть новий опис (або /skip щоб пропустити):",
        reply_markup=back_keyboard("edit_menu"),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_description)
    await callback.answer()


@router.message(TeacherStates.editing_test_description, F.text)
async def edit_test_description_save(message: Message, state: FSMContext) -> None:
    """Save new description."""
    new_desc = None if message.text.strip().lower() == "/skip" else message.text.strip()
    
    data = await state.get_data()
    test_id = data["editing_test_id"]
    
    await queries.update_test(test_id, description=new_desc)
    await message.answer(
        f"✅ Опис оновлено.",
        parse_mode="Markdown",
    )
    
    # Return to edit test menu
    await message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "vis"))
async def edit_test_visibility_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new visibility."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    test = await queries.get_test(callback_data.id)
    vis_text = "Публічний" if test["is_public"] else f"Приватний (код: {test['access_code']})"
    
    await callback.message.edit_text(
        f"🔍 Поточна видимість: {vis_text}\n\n"
        "Оберіть нову видимість:",
        reply_markup=visibility_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_visibility)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_visibility, VisibilityCallback.filter())
async def edit_test_visibility_save(callback: CallbackQuery, callback_data: VisibilityCallback, state: FSMContext) -> None:
    """Save new visibility."""
    is_public = callback_data.value == "public"
    access_code = None if is_public else _generate_code()
    
    data = await state.get_data()
    test_id = data["editing_test_id"]
    
    await queries.update_test(test_id, is_public=is_public, access_code=access_code)
    
    note = "Тест тепер *публічний*." if is_public else f"Тест тепер *приватний*.\nНовий код: `{access_code}`"
    await callback.message.edit_text(
        f"✅ {note}",
        parse_mode="Markdown",
    )
    await callback.answer("Збережено!")
    
    # Return to edit test menu
    await callback.message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "attempts"))
async def edit_test_attempts_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new attempts limit."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    test = await queries.get_test(callback_data.id)
    att_text = f"{test['max_attempts']} спроб" if test['max_attempts'] else "Необмежено"
    
    await callback.message.edit_text(
        f"⏱️ Поточне обмеження: {att_text}\n\n"
        "Оберіть нове:",
        reply_markup=attempts_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_attempts)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "time"))
async def edit_test_time_limit_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for the test time limit."""
    test = await queries.get_test(callback_data.id)
    current_limit = f"{test['time_limit_minutes']} хв." if test.get("time_limit_minutes") is not None else "Немає"
    await callback.message.edit_text(
        f"⏱️ Поточний ліміт часу: {current_limit}\n\n"
        "Введіть новий ліміт часу в хвилинах або надішліть /skip, щоб вимкнути обмеження:",
        reply_markup=back_keyboard("edit_menu"),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_time_limit)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_attempts, AttemptsCallback.filter())
async def edit_test_attempts_selection(callback: CallbackQuery, callback_data: AttemptsCallback, state: FSMContext) -> None:
    """Handle attempts selection while editing a test."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    if callback_data.value == "unlimited":
        await queries.update_test(test_id, max_attempts=None)
        await callback.message.edit_text(
            i18n("attempts_unlimited_confirmed", lang),
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.editing_test)
    else:
        await callback.message.edit_text(
            i18n("attempts_limited_prompt", lang),
            reply_markup=limited_attempts_keyboard(lang),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.editing_test_limited_attempts)

    await callback.answer()


@router.message(TeacherStates.editing_test_time_limit, F.text)
async def edit_test_time_limit_save(message: Message, state: FSMContext) -> None:
    """Save a new time limit or clear it."""
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    text = message.text.strip()
    data = await state.get_data()
    test_id = data["editing_test_id"]

    if text.lower() == "/skip":
        await queries.update_test(test_id, time_limit_minutes=None, set_time_limit=True)
        await message.answer("✅ Обмеження часу вимкнено.")
    else:
        try:
            minutes = int(text)
            if minutes <= 0:
                raise ValueError()
        except ValueError:
            await message.answer("⚠️ Невірний формат. Введіть число хвилин або /skip:")
            return
        await queries.update_test(test_id, time_limit_minutes=minutes, set_time_limit=True)
        await message.answer(f"✅ Ліміт часу оновлено: *{minutes} хв.*", parse_mode="Markdown")

    await message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test_limited_attempts, LimitedAttemptsCallback.filter())
async def edit_test_limited_attempts_save(callback: CallbackQuery, callback_data: LimitedAttemptsCallback, state: FSMContext) -> None:
    """Save limited attempts."""
    data = await state.get_data()
    test_id = data["editing_test_id"]
    
    await queries.update_test(test_id, max_attempts=callback_data.count)
    
    attempts_text = "1 спроба" if callback_data.count == 1 else f"{callback_data.count} спроб"
    await callback.message.edit_text(
        f"✅ Максимум спроб: *{attempts_text}*",
        parse_mode="Markdown",
    )
    await callback.answer()
    
    # Return to edit test menu
    await callback.message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "questions"))
async def edit_questions_list(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Show list of questions for editing."""
    test = await queries.get_test_with_questions(callback_data.id)
    questions = test.get("questions", []) if test else []
    
    if not questions:
        await callback.answer("❓ У цьому тесті немає питань.", show_alert=True)
        return
    
    await state.update_data(editing_test_id=callback_data.id)
    await callback.message.edit_text(
        f"❓ *Питання тесту: {test['title']}*\n\n"
        "Оберіть питання для редагування:",
        reply_markup=edit_questions_list_keyboard(callback_data.id, questions),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_questions_menu)
    await callback.answer()


@router.callback_query(TeacherStates.editing_questions_menu, EditQuestionCallback.filter(F.action == "delete"))
async def delete_question(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    """Delete a question."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await _handle_delete_test_question(callback, callback_data, state, lang)


@router.callback_query(TeacherStates.editing_questions_menu, EditQuestionCallback.filter(F.action == "edit"))
async def edit_question_prompt(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    """Show question edit menu."""
    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    await state.update_data(editing_question_id=callback_data.id)
    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(callback_data.id, question['text']),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_question_to_edit, EditQuestionCallback.filter(F.action == "delete"))
async def delete_question_from_edit_menu(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    """Delete question from question edit menu."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await _handle_delete_test_question(callback, callback_data, state, lang)


@router.callback_query(TeacherStates.selecting_question_to_edit, EditQuestionCallback.filter(F.action == "text"))
async def edit_question_text_prompt(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    await state.update_data(editing_question_id=callback_data.id)
    await callback.message.edit_text(
        f"✏️ Поточний текст питання:\n\n{question['text']}\n\n"
        "Надішліть новий текст питання:",
        reply_markup=back_keyboard("question_edit"),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_text)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_question_to_edit, EditQuestionCallback.filter(F.action == "options"))
async def edit_question_options_prompt(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    options = await queries.get_options_by_question(callback_data.id)
    await state.update_data(editing_question_id=callback_data.id)
    await callback.message.edit_text(
        f"📝 *Варіанти для питання*\n\n{question['text']}",
        reply_markup=edit_options_list_keyboard(callback_data.id, options),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.message(TeacherStates.editing_question_text, F.text)
async def edit_question_text_save(message: Message, state: FSMContext) -> None:
    new_text = message.text.strip()
    if not new_text:
        await message.answer("⚠️ Текст питання не може бути пустим. Спробуйте ще раз:")
        return

    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await message.answer("⚠️ Не знайдено питання для редагування.")
        return

    await queries.update_question(question_id, text=new_text)
    question = await queries.get_question(question_id)

    await message.answer("✅ Текст питання оновлено.")
    await message.answer(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(question_id, question['text']),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "edit"))
async def edit_option_prompt(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    option = await queries.get_option(callback_data.id)
    if not option:
        await callback.answer("❌ Вариант не знайдено.", show_alert=True)
        return

    await state.update_data(editing_option_id=callback_data.id)
    await callback.message.edit_text(
        f"✏️ Поточний текст варіанту:\n\n{option['text']}\n\n"
        "Надішліть новий текст варіанту:",
        reply_markup=back_keyboard("question_edit"),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_option_index)
    await callback.answer()


@router.message(TeacherStates.editing_question_option_index, F.text)
async def edit_option_save(message: Message, state: FSMContext) -> None:
    new_text = message.text.strip()
    if not new_text:
        await message.answer("⚠️ Текст варіанту не може бути пустим. Спробуйте ще раз:")
        return

    data = await state.get_data()
    option_id = data.get("editing_option_id")
    question_id = data.get("editing_question_id")
    if not option_id or not question_id:
        await message.answer("⚠️ Не знайдено варіант для редагування.")
        return

    option = await queries.get_option(option_id)
    if not option:
        await message.answer("⚠️ Вариант не знайдено.")
        return

    await queries.update_option(option_id, text=new_text, is_correct=option["is_correct"])
    question = await queries.get_question(question_id)
    options = await queries.get_options_by_question(question_id)

    await message.answer("✅ Варіант оновлено.")
    await message.answer(
        f"📝 *Варіанти для питання*\n\n{question['text']}",
        reply_markup=edit_options_list_keyboard(question_id, options),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "delete"))
async def delete_question_option(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await callback.answer("⚠️ Не знайдено питання для редагування.", show_alert=True)
        return

    option = await queries.get_option(callback_data.id)
    if not option:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)
        return
    if option.get("is_correct"):
        await callback.answer(i18n("cannot_delete_correct_option", lang), show_alert=True)
        return

    options = await queries.get_options_by_question(question_id)
    if len(options) <= 2:
        await callback.answer(i18n("min_options", lang), show_alert=True)
        return

    deleted = await queries.delete_option(callback_data.id)
    if deleted:
        await callback.answer("✅ Варіант видалено.", show_alert=True)
    else:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)

    question = await queries.get_question(question_id)
    options = await queries.get_options_by_question(question_id)
    await callback.message.edit_text(
        f"📝 *Варіанти для питання*\n\n{question['text']}",
        reply_markup=edit_options_list_keyboard(question_id, options),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "mark_correct"))
async def mark_question_option_correct(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await callback.answer("⚠️ Не знайдено питання для редагування.", show_alert=True)
        return

    await queries.mark_option_correct(callback_data.id, question_id)
    question = await queries.get_question(question_id)
    options = await queries.get_options_by_question(question_id)

    await callback.message.edit_text(
        f"📝 *Варіанти для питання*\n\n{question['text']}",
        reply_markup=edit_options_list_keyboard(question_id, options),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_options, BackCallback.filter())
async def back_from_edit_question_options(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(question_id, question['text']),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_text, BackCallback.filter())
async def back_from_edit_question_text(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(question_id, question['text']),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_option_index, BackCallback.filter())
async def back_from_edit_option_text(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer("❌ Питання не знайдено.", show_alert=True)
        return

    options = await queries.get_options_by_question(question_id)
    await callback.message.edit_text(
        f"📝 *Варіанти для питання*\n\n{question['text']}",
        reply_markup=edit_options_list_keyboard(question_id, options),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_question_to_edit, BackCallback.filter())
async def back_from_selecting_question(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    if not test_id:
        await callback.answer("⚠️ Не знайдено тест для повернення.", show_alert=True)
        return

    test = await queries.get_test_with_questions(test_id)
    questions = test.get("questions", []) if test else []
    if not questions:
        await callback.answer("❌ Не знайдено питань.", show_alert=True)
        return

    await callback.message.edit_text(
        f"❓ *Питання тесту: {test['title']}*\n\n"
        "Оберіть питання для редагування:",
        reply_markup=edit_questions_list_keyboard(test_id, questions),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_questions_menu)
    await callback.answer()


# Handle Back button during editing

@router.callback_query(TeacherStates.editing_test, BackCallback.filter())
async def back_from_edit_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to tests list from edit menu."""
    user = await queries.get_user(callback.from_user.id)
    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    await state.update_data(all_tests=tests)
    
    await callback.message.edit_text(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Оберіть предмет, щоб переглянути тести:",
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_title, BackCallback.filter())
async def back_from_edit_title(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from title edit."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_questions_menu, BackCallback.filter())
async def back_from_questions_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from questions list."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_description, BackCallback.filter())
async def back_from_edit_description(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from description edit."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_visibility, BackCallback.filter())
async def back_from_edit_visibility(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from visibility edit."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_time_limit, BackCallback.filter())
async def back_from_edit_time_limit(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from time limit edit."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_attempts, BackCallback.filter())
@router.callback_query(TeacherStates.editing_test_limited_attempts, BackCallback.filter())
async def back_from_edit_attempts(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to edit menu from attempts edit."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    
    if test_id:
        await callback.message.edit_text(
            "✏️ Редагування тесту",
            reply_markup=edit_test_menu_keyboard(test_id),
            parse_mode="Markdown",
        )
    await state.set_state(TeacherStates.editing_test)
    await callback.answer()
