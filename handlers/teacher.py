import logging
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from db import queries
from db.queries import QuestionType, matches_open_answer
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
    subject_tests_list_keyboard, answer_keyboard,
    answer_visibility_keyboard, attempts_keyboard, limited_attempts_keyboard,
    edit_test_menu_keyboard, edit_questions_list_keyboard, edit_options_list_keyboard,
    question_edit_menu_keyboard, statistics_period_keyboard,
    statistics_subjects_keyboard, statistics_subject_view_keyboard,
    statistics_test_back_keyboard,
    confirm_delete_keyboard, back_keyboard,
)
from states.states import TeacherStates

logger = logging.getLogger(__name__)
router = Router()

MAX_OPTIONS = 10  # per question


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


def _period_start(period: str) -> str | None:
    now = datetime.now(timezone.utc)
    if period == "week":
        since = now - timedelta(days=7)
    elif period == "month":
        since = now - timedelta(days=30)
    else:
        return None
    return since.astimezone(timezone.utc).isoformat()


def _question_summary(data: dict) -> str:
    qs = data.get("questions", [])
    cq = data.get("current_question", {})
    total = len(qs) + (1 if cq else 0)
    return f"Питань збережено: {len(qs)}"


def _demo_answer_keyboard(question: dict, selected_ids: Optional[list[int]] = None) -> InlineKeyboardMarkup:
    """Keyboard for the teacher demo test mode."""
    question_type = question.get("question_type", QuestionType.SINGLE_CHOICE)
    if question_type == QuestionType.MULTIPLE_CHOICE:
        rows = []
        selected_ids = selected_ids or []
        for opt in question.get("options", []):
            prefix = "✅ " if opt["id"] in selected_ids else "⭕ "
            rows.append([
                InlineKeyboardButton(
                    text=f"{prefix}{opt['text']}",
                    callback_data=f"demo_mult:{opt['id']}",
                )
            ])
        rows.append([
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="demo_mult_confirm")
        ])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    rows = []
    for opt in question.get("options", []):
        rows.append([
            InlineKeyboardButton(
                text=opt["text"],
                callback_data=f"demo_ans:{question['id']}:{opt['id']}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_demo_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    questions = data["questions"]
    idx = data["current_index"]
    question = questions[idx]
    total = len(questions)
    question_type = question.get("question_type", QuestionType.SINGLE_CHOICE)

    if question_type == QuestionType.MULTIPLE_CHOICE:
        keyboard = _demo_answer_keyboard(question, data.get("selected_option_ids", []))
        instruction = "\n\n📌 *Оберіть одну або кілька правильних відповідей, потім натисніть «Підтвердити»*"
    elif question_type == QuestionType.OPEN_ANSWER:
        keyboard = None
        instruction = i18n("open_answer_instruction", lang)
    else:
        keyboard = _demo_answer_keyboard(question)
        instruction = ""

    await message.answer(
        f"{i18n('question_counter', lang, current=idx + 1, total=total)}\n\n{question['text']}{instruction}",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


async def _finish_demo_test(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    total = len(data.get("questions", []))
    earned = float(data.get("score", 0.0))
    ratio = earned / total if total else 0.0
    pct = round(ratio * 100)
    max_points = data.get("max_points")
    scale = float(max_points) if max_points is not None else float(total)
    scaled = round(ratio * scale, 1) if scale > 0 else 0.0

    await state.clear()
    await message.answer(
        i18n(
            "demo_test_finished",
            lang,
            title=data.get("test_title", "Test"),
            score=f"{scaled:.1f}",
            total=f"{scale:.0f}",
            pct=pct,
        ),
        reply_markup=teacher_menu(lang),
        parse_mode="Markdown",
    )


async def _save_question_to_existing_test(state: FSMContext, cq: dict) -> bool:
    """Save a freshly created question directly to an existing test."""
    data = await state.get_data()
    test_id = data.get("editing_test_id")
    if not test_id:
        return False

    test = await queries.get_test_with_questions(test_id)
    order = len(test.get("questions", [])) if test else 0
    question_type = cq.get("question_type", QuestionType.SINGLE_CHOICE)
    q_type_value = question_type.value if isinstance(question_type, QuestionType) else str(question_type)

    question = await queries.add_question(test_id, cq["text"], order, q_type_value)
    for option in cq.get("options", []):
        await queries.add_option(question["id"], option["text"], bool(option.get("is_correct", False)))

    await state.update_data(current_question=None)
    return True


async def _go_to_tests_list(callback: CallbackQuery, state: FSMContext, user: dict) -> None:
    lang = user.get("language", "uk")
    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    await state.update_data(all_tests=tests)
    await callback.message.edit_text(
        i18n("teacher_tests_list", lang, count=len(tests)),
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)


def _question_type_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    """Keyboard for choosing question type."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n("question_type_single", lang),
                                 callback_data="qtype:single"),
            InlineKeyboardButton(text=i18n("question_type_multiple", lang),
                                 callback_data="qtype:multiple"),
        ],
        [
            InlineKeyboardButton(text=i18n("question_type_open", lang),
                                 callback_data="qtype:open"),
        ],
    ])


def _multiple_correct_keyboard(
    options: list[str], selected_indices: list[int], lang: str = "uk"
) -> InlineKeyboardMarkup:
    """Keyboard for selecting multiple correct answers."""
    rows = []
    for i, text in enumerate(options):
        is_selected = i in selected_indices
        prefix = "✅ " if is_selected else "⭕ "
        rows.append([InlineKeyboardButton(
            text=f"{prefix}{i + 1}. {text}",
            callback_data=f"mult_correct:{i}"
        )])
    rows.append([InlineKeyboardButton(
        text=i18n("multiple_correct_done", lang),
        callback_data="mult_correct:done"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _is_multiple_choice(question_type) -> bool:
    return question_type in (QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_CHOICE.value)


def _is_open_answer(question_type) -> bool:
    return question_type in (QuestionType.OPEN_ANSWER, QuestionType.OPEN_ANSWER.value)


def _accepted_answers_list(opts: list[str], lang: str) -> str:
    body = "\n".join(f"  {i + 1}. {o}" for i, o in enumerate(opts))
    return i18n("accepted_answers_list", lang, options=body)


def _edit_options_title(question: dict, lang: str) -> str:
    if _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE)):
        return f"📝 *Еталонні відповіді*\n\n{question['text']}"
    return f"📝 *Варіанти для питання*\n\n{question['text']}"


async def _options_edit_screen(question_id: int, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """Build options/reference-answers edit message and keyboard."""
    question = await queries.get_question(question_id)
    if not question:
        return "", InlineKeyboardMarkup(inline_keyboard=[])
    options = await queries.get_options_by_question(question_id)
    question_type = question.get("question_type", QuestionType.SINGLE_CHOICE)
    open_q = _is_open_answer(question_type)
    hint = ""
    if _is_multiple_choice(question_type):
        hint = "\n\n_" + i18n("mark_multiple_correct", lang) + "_"
    text = _edit_options_title(question, lang) + hint
    keyboard = edit_options_list_keyboard(
        question_id,
        options,
        open_answer=open_q,
        can_add=open_q and len(options) < MAX_OPTIONS,
        lang=lang,
    )
    return text, keyboard


def _option_text_edit_prompt(option_text: str, lang: str, *, open_answer: bool, adding: bool) -> str:
    if open_answer:
        if adding:
            return i18n("open_answer_add_during_edit", lang)
        return i18n("open_answer_edit_during_edit", lang, text=option_text)
    return (
        f"✏️ Поточний текст варіанту:\n\n{option_text}\n\n"
        "Надішліть новий текст варіанту:"
    )


async def _finalize_open_question(
    message_or_cq, state: FSMContext, cq: dict, opts: list[str], lang: str,
) -> None:
    """Save open-answer question with all reference answers marked correct."""
    option_dicts = [{"text": text, "is_correct": True} for text in opts]
    cq["options"] = option_dicts

    if await _save_question_to_existing_test(state, cq):
        data = await state.get_data()
        test_id = data.get("editing_test_id")
        test = await queries.get_test_with_questions(test_id) if test_id else None
        questions = test.get("questions", []) if test else []
        text = "✅ *Питання додано до тесту!*"
        if isinstance(message_or_cq, CallbackQuery):
            await message_or_cq.message.edit_text(text, parse_mode="Markdown")
            await message_or_cq.message.answer(
                f"❓ *Питання тесту: {test['title']}*\n\nОберіть питання для редагування:",
                reply_markup=edit_questions_list_keyboard(test_id, questions),
                parse_mode="Markdown",
            )
            await message_or_cq.answer(i18n("saved_notification", lang))
        else:
            await message_or_cq.answer(
                text,
                reply_markup=edit_questions_list_keyboard(test_id, questions),
                parse_mode="Markdown",
            )
        await state.set_state(TeacherStates.editing_questions_menu)
        return

    data = await state.get_data()
    questions: list = data.get("questions", [])
    questions.append(cq)
    await state.update_data(questions=questions, current_question=None)
    correct_texts = ", ".join(opts)
    q_num = len(questions)
    text = i18n("question_saved_open", lang, num=q_num, correct=correct_texts)
    markup = question_next_keyboard(lang)
    if isinstance(message_or_cq, CallbackQuery):
        await message_or_cq.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
        await message_or_cq.answer(i18n("saved_notification", lang))
    else:
        await message_or_cq.answer(text, reply_markup=markup, parse_mode="Markdown")


STATS_MAX_LINES = 20


def _sort_statistics(stats: list[dict]) -> list[dict]:
    with_sessions = [s for s in stats if s["total_sessions"]]
    without = [s for s in stats if not s["total_sessions"]]
    with_sessions.sort(key=lambda s: (-s["total_sessions"], -s["average_score"]))
    without.sort(key=lambda s: s["subject_name"].casefold())
    return with_sessions + without


def _stats_weighted_average(stats: list[dict]) -> float:
    total_sessions = sum(s["total_sessions"] for s in stats)
    if not total_sessions:
        return 0
    return round(
        sum(s["average_score"] * s["total_sessions"] for s in stats) / total_sessions,
        1,
    )


def _format_stats_overview(stats: list[dict], lang: str, *, period: str = "all") -> str:
    total_subjects = len(stats)
    total_tests = sum(s["test_count"] for s in stats)
    total_sessions = sum(s["total_sessions"] for s in stats)
    lines = [i18n("stats_title", lang)]

    if total_sessions:
        avg = _stats_weighted_average(stats)
        bar = _progress_bar(int(round(avg)))
        lines.append(i18n(
            "stats_overview", lang,
            bar=bar, avg=f"{avg}%",
            sessions=total_sessions, tests=total_tests, subjects=total_subjects,
        ))
    else:
        lines.append(i18n(
            "stats_overview_pending", lang,
            tests=total_tests, subjects=total_subjects,
        ))

    lines.append("")
    lines.append(i18n("stats_period_label", lang, period=i18n(f"stats_period_{period}", lang)))

    if len(stats) > 1:
        lines.extend(["", i18n("stats_pick_subject", lang)])
    return "\n".join(lines)


def _format_student_result_line(session: dict, lang: str, *, show_test: bool) -> str:
    name = (session.get("users") or {}).get("name") or "—"
    pct = round(session.get("percentage", 0))
    score = queries.format_points_value(session.get("score", 0))
    total = queries.format_points_value(queries.session_points_total(session))
    if show_test:
        return i18n(
            "stats_student_test", lang,
            name=name, pct=pct, score=score, total=total,
            test=session.get("test_title", "—"),
        )
    return i18n("stats_student", lang, name=name, pct=pct, score=score, total=total)


def _format_test_results_list(test_title: str, sessions: list[dict], lang: str) -> str:
    lines = [i18n("stats_test_title", lang, title=test_title)]
    if not sessions:
        lines.append(i18n("stats_test_empty", lang))
        return "\n".join(lines)
    for session in sessions:
        lines.append(_format_student_result_line(session, lang, show_test=False))
    return "\n".join(lines)


def _format_stats_subject(
    stat: dict, sessions: list[dict], lang: str, *, period: str = "all", max_lines: int = STATS_MAX_LINES,
) -> str:
    lines = [i18n("stats_subject_title", lang, name=stat["subject_name"])]
    lines.append(i18n("stats_period_label", lang, period=i18n(f"stats_period_{period}", lang)))
    if stat["total_sessions"]:
        pct = int(round(stat["average_score"]))
        lines.append(i18n(
            "stats_subject_result", lang,
            bar=_progress_bar(pct),
            avg=f"{stat['average_score']}%",
            sessions=stat["total_sessions"],
            tests=stat["test_count"],
        ))
        if sessions:
            lines.extend(["", i18n("stats_results_header", lang)])
            multi_test = len({s["test_id"] for s in sessions}) > 1
            for session in sessions[:max_lines]:
                lines.append(_format_student_result_line(session, lang, show_test=multi_test))
            if len(sessions) > max_lines:
                lines.append(i18n("stats_results_more", lang, count=len(sessions) - max_lines))
    else:
        lines.append(i18n("stats_subject_pending", lang, tests=stat["test_count"]))
    return "\n".join(lines)


async def _subject_stats_reply(
    user: dict,
    subject_id: int,
    lang: str,
    *,
    show_overview_back: bool,
    since: str | None = None,
    period: str = "all",
) -> tuple[str | None, InlineKeyboardMarkup | None]:
    stats = await queries.get_subject_statistics(user["id"], since=since)
    stat = next((s for s in stats if s["subject_id"] == subject_id), None)
    if not stat:
        return None, None
    sessions = await queries.get_subject_sessions(user["id"], subject_id, since=since)
    tests = await queries.get_subject_tests_stats(user["id"], subject_id, since=since)
    text = _format_stats_subject(stat, sessions, lang, period=period)
    tests_with_results = [t for t in tests if t["session_count"]]
    show_test_buttons = len(tests_with_results) > 1 or len(sessions) > STATS_MAX_LINES
    keyboard = statistics_subject_view_keyboard(
        tests, subject_id, lang,
        show_test_buttons=show_test_buttons,
        show_overview_back=show_overview_back,
    )
    if keyboard is not None:
        keyboard.inline_keyboard.extend(statistics_period_keyboard(lang, subject_id=subject_id).inline_keyboard)
    return text, keyboard


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



async def _prompt_max_points(message: Message, state: FSMContext, lang: str) -> None:
    await message.answer(i18n("max_points_prompt", lang), parse_mode="Markdown")
    await state.set_state(TeacherStates.choosing_max_points)


def _parse_max_points(text: str) -> Optional[int]:
    try:
        value = int(text.strip())
        if 1 <= value <= 100:
            return value
    except ValueError:
        pass
    return None


@router.message(TeacherStates.choosing_time_limit, F.text)
async def choose_time_limit(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    text = message.text.strip()
    if text.lower() == "/skip":
        await state.update_data(time_limit_minutes=None)
        await _prompt_max_points(message, state, lang)
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
    await _prompt_max_points(message, state, lang)


@router.message(TeacherStates.choosing_max_points, F.text)
async def choose_max_points(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    points = _parse_max_points(message.text)
    if points is None:
        await message.answer(i18n("max_points_invalid", lang))
        return

    await state.update_data(max_points=points)
    await message.answer(i18n("max_points_set", lang, points=points), parse_mode="Markdown")
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
    await state.update_data(current_question={"text": q_text, "options": [], "question_type": QuestionType.SINGLE_CHOICE})
    await message.answer(
        i18n("question_confirmed", lang, text=q_text, max=MAX_OPTIONS),
        parse_mode="Markdown",
    )
    # Ask for question type
    await message.answer(
        i18n("question_type_prompt", lang),
        reply_markup=_question_type_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_question_type)


# Question type selection

@router.callback_query(TeacherStates.choosing_question_type, F.data.startswith("qtype:"))
async def choose_question_type(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    qtype = callback.data.split(":")[1]

    # Map callback data to QuestionType enum
    if qtype == "single":
        question_type = QuestionType.SINGLE_CHOICE
    elif qtype == "multiple":
        question_type = QuestionType.MULTIPLE_CHOICE
    elif qtype == "open":
        question_type = QuestionType.OPEN_ANSWER
    else:
        question_type = QuestionType.SINGLE_CHOICE

    data = await state.get_data()
    cq = data.get("current_question", {})
    cq["question_type"] = question_type
    await state.update_data(current_question=cq)

    if question_type == QuestionType.MULTIPLE_CHOICE:
        type_text = i18n("question_type_multiple_selected", lang)
        next_prompt = i18n("option_prompt", lang, num=1)
    elif question_type == QuestionType.OPEN_ANSWER:
        type_text = i18n("question_type_open_selected", lang)
        next_prompt = i18n("open_answer_prompt", lang, num=1)
    else:
        type_text = i18n("question_type_single_selected", lang)
        next_prompt = i18n("option_prompt", lang, num=1)
    await callback.message.edit_text(
        type_text + "\n\n" + next_prompt,
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_option)
    await callback.answer()


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
    question_type = cq.get("question_type", QuestionType.SINGLE_CHOICE)

    if n >= MAX_OPTIONS:
        if _is_open_answer(question_type):
            await _finalize_open_question(message, state, cq, opts, lang)
            return
        options_body = _options_list(opts).replace("📋 Варіанти:\n", "").replace("📋 Options:\n", "")
        if _is_multiple_choice(question_type):
            await state.update_data(selected_correct_indices=[])
            await message.answer(
                i18n(
                    "options_max_reached_multiple", lang,
                    options=options_body,
                    instruction=i18n("mark_multiple_correct", lang),
                ),
                reply_markup=_multiple_correct_keyboard(opts, [], lang),
                parse_mode="Markdown",
            )
            await state.set_state(TeacherStates.marking_multiple_correct)
        else:
            await message.answer(
                i18n("options_max_reached", lang, options=options_body),
                reply_markup=correct_option_keyboard(opts),
                parse_mode="Markdown",
            )
            await state.set_state(TeacherStates.marking_correct)
    else:
        if _is_open_answer(question_type):
            prompt = i18n("open_answer_prompt_or_done", lang, num=n + 1)
            body = _accepted_answers_list(opts, lang)
        else:
            prompt = i18n("option_prompt_or_done", lang, num=n + 1)
            body = _options_list(opts)
        await message.answer(
            body + "\n\n" + prompt,
            reply_markup=options_input_keyboard(opts, lang, question_type=question_type),
            parse_mode="Markdown",
        )


@router.callback_query(TeacherStates.entering_option, DoneOptionsCallback.filter())
async def done_options(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    cq = data["current_question"]
    opts = cq["options"]
    question_type = cq.get("question_type", QuestionType.SINGLE_CHOICE)
    min_count = 1 if _is_open_answer(question_type) else 2
    if len(opts) < min_count:
        key = "min_accepted_answers" if _is_open_answer(question_type) else "min_options"
        await callback.answer(i18n(key, lang), show_alert=True)
        return

    if _is_open_answer(question_type):
        await _finalize_open_question(callback, state, cq, opts, lang)
        return

    if _is_multiple_choice(question_type):
        await state.update_data(selected_correct_indices=[])
        await callback.message.edit_text(
            _options_list(opts) + "\n\n" + i18n("mark_multiple_correct", lang),
            reply_markup=_multiple_correct_keyboard(opts, [], lang),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.marking_multiple_correct)
    else:
        await callback.message.edit_text(
            _options_list(opts) + "\n\n" + i18n("mark_correct", lang),
            reply_markup=correct_option_keyboard(opts),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.marking_correct)
    await callback.answer()


# Questions loop - mark correct answer (single choice)

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

    if await _save_question_to_existing_test(state, cq):
        test_id = data.get("editing_test_id")
        test = await queries.get_test_with_questions(test_id) if test_id else None
        questions = test.get("questions", []) if test else []
        await callback.message.edit_text(
            "✅ *Питання додано до тесту!*",
            parse_mode="Markdown",
        )
        await callback.message.answer(
            f"❓ *Питання тесту: {test['title']}*\n\nОберіть питання для редагування:",
            reply_markup=edit_questions_list_keyboard(test_id, questions),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.editing_questions_menu)
        await callback.answer(i18n("saved_notification", lang))
        return

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


# Questions loop - mark multiple correct answers

@router.callback_query(TeacherStates.marking_multiple_correct, F.data.startswith("mult_correct:"))
async def mark_multiple_correct(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    cq = data["current_question"]
    opts = cq["options"]
    
    # Get currently selected indices from state
    selected_indices = data.get("selected_correct_indices", [])
    
    action = callback.data.split(":")[1]
    
    if action == "done":
        # Save the question with multiple correct answers
        if not selected_indices:
            await callback.answer(i18n("select_at_least_one", lang), show_alert=True)
            return
        
        # Build option dicts
        option_dicts = [
            {"text": text, "is_correct": (i in selected_indices)}
            for i, text in enumerate(opts)
        ]
        cq["options"] = option_dicts
        
        if await _save_question_to_existing_test(state, cq):
            test_id = data.get("editing_test_id")
            test = await queries.get_test_with_questions(test_id) if test_id else None
            questions = test.get("questions", []) if test else []
            await callback.message.edit_text(
                "✅ *Питання додано до тесту!*",
                parse_mode="Markdown",
            )
            await callback.message.answer(
                f"❓ *Питання тесту: {test['title']}*\n\nОберіть питання для редагування:",
                reply_markup=edit_questions_list_keyboard(test_id, questions),
                parse_mode="Markdown",
            )
            await state.set_state(TeacherStates.editing_questions_menu)
            await callback.answer(i18n("saved_notification", lang))
            return

        # Append to questions list
        questions: list = data.get("questions", [])
        questions.append(cq)
        await state.update_data(questions=questions, current_question=None, selected_correct_indices=[])
        
        correct_texts = ", ".join([opts[i] for i in selected_indices])
        q_num = len(questions)
        
        await callback.message.edit_text(
            i18n("question_saved_multiple", lang, num=q_num, correct=correct_texts),
            reply_markup=question_next_keyboard(lang),
            parse_mode="Markdown",
        )
        await callback.answer(i18n("saved_notification", lang))
    else:
        # Toggle selection
        idx = int(action)
        if idx in selected_indices:
            selected_indices.remove(idx)
        else:
            selected_indices.append(idx)
        
        await state.update_data(selected_correct_indices=selected_indices)
        await callback.message.edit_reply_markup(
            reply_markup=_multiple_correct_keyboard(opts, selected_indices, lang)
        )
        await callback.answer()


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
        max_points=data.get("max_points"),
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

    points_line = ""
    if data.get("max_points") is not None:
        points_line = f"📊 Максимум балів: *{data['max_points']}*\n"

    await callback.message.edit_text(
        i18n(
            "test_created",
            lang,
            title=data["title"],
            subject=data["subject_name"],
            count=len(questions),
            access_line=("🌐 Публічний\n" if data["is_public"] else "🔒 Приватний\n") + attempts_info + time_limit_line + points_line + code_line,
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
        i18n("teacher_tests_list", user.get("language", "uk"), count=len(tests)),
        reply_markup=my_tests_subjects_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)



@router.message(F.text.in_([
    i18n("menu_statistics", "uk"),
    i18n("menu_statistics", "en"),
]))
async def view_statistics(message: Message, state: FSMContext) -> None:
    """Show compact statistics overview with per-subject navigation."""
    user = await _require_teacher(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()
    period = "all"
    since = _period_start(period)
    stats = await queries.get_subject_statistics(user["id"], since=since)
    if not stats:
        await message.answer(
            f"{i18n('stats_title', lang)}\n\n{i18n('stats_empty', lang)}",
            parse_mode="Markdown",
        )
        return

    sorted_stats = _sort_statistics(stats)
    if len(sorted_stats) == 1:
        text, reply_markup = await _subject_stats_reply(
            user,
            sorted_stats[0]["subject_id"],
            lang,
            show_overview_back=False,
            since=since,
            period=period,
        )
        if not text:
            await message.answer(
                f"{i18n('stats_title', lang)}\n\n{i18n('stats_empty', lang)}",
                parse_mode="Markdown",
            )
            return
    else:
        text = _format_stats_overview(sorted_stats, lang, period=period)
        reply_markup = statistics_subjects_keyboard(sorted_stats)
        reply_markup.inline_keyboard.extend(statistics_period_keyboard(lang).inline_keyboard)
    await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    await state.set_state(TeacherStates.viewing_statistics)


@router.callback_query(TeacherStates.viewing_tests_and_results, SubjectCallback.filter())
async def view_tests_by_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    """Show tests for a selected subject."""
    user = await _require_teacher(callback)
    if not user:
        return
    lang = user.get("language", "uk")

    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    subject_tests = [t for t in tests if t.get("subject_id") == callback_data.id]
    if not subject_tests:
        await callback.answer(i18n("no_tests_in_subject_teacher", lang), show_alert=True)
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

    await _go_to_tests_list(callback, state, user)
    await callback.answer()


@router.callback_query(TeacherStates.viewing_statistics, StatisticsCallback.filter())
async def show_statistics(callback: CallbackQuery, callback_data: StatisticsCallback, state: FSMContext) -> None:
    """Statistics overview or subject detail."""
    user = await _require_teacher(callback)
    if not user:
        return
    lang = user.get("language", "uk")

    data = await state.get_data()
    period = data.get("stats_period", "all")
    if callback_data.action == "period":
        period = callback_data.period or "all"
    await state.update_data(stats_period=period)
    since = _period_start(period)
    stats = await queries.get_subject_statistics(user["id"], since=since)
    if not stats:
        await callback.message.edit_text(
            f"{i18n('stats_title', lang)}\n\n{i18n('stats_empty', lang)}",
            parse_mode="Markdown",
        )
        await state.clear()
        await callback.answer()
        return

    sorted_stats = _sort_statistics(stats)

    if callback_data.action == "period":
        period = callback_data.period or "all"
        await state.update_data(stats_period=period)
        subject_id = callback_data.id or 0
        if subject_id:
            text, keyboard = await _subject_stats_reply(
                user,
                subject_id,
                lang,
                show_overview_back=len(sorted_stats) > 1,
                since=_period_start(period),
                period=period,
            )
            if not text:
                await callback.answer(i18n("subject_not_found", lang), show_alert=True)
                return
            await state.update_data(stats_subject_id=subject_id)
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
            await callback.answer()
            return

    if callback_data.action == "test" and callback_data.id:
        test = await queries.get_test(callback_data.id)
        if not test:
            await callback.answer(i18n("test_not_found", lang), show_alert=True)
            return
        sessions = await queries.get_test_results(callback_data.id, since=since)
        subject_id = callback_data.sub or test.get("subject_id", 0)
        await callback.message.edit_text(
            _format_test_results_list(test["title"], sessions, lang),
            reply_markup=statistics_test_back_keyboard(subject_id, lang),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    if callback_data.action == "subject" and callback_data.id:
        text, keyboard = await _subject_stats_reply(
            user,
            callback_data.id,
            lang,
            show_overview_back=len(sorted_stats) > 1,
            since=since,
            period=period,
        )
        if not text:
            await callback.answer(i18n("subject_not_found", lang), show_alert=True)
            return
        await state.update_data(stats_subject_id=callback_data.id)
        await callback.message.edit_text(
            text, reply_markup=keyboard, parse_mode="Markdown",
        )
        await callback.answer()
        return

    if len(sorted_stats) == 1:
        text, keyboard = await _subject_stats_reply(
            user,
            sorted_stats[0]["subject_id"],
            lang,
            show_overview_back=False,
            since=since,
            period=period,
        )
        await state.update_data(stats_subject_id=sorted_stats[0]["subject_id"])
        await callback.message.edit_text(
            text, reply_markup=keyboard, parse_mode="Markdown",
        )
    else:
        reply_markup = statistics_subjects_keyboard(sorted_stats)
        reply_markup.inline_keyboard.extend(statistics_period_keyboard(lang).inline_keyboard)
        await callback.message.edit_text(
            _format_stats_overview(sorted_stats, lang, period=period),
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(TeacherStates.viewing_tests_and_results, TestCallback.filter())
async def handle_test_action(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    if callback_data.action == "results":
        await _show_results(callback, callback_data.id, state)
    elif callback_data.action == "delete":
        await _delete_test(callback, callback_data.id, state)
    elif callback_data.action == "demo":
        await start_teacher_self_test(callback, callback_data, state)
    elif callback_data.action == "open":
        # Show action menu for the selected test
        test = await queries.get_test(callback_data.id)
        if not test:
            await callback.answer(i18n("test_not_found", lang), show_alert=True)
            return
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Переглянути результати", callback_data=TestCallback(id=callback_data.id, action="results").pack())],
            [InlineKeyboardButton(text="🧪 Пройти для тестування", callback_data=TestCallback(id=callback_data.id, action="demo").pack())],
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


@router.callback_query(TeacherStates.viewing_tests_and_results, TestCallback.filter(F.action == "demo"))
async def start_teacher_self_test(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    """Launch a local demo run of the teacher's own test without saving results to DB."""
    user = await _require_teacher(callback)
    if not user:
        return

    test = await queries.get_test_with_questions(callback_data.id)
    if not test or not test.get("questions"):
        await callback.answer(i18n("test_no_questions", user.get("language", "uk")), show_alert=True)
        return

    lang = user.get("language", "uk")
    max_pts = float(test["max_points"]) if test.get("max_points") is not None else float(len(test["questions"]))

    await state.clear()
    await state.set_state(TeacherStates.demo_taking_test)
    await state.update_data(
        test_id=test["id"],
        test_title=test["title"],
        questions=test["questions"],
        current_index=0,
        score=0.0,
        max_points=max_pts,
        show_answer_correctness=test.get("show_answer_correctness", False),
        selected_option_ids=[],
        lang=lang,
    )

    await callback.message.edit_text(
        i18n("demo_test_intro", lang, title=test["title"], count=len(test["questions"])),
        parse_mode="Markdown",
    )
    await _send_demo_question(callback.message, state)
    await callback.answer()


@router.callback_query(TeacherStates.demo_taking_test, F.data.startswith("demo_ans:"))
async def handle_demo_single_answer(callback: CallbackQuery, state: FSMContext) -> None:
    user = await _require_teacher(callback)
    if not user:
        return

    _, q_id_str, opt_id_str = callback.data.split(":")
    question_id = int(q_id_str)
    option_id = int(opt_id_str)

    data = await state.get_data()
    lang = data.get("lang", user.get("language", "uk"))
    questions = data["questions"]
    idx = data["current_index"]
    question = questions[idx]

    selected_opt = next((opt for opt in question.get("options", []) if opt["id"] == option_id), None)
    if not selected_opt:
        await callback.answer(i18n("answer_error", lang), show_alert=True)
        return

    is_correct = bool(selected_opt.get("is_correct"))
    score = float(data.get("score", 0.0)) + (1 if is_correct else 0)
    await state.update_data(score=score, current_index=idx + 1)

    show_answers = data.get("show_answer_correctness", False)
    if show_answers:
        feedback = i18n("correct_answer", lang) if is_correct else i18n("wrong_answer", lang, correct=next((opt["text"] for opt in question.get("options", []) if opt.get("is_correct")), "—"))
    else:
        feedback = i18n("answer_saved", lang)
    await callback.message.edit_reply_markup()
    await callback.message.answer(feedback, parse_mode="Markdown")

    if idx + 1 >= len(questions):
        await _finish_demo_test(callback.message, state, lang)
    else:
        await _send_demo_question(callback.message, state)
    await callback.answer()


@router.callback_query(TeacherStates.demo_taking_test, F.data.startswith("demo_mult:"))
async def toggle_demo_multiple_answer(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "demo_mult_confirm":
        return

    _, opt_id_str = callback.data.split(":")
    option_id = int(opt_id_str)
    data = await state.get_data()
    selected = list(data.get("selected_option_ids", []))
    if option_id in selected:
        selected.remove(option_id)
    else:
        selected.append(option_id)
    await state.update_data(selected_option_ids=selected)

    questions = data["questions"]
    idx = data["current_index"]
    question = questions[idx]
    await callback.message.edit_reply_markup(reply_markup=_demo_answer_keyboard(question, selected))
    await callback.answer()


@router.callback_query(TeacherStates.demo_taking_test, F.data == "demo_mult_confirm")
async def confirm_demo_multiple_answer(callback: CallbackQuery, state: FSMContext) -> None:
    user = await _require_teacher(callback)
    if not user:
        return

    data = await state.get_data()
    lang = data.get("lang", user.get("language", "uk"))
    questions = data["questions"]
    idx = data["current_index"]
    question = questions[idx]
    selected = set(data.get("selected_option_ids", []))

    if not selected:
        await callback.answer(i18n("select_at_least_one", lang), show_alert=True)
        return

    correct_ids = {opt["id"] for opt in question.get("options", []) if opt.get("is_correct")}
    if not correct_ids:
        score_contrib = 0.0
    else:
        correct_selections = len(selected & correct_ids)
        incorrect_selections = len(selected - correct_ids)
        score_contrib = max(0.0, min(1.0, (correct_selections / len(correct_ids)) - incorrect_selections * 0.5))

    score = float(data.get("score", 0.0)) + score_contrib
    await state.update_data(score=score, selected_option_ids=[], current_index=idx + 1)

    show_answers = data.get("show_answer_correctness", False)
    if show_answers:
        if score_contrib >= 1.0:
            feedback = i18n("correct_answer", lang)
        elif score_contrib > 0:
            feedback = i18n("partial_correct", lang, score=int(score_contrib * 100))
        else:
            feedback = i18n("wrong_answer_multiple", lang, correct=", ".join(opt["text"] for opt in question.get("options", []) if opt.get("is_correct")))
    else:
        feedback = i18n("answer_saved", lang)

    await callback.message.edit_reply_markup()
    await callback.message.answer(feedback, parse_mode="Markdown")

    if idx + 1 >= len(questions):
        await _finish_demo_test(callback.message, state, lang)
    else:
        await _send_demo_question(callback.message, state)
    await callback.answer()


@router.message(TeacherStates.demo_taking_test, F.text)
async def handle_demo_open_answer(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_index"]
    question = questions[idx]

    if question.get("question_type", QuestionType.SINGLE_CHOICE) != QuestionType.OPEN_ANSWER:
        await message.answer(i18n("use_buttons_not_text", lang))
        return

    answer_text = message.text.strip()
    if not answer_text:
        await message.answer(i18n("open_answer_empty", lang))
        return

    is_correct = matches_open_answer(answer_text, question.get("options", []))
    score = float(data.get("score", 0.0)) + (1 if is_correct else 0)
    await state.update_data(score=score, current_index=idx + 1)

    show_answers = data.get("show_answer_correctness", False)
    if show_answers:
        feedback = i18n("correct_answer", lang) if is_correct else i18n("wrong_answer_open", lang, correct=", ".join(opt["text"] for opt in question.get("options", []) if opt.get("is_correct")))
    else:
        feedback = i18n("answer_saved", lang)
    await message.answer(feedback, parse_mode="Markdown")

    if idx + 1 >= len(questions):
        await _finish_demo_test(message, state, lang)
    else:
        await _send_demo_question(message, state)


async def _show_results(callback: CallbackQuery, test_id: int, state: FSMContext) -> None:
    test = await queries.get_test(test_id)
    sessions = await queries.get_test_results(test_id)

    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    if not sessions:
        await callback.message.edit_text(
            _format_test_results_list(test["title"], [], lang),
            parse_mode="Markdown",
        )
        return

    text = _format_test_results_list(test["title"], sessions, lang)
    await callback.message.edit_text(text, parse_mode="Markdown")


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
    user = await _require_teacher(callback)
    if not user:
        return
    lang = user.get("language", "uk")
    data = await state.get_data()
    test_id = data.get("deleting_test_id")
    
    if not test_id:
        await callback.answer(i18n("error_test_not_found", lang), show_alert=True)
        return
    
    if callback_data.action == "yes":
        deleted = await queries.deactivate_test(test_id, user["id"])
        await _go_to_tests_list(callback, state, user)
        await callback.answer(i18n("test_deleted", lang) if deleted else i18n("delete_error", lang))
    else:
        # Cancel deletion
        await _go_to_tests_list(callback, state, user)
        await callback.answer(i18n("cancelled", lang))


@router.callback_query(TeacherStates.confirming_delete_test, BackCallback.filter())
async def back_from_delete_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to tests list from delete confirmation."""
    user = await _require_teacher(callback)
    if not user:
        return
    await _go_to_tests_list(callback, state, user)
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
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return

    test = await queries.get_test_with_questions(test_id)
    if not test:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return

    if len(test.get("questions", [])) <= 1:
        await callback.answer(i18n("cannot_delete_last_question", lang), show_alert=True)
        return

    deleted = await queries.delete_question(callback_data.id)
    if not deleted:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
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
    await callback.answer(i18n("question_deleted", lang))


# Edit test

@router.callback_query(EditTestCallback.filter(F.action == "menu"))
async def edit_test_menu(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Open edit test menu."""
    user = await _require_teacher(callback)
    if not user:
        return
    
    lang = user.get("language", "uk") if user else "uk"

    test = await queries.get_test(callback_data.id)
    if not test or test["teacher_id"] != user["id"]:
        await callback.answer(i18n("not_author", lang), show_alert=True)
        return
    
    badge = "🌐" if test["is_public"] else "🔒"
    vis_text = "Публічний" if test["is_public"] else "Приватний"
    att_text = f"{test['max_attempts']} спроб" if test['max_attempts'] else "Необмежено"
    time_text = f"{test['time_limit_minutes']} хв." if test.get("time_limit_minutes") is not None else "Немає"
    pts = test.get("max_points")
    points_text = f"{queries.format_points_value(pts)}" if pts is not None else "—"
    
    await callback.message.edit_text(
        f"✏️ *Редагування тесту*\n\n"
        f"📝 Назва: *{test['title']}*\n"
        f"🔍 Видимість: {badge} {vis_text}\n"
        f"⏱️ Спроби: {att_text}\n"
        f"⏱️ Ліміт часу: {time_text}\n"
        f"📊 Максимум балів: {points_text}\n\n"
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
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    new_title = message.text.strip()
    if len(new_title) < 3:
        await message.answer(i18n("title_too_short", lang))
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
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await callback.answer(i18n("saved_notification", lang))
    
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
        await message.answer(i18n("time_limit_disabled", lang))
    else:
        try:
            minutes = int(text)
            if minutes <= 0:
                raise ValueError()
        except ValueError:
            await message.answer(i18n("time_limit_invalid", lang))
            return
        await queries.update_test(test_id, time_limit_minutes=minutes, set_time_limit=True)
        await message.answer(i18n("time_limit_set", lang, minutes=minutes), parse_mode="Markdown")

    await message.answer(
        f"✏️ *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "points"))
async def edit_test_max_points_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for the test grading scale (max points)."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    test = await queries.get_test(callback_data.id)
    current = test.get("max_points")
    current_label = queries.format_points_value(current) if current is not None else "—"
    await callback.message.edit_text(
        i18n("max_points_edit_prompt", lang, current=current_label),
        reply_markup=back_keyboard("edit_menu"),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_max_points)
    await callback.answer()


@router.message(TeacherStates.editing_test_max_points, F.text)
async def edit_test_max_points_save(message: Message, state: FSMContext) -> None:
    """Save new max points for the test."""
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    points = _parse_max_points(message.text)
    if points is None:
        await message.answer(i18n("max_points_invalid", lang))
        return

    data = await state.get_data()
    test_id = data["editing_test_id"]
    await queries.update_test(test_id, max_points=float(points))
    await message.answer(
        i18n("max_points_updated", lang, points=points),
        parse_mode="Markdown",
    )
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
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    test = await queries.get_test_with_questions(callback_data.id)
    questions = test.get("questions", []) if test else []
    
    if not questions:
        await callback.answer(i18n("no_questions_error", lang), show_alert=True)
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


@router.callback_query(TeacherStates.editing_questions_menu, EditTestCallback.filter(F.action == "add_question"))
async def start_add_question_to_test(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Start adding a new question to an existing test."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await state.update_data(editing_test_id=callback_data.id)
    await callback.message.edit_text(
        i18n("enter_question_text", lang, num=1),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_question_text)
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
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    await state.update_data(editing_question_id=callback_data.id)
    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))
    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(
            callback_data.id, question['text'], open_answer=open_q,
        ),
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
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
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
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    question = await queries.get_question(callback_data.id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await state.update_data(editing_question_id=callback_data.id, adding_new_option=False)
    text, keyboard = await _options_edit_screen(callback_data.id, lang)
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_options, EditQuestionCallback.filter(F.action == "add_answer"))
async def add_accepted_answer_prompt(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    question = await queries.get_question(callback_data.id)
    if not question or not _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE)):
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    options = await queries.get_options_by_question(callback_data.id)
    if len(options) >= MAX_OPTIONS:
        await callback.answer(
            i18n("open_answer_max_reached", lang, max=MAX_OPTIONS),
            show_alert=True,
        )
        return

    await state.update_data(
        editing_question_id=callback_data.id,
        adding_new_option=True,
        editing_option_id=None,
    )
    await callback.message.edit_text(
        _option_text_edit_prompt("", lang, open_answer=True, adding=True),
        reply_markup=back_keyboard("options"),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_option_index)
    await callback.answer()


@router.message(TeacherStates.editing_question_text, F.text)
async def edit_question_text_save(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    new_text = message.text.strip()
    if not new_text:
        await message.answer(i18n("question_text_empty", lang))
        return

    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await message.answer(i18n("question_edit_not_found", lang))
        return

    await queries.update_question(question_id, text=new_text)
    question = await queries.get_question(question_id)
    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))

    await message.answer(i18n("question_text_updated", lang))
    await message.answer(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(
            question_id, question['text'], open_answer=open_q,
        ),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "edit"))
async def edit_option_prompt(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    option = await queries.get_option(callback_data.id)
    if not option:
        await callback.answer(i18n("option_not_found", lang), show_alert=True)
        return

    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id) if question_id else None
    open_q = _is_open_answer(
        (question or {}).get("question_type", QuestionType.SINGLE_CHOICE)
    )

    await state.update_data(editing_option_id=callback_data.id, adding_new_option=False)
    await callback.message.edit_text(
        _option_text_edit_prompt(option["text"], lang, open_answer=open_q, adding=False),
        reply_markup=back_keyboard("options"),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_question_option_index)
    await callback.answer()


@router.message(TeacherStates.editing_question_option_index, F.text)
async def edit_option_save(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    new_text = message.text.strip()
    if not new_text:
        await message.answer(i18n("option_empty", lang))
        return

    data = await state.get_data()
    option_id = data.get("editing_option_id")
    question_id = data.get("editing_question_id")
    adding_new = data.get("adding_new_option", False)
    if not question_id or (not adding_new and not option_id):
        await message.answer(i18n("option_edit_not_found", lang))
        return

    question = await queries.get_question(question_id)
    if not question:
        await message.answer(i18n("question_not_found", lang))
        return
    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))

    if adding_new:
        if not open_q:
            await message.answer(i18n("adding_option_error", lang))
            return
        options = await queries.get_options_by_question(question_id)
        if len(options) >= MAX_OPTIONS:
            await message.answer(i18n("open_answer_max_reached", lang, max=MAX_OPTIONS))
            return
        await queries.add_option(question_id, new_text, is_correct=True)
        saved_msg = i18n("accepted_answer_added", lang)
    else:
        option = await queries.get_option(option_id)
        if not option:
            await message.answer(i18n("option_not_found", lang))
            return
        is_correct = True if open_q else option["is_correct"]
        await queries.update_option(option_id, text=new_text, is_correct=is_correct)
        saved_msg = i18n("accepted_answer_updated", lang) if open_q else i18n("option_updated", lang)

    await state.update_data(adding_new_option=False)
    text, keyboard = await _options_edit_screen(question_id, lang)
    await message.answer(saved_msg)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(TeacherStates.editing_question_options)


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "delete"))
async def delete_question_option(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await callback.answer(i18n("question_edit_not_found", lang), show_alert=True)
        return

    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return
    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))

    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return
    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))

    option = await queries.get_option(callback_data.id)
    if not option:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return
    if not open_q and option.get("is_correct"):
        await callback.answer(i18n("cannot_delete_correct_option", lang), show_alert=True)
        return

    options = await queries.get_options_by_question(question_id)
    min_count = 1 if open_q else 2
    if len(options) <= min_count:
        key = "min_accepted_answers" if open_q else "min_options"
        await callback.answer(i18n(key, lang), show_alert=True)
        return

    deleted = await queries.delete_option(callback_data.id)
    if not deleted:
        await callback.answer(i18n("delete_error", lang), show_alert=True)
        return

    text, keyboard = await _options_edit_screen(question_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    deleted_msg = i18n("accepted_answer_deleted", lang) if open_q else i18n("option_deleted", lang)
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer(deleted_msg)


@router.callback_query(TeacherStates.editing_question_options, EditOptionCallback.filter(F.action == "mark_correct"))
async def mark_question_option_correct(callback: CallbackQuery, callback_data: EditOptionCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    if not question_id:
        await callback.answer(i18n("question_edit_not_found", lang), show_alert=True)
        return

    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    question_type = question.get("question_type", QuestionType.SINGLE_CHOICE)
    open_q = _is_open_answer(question_type)
    if open_q:
        await callback.answer()
        return

    if _is_multiple_choice(question_type):
        option = await queries.get_option(callback_data.id)
        if option and option.get("is_correct"):
            options = await queries.get_options_by_question(question_id)
            if sum(1 for o in options if o.get("is_correct")) <= 1:
                await callback.answer(i18n("cannot_unmark_last_correct", lang), show_alert=True)
                return
        await queries.toggle_option_correct(callback_data.id)
    else:
        await queries.mark_option_correct(
            callback_data.id, question_id, QuestionType.SINGLE_CHOICE
        )

    text, keyboard = await _options_edit_screen(question_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_options, BackCallback.filter())
async def back_from_edit_question_options(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))
    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(
            question_id, question['text'], open_answer=open_q,
        ),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_text, BackCallback.filter())
async def back_from_edit_question_text(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    open_q = _is_open_answer(question.get("question_type", QuestionType.SINGLE_CHOICE))
    await callback.message.edit_text(
        f"❓ *Редагування питання*\n\n{question['text']}",
        reply_markup=question_edit_menu_keyboard(
            question_id, question['text'], open_answer=open_q,
        ),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.selecting_question_to_edit)
    await callback.answer()


@router.callback_query(TeacherStates.editing_question_option_index, BackCallback.filter())
async def back_from_edit_option_text(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    question = await queries.get_question(question_id)
    if not question:
        await callback.answer(i18n("question_not_found", lang), show_alert=True)
        return

    await state.update_data(adding_new_option=False)
    text, keyboard = await _options_edit_screen(question_id, lang)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(TeacherStates.editing_question_options)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_question_to_edit, BackCallback.filter())
async def back_from_selecting_question(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"

    data = await state.get_data()
    test_id = data.get("editing_test_id")
    if not test_id:
        await callback.answer(i18n("test_return_not_found", lang), show_alert=True)
        return

    test = await queries.get_test_with_questions(test_id)
    questions = test.get("questions", []) if test else []
    if not questions:
        await callback.answer(i18n("questions_not_found", lang), show_alert=True)
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
    user = await _require_teacher(callback)
    if not user:
        return
    await _go_to_tests_list(callback, state, user)
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
