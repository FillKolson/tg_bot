import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from db import queries
from db.queries import QuestionType, matches_open_answer, save_open_answer
from config.i18n import i18n
from keyboards.callbacks import (
    SubjectCallback, TestCallback, BackCallback, SearchCallback, TeacherFilterCallback,
    StudentResultsCallback,
)
from keyboards.keyboards import (
    student_menu, subjects_keyboard, tests_keyboard,
    answer_keyboard, start_test_keyboard, search_menu_keyboard, teachers_list_keyboard,
    student_results_subjects_keyboard,
    student_results_subject_view_keyboard, student_results_test_back_keyboard,
)
from states.states import StudentStates

logger = logging.getLogger(__name__)
router = Router()

_STUDENT_MENU_TEXTS = frozenset({
    i18n("menu_subjects", "uk"), i18n("menu_subjects", "en"),
    "📚 Предмети", "📚 Subjects", "Предмети", "Subjects",
    i18n("menu_enter_code", "uk"), i18n("menu_enter_code", "en"),
    "🔑 Ввести код", "🔑 Enter Code", "Ввести код", "Enter Code",
    i18n("menu_my_results", "uk"), i18n("menu_my_results", "en"),
    "Мої результати", "My Results",
    i18n("menu_search", "uk"), i18n("menu_search", "en"),
    "🔍 Пошук", "🔍 Search", "Пошук", "Search",
})


def _multiple_answer_keyboard(question_id: int, options: list[dict], selected_ids: list[int]) -> InlineKeyboardMarkup:
    """Keyboard for selecting multiple answers for a multiple choice question."""
    rows = []
    for opt in options:
        is_selected = opt["id"] in selected_ids
        prefix = "✅ " if is_selected else "⭕ "
        rows.append([InlineKeyboardButton(
            text=f"{prefix}{opt['text']}",
            callback_data=f"ans:{question_id}:{opt['id']}"
        )])
    # Add confirm button
    rows.append([InlineKeyboardButton(
        text="✓ Підтвердити",
        callback_data=f"mult_ans_confirm:{question_id}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _is_time_expired(expires_at: Optional[str]) -> bool:
    if not expires_at:
        return False
    try:
        ex = expires_at
        if ex.endswith("Z"):
            ex = ex[:-1] + "+00:00"
        return datetime.now(timezone.utc) >= datetime.fromisoformat(ex)
    except Exception:
        return False


async def _clear_taking_test_state(
    bot, storage: Optional[BaseStorage], telegram_user_id: int, chat_id: int,
) -> None:
    if not bot or not storage:
        return
    key = StorageKey(bot_id=bot.id, chat_id=chat_id, user_id=telegram_user_id)
    await storage.set_state(key=key, state=None)
    await storage.set_data(key=key, data={})


async def _abort_taking_test_if_over(
    message: Optional[Message],
    callback: Optional[CallbackQuery],
    state: FSMContext,
    *,
    notify: bool = True,
) -> bool:
    """If the attempt is finished or time is up, clear FSM. Returns True when test is over."""
    data = await state.get_data()
    session_id = data.get("session_id")
    if not session_id:
        await state.clear()
        return False

    session = await queries.get_session(session_id)
    lang = data.get("lang", "uk")
    total_q = len(data.get("questions", []))
    already_done = bool(session and session.get("completed_at"))
    expired = _is_time_expired(data.get("expires_at"))

    if not already_done and not expired:
        return False

    if not already_done and expired:
        await queries.complete_session_from_answers(session_id, total_q)

    await state.clear()
    if not notify:
        return True

    target = message if message else callback.message
    if callback:
        if already_done:
            await callback.answer(i18n("test_session_ended", lang), show_alert=True)
        else:
            await target.answer(i18n("time_up", lang), reply_markup=student_menu(lang))
            await callback.answer()
    else:
        text = i18n("test_session_ended", lang) if already_done else i18n("time_up", lang)
        await target.answer(text, reply_markup=student_menu(lang))
    return True


async def _route_student_menu(message: Message, state: FSMContext) -> None:
    """Dispatch reply-menu button while leaving taking_test state."""
    text = message.text.strip()
    if text in {
        i18n("menu_my_results", "uk"), i18n("menu_my_results", "en"),
        "Мої результати", "My Results",
    }:
        await my_results(message, state)
    elif text in {"📚 Предмети", "📚 Subjects", "Предмети", "Subjects"}:
        await browse_subjects(message, state)
    elif text in {
        "🔑 Ввести код", "🔑 Enter Code", "Ввести код", "Enter Code",
    }:
        await enter_code_prompt(message, state)
    elif text in {"🔍 Пошук", "🔍 Search", "Пошук", "Search"}:
        await search_tests(message, state)


async def _expiry_watcher(
    session_id: int,
    expires_iso: str,
    telegram_user_id: int,
    chat_id: int,
    bot,
    storage: Optional[BaseStorage],
) -> None:
    """Background task: on timeout complete session, clear FSM, notify student."""
    try:
        ex = expires_iso
        if ex.endswith("Z"):
            ex = ex[:-1] + "+00:00"
        exp_dt = datetime.fromisoformat(ex)
        wait = (exp_dt - datetime.now(timezone.utc)).total_seconds()
        if wait > 0:
            await asyncio.sleep(wait)

        session = await queries.get_session(session_id)
        if not session or session.get("completed_at"):
            return

        total = session.get("total_questions") or 0
        await queries.complete_session_from_answers(session_id, total)
        await _clear_taking_test_state(bot, storage, telegram_user_id, chat_id)

        user = await queries.get_user_by_id(session.get("student_id"))
        lang = user.get("language", "uk") if user else "uk"
        try:
            await bot.send_message(
                chat_id, i18n("time_up", lang), reply_markup=student_menu(lang),
            )
        except Exception:
            pass
    except Exception:
        logger.exception("Expiry watcher failed for session %s", session_id)

def _attempts_label(max_attempts: int, lang: str) -> str:
    if lang == "en":
        return "1 attempt" if max_attempts == 1 else f"{max_attempts} attempts"
    return "1 спроба" if max_attempts == 1 else f"{max_attempts} спроб"


def _format_result_points(earned: float, total: float) -> str:
    earned_s = queries.format_points_value(earned)
    total_s = queries.format_points_value(total)
    return f"*{earned_s} / {total_s}*"


async def _finish_test(message: Message, state: FSMContext, lang: str) -> None:
    """Complete session and send final result (supports fractional points)."""
    data = await state.get_data()
    session_id = data["session_id"]
    total = len(data["questions"])
    earned, scale, pct = await queries.complete_session_from_answers(session_id, total)
    await state.clear()

    bar = _progress_bar(pct)
    grade = _grade_i18n(pct, lang)
    title = data.get("test_title", "Тест")
    subject_name = data.get("subject_name", "—")
    result_line = _format_result_points(earned, scale)

    await message.answer(
        f"🏁 *Тест завершено!*\n\n"
        f"📝 *{title}*\n"
        f"📖 Предмет: {subject_name}\n"
        f"📊 Результат: {result_line} ({pct}%)\n"
        f"{bar}\n"
        f"{grade}\n\n"
        "📌 Перегляньте історію у меню *📈 Мої результати*.",
        reply_markup=student_menu(lang),
        parse_mode="Markdown",
    )


def _grade_i18n(pct: int, lang: str) -> str:
    if pct == 100:
        return i18n("grade_excellent", lang)
    elif pct >= 80:
        return i18n("grade_good", lang)
    elif pct >= 60:
        return i18n("grade_satisfactory", lang)
    elif pct >= 40:
        return i18n("grade_weak", lang)
    else:
        return i18n("grade_poor", lang)


async def _require_student(msg_or_cq) -> Optional[dict]:
    tid = msg_or_cq.from_user.id
    user = await queries.get_user(tid)
    if not user or user["role"] != "student":
        lang = user.get("language", "uk") if user else "uk"
        text = i18n("student_only", lang)
        if isinstance(msg_or_cq, CallbackQuery):
            await msg_or_cq.answer(text, show_alert=True)
        else:
            await msg_or_cq.answer(text)
        return None
    return user


# Browse subjects

@router.message(F.text.in_(["📚 Предмети", "📚 Subjects", "Предмети", "Subjects"]))
async def browse_subjects(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()
    subjects = await queries.get_subjects()

    if not subjects:
        await message.answer(i18n("no_public_tests", lang))
        return

    await message.answer(
        i18n("select_subject", lang),
        reply_markup=subjects_keyboard(subjects, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)


@router.callback_query(StudentStates.browsing_subjects, SubjectCallback.filter())
async def browse_tests(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subject = await queries.get_subject(callback_data.id)
    tests = await queries.get_public_tests_by_subject(callback_data.id)

    if not tests:
        await callback.answer(i18n("no_tests_in_subject", lang), show_alert=True)
        return

    await callback.message.edit_text(
        i18n("tests_in_subject", lang, subject=subject["name"], count=len(tests)),
        reply_markup=tests_keyboard(tests, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)
    await callback.answer()


@router.callback_query(StudentStates.browsing_tests, BackCallback.filter(F.data.endswith("subjects")))
@router.callback_query(StudentStates.browsing_subjects, BackCallback.filter())
async def back_to_subjects(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subjects = await queries.get_subjects()
    await callback.message.edit_text(
        i18n("select_subject", lang),
        reply_markup=subjects_keyboard(subjects, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)
    await callback.answer()


# Private test - access code

@router.message(F.text.in_(["🔑 Ввести код", "🔑 Enter Code", "Ввести код", "Enter Code"]))
async def enter_code_prompt(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()
    await message.answer(
        i18n("enter_code_prompt", lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.entering_access_code)


@router.message(StudentStates.entering_access_code, F.text)
async def process_access_code(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    code = message.text.strip().upper()
    test = await queries.get_test_by_code(code)

    if not test:
        await message.answer(i18n("code_not_found", lang))
        return

    q_count = await queries.get_question_count(test["id"])
    subject_name = test["subjects"]["name"] if test.get("subjects") else "—"
    teacher_name = test["users"]["name"] if test.get("users") else "—"

    await message.answer(
        i18n(
            "test_found",
            lang,
            title=test["title"],
            subject=subject_name,
            teacher=teacher_name,
            count=q_count,
            description=(i18n("test_found_description", lang, description=test["description"]) if test.get("description") else ""),
        ),
        reply_markup=start_test_keyboard(test["id"], lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)


# Test preview (from public list)

@router.callback_query(StudentStates.browsing_tests, TestCallback.filter(F.action == "preview"))
async def test_preview(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await _require_student(callback)
    if not user:
        return
    lang = user.get("language", "uk")

    test = await queries.get_test(callback_data.id)
    if not test:
        await callback.answer(i18n("test_not_found", lang), show_alert=True)
        return

    q_count = await queries.get_question_count(test["id"])
    teacher_name = test["users"]["name"] if test.get("users") else "—"

    # Build attempts info
    attempts_info = ""
    if test.get("max_attempts"):
        attempt_count = await queries.get_student_attempt_count(test["id"], user["id"])
        remaining = test["max_attempts"] - attempt_count
        attempts_text = i18n("attempts_left", lang, remaining=remaining, max=test["max_attempts"])
        if remaining <= 0:
            attempts_text = i18n("attempts_exhausted", lang, max=test["max_attempts"])
        attempts_info = f"{attempts_text}\n"
    else:
        attempts_info = i18n("attempts_unlimited_info", lang) + "\n"

    await callback.message.edit_text(
        i18n(
            "test_preview",
            lang,
            title=test["title"],
            teacher=teacher_name,
            count=q_count,
            attempts=attempts_info,
            description=(i18n("test_preview_description", lang, description=test["description"]) if test.get("description") else ""),
            confirm=i18n("test_start_confirm", lang),
        ),
        reply_markup=start_test_keyboard(test["id"], lang=lang),
        parse_mode="Markdown",
    )
    await callback.answer()


# Start test

@router.callback_query(TestCallback.filter(F.action == "start"))
async def start_test(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await _require_student(callback)
    if not user:
        return
    lang = user.get("language", "uk")

    test = await queries.get_test_with_questions(callback_data.id)
    if not test or not test.get("questions"):
        await callback.answer(i18n("test_no_questions", lang), show_alert=True)
        return

    # Check attempt limit
    if test.get("max_attempts"):
        attempt_count = await queries.get_student_attempt_count(test["id"], user["id"])
        if attempt_count >= test["max_attempts"]:
            attempts_text = _attempts_label(test["max_attempts"], lang)
            await callback.answer(
                i18n("attempts_all_used_alert", lang, attempts=attempts_text),
                show_alert=True
            )
            return

    # Compute expires_at for timed tests
    expires_at = None
    if test.get("time_limit_minutes") is not None:
        from datetime import datetime, timezone, timedelta

        try:
            minutes = int(test["time_limit_minutes"])
            expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            expires_at = expires.isoformat()
        except Exception:
            expires_at = None

    question_count = len(test["questions"])
    max_pts = float(test["max_points"]) if test.get("max_points") is not None else float(question_count)

    session = await queries.create_session(
        test["id"],
        user["id"],
        question_count,
        expires_at=expires_at,
        max_points=max_pts,
    )

    # Start background watcher to auto-complete and notify when time expires
    if expires_at:
        try:
            asyncio.create_task(_expiry_watcher(
                session["id"],
                expires_at,
                callback.from_user.id,
                callback.message.chat.id,
                callback.bot,
                state.storage,
            ))
        except Exception:
            logger.exception("Failed to start expiry watcher task")

    await state.set_state(StudentStates.taking_test)
    await state.update_data(
        test_id=test["id"],
        session_id=session["id"],
        expires_at=expires_at,
        test_title=test["title"],
        subject_name=test.get("subjects", {}).get("name", "—"),
        questions=test["questions"],
        current_index=0,
        score=0,
        show_answer_correctness=test.get("show_answer_correctness", False),
        lang=lang,
    )

    await callback.message.edit_text(
        i18n("test_started", lang, title=test["title"], count=len(test["questions"])),
        parse_mode="Markdown",
    )
    await _send_question(callback.message, state)
    await callback.answer()


async def _send_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]
    total = len(questions)
    question_type = q.get("question_type", QuestionType.SINGLE_CHOICE)

    if question_type == QuestionType.MULTIPLE_CHOICE:
        keyboard = _multiple_answer_keyboard(q["id"], q["options"], [])
        instruction = "\n\n📌 *Оберіть одну або кілька правильних відповідей, потім натисніть «Підтвердити»*"
    elif question_type == QuestionType.OPEN_ANSWER:
        keyboard = None
        instruction = i18n("open_answer_instruction", lang)
    else:
        keyboard = answer_keyboard(q["id"], q["options"])
        instruction = ""

    await message.answer(
        f"{i18n('question_counter', lang, current=idx + 1, total=total)}\n\n{q['text']}{instruction}",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.message(StudentStates.taking_test, F.text.in_(_STUDENT_MENU_TEXTS))
async def student_menu_during_test(message: Message, state: FSMContext) -> None:
    """Reply menu during a test (e.g. after time expired FSM was not cleared)."""
    await _abort_taking_test_if_over(message, None, state, notify=False)
    await state.clear()
    await _route_student_menu(message, state)


@router.message(StudentStates.taking_test, F.text)
async def handle_open_answer_text(message: Message, state: FSMContext) -> None:
    """Free-text answer for open-ended questions."""
    if await _abort_taking_test_if_over(message, None, state):
        return

    data = await state.get_data()
    lang = data.get("lang", "uk")
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]
    question_type = q.get("question_type", QuestionType.SINGLE_CHOICE)

    if question_type != QuestionType.OPEN_ANSWER:
        await message.answer(i18n("use_buttons_not_text", lang))
        return

    answer_text = message.text.strip()
    if not answer_text:
        await message.answer(i18n("open_answer_empty", lang))
        return

    is_correct = matches_open_answer(answer_text, q.get("options", []))
    await save_open_answer(data["session_id"], q["id"], answer_text, is_correct)

    show_answers = data.get("show_answer_correctness", False)
    if show_answers:
        if is_correct:
            feedback = i18n("correct_answer", lang)
        else:
            accepted = [o["text"] for o in q.get("options", []) if o.get("is_correct")]
            feedback = i18n("wrong_answer_open", lang, correct=", ".join(accepted) or "—")
    else:
        feedback = i18n("answer_saved", lang)

    await message.answer(feedback, parse_mode="Markdown")

    next_idx = idx + 1
    total = len(questions)
    if next_idx >= total:
        await _finish_test(message, state, lang)
    else:
        await state.update_data(current_index=next_idx)
        await _send_question(message, state)


# Answer question (single choice)

@router.callback_query(StudentStates.taking_test, F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
    if await _abort_taking_test_if_over(None, callback, state):
        return

    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    _, q_id_str, opt_id_str = callback.data.split(":")
    question_id = int(q_id_str)
    option_id = int(opt_id_str)

    data = await state.get_data()
    lang = data.get("lang", lang)
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]

    # Check if this is a multiple choice question
    question_type = q.get("question_type", QuestionType.SINGLE_CHOICE)
    if question_type == QuestionType.MULTIPLE_CHOICE:
        # Handle multiple selection
        selected_option_ids = data.get("selected_option_ids", [])
        if option_id in selected_option_ids:
            selected_option_ids.remove(option_id)
        else:
            selected_option_ids.append(option_id)
        await state.update_data(selected_option_ids=selected_option_ids)
        await callback.message.edit_reply_markup(
            reply_markup=_multiple_answer_keyboard(q["id"], q["options"], selected_option_ids)
        )
        await callback.answer()
        return

    # Single choice handling
    # Find selected option
    selected_opt = next((o for o in q["options"] if o["id"] == option_id), None)
    if not selected_opt:
        await callback.answer(i18n("answer_error", lang), show_alert=True)
        return

    is_correct = selected_opt["is_correct"]
    correct_opt = next((o for o in q["options"] if o["is_correct"]), None)
    score = data["score"] + (1 if is_correct else 0)

    await queries.save_answer(data["session_id"], question_id, option_id, is_correct)

    # Feedback to user (depends on show_answer_correctness setting)
    show_answers = data.get("show_answer_correctness", False)

    if show_answers:
        # Show immediate feedback with correct/incorrect info
        if is_correct:
            feedback = i18n("correct_answer", lang)
        else:
            correct_text = correct_opt["text"] if correct_opt else "—"
            feedback = i18n("wrong_answer", lang, correct=correct_text)
    else:
        # Hide correctness info, only confirm answer was saved
        feedback = i18n("answer_saved", lang)

    await callback.message.edit_reply_markup()  # remove buttons
    await callback.message.answer(feedback, parse_mode="Markdown")

    next_idx = idx + 1
    total = len(questions)

    if next_idx >= total:
        await _finish_test(callback.message, state, lang)
    else:
        await state.update_data(current_index=next_idx, score=score)
        await _send_question(callback.message, state)

    await callback.answer()


# Handle multiple answer confirmation

@router.callback_query(StudentStates.taking_test, F.data.startswith("mult_ans_confirm:"))
async def handle_multiple_answer_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    if await _abort_taking_test_if_over(None, callback, state):
        return

    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    _, q_id_str = callback.data.split(":")
    question_id = int(q_id_str)

    data = await state.get_data()
    lang = data.get("lang", lang)
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]
    selected_option_ids = data.get("selected_option_ids", [])

    if not selected_option_ids:
        await callback.answer(i18n("select_at_least_one", lang), show_alert=True)
        return

    # Save multiple answers
    await queries.save_multiple_answers(data["session_id"], question_id, selected_option_ids)

    question_score = await queries.get_question_score(data["session_id"], question_id)

    # Get correct options for feedback
    correct_opts = [o for o in q["options"] if o.get("is_correct")]
    correct_texts = ", ".join([o["text"] for o in correct_opts])

    # Feedback to user
    show_answers = data.get("show_answer_correctness", False)
    if show_answers:
        if question_score == 1.0:
            feedback = i18n("correct_answer", lang)
        elif question_score > 0:
            feedback = i18n("partial_correct", lang, score=int(question_score * 100))
        else:
            feedback = i18n("wrong_answer_multiple", lang, correct=correct_texts)
    else:
        feedback = i18n("answer_saved", lang)

    await callback.message.edit_reply_markup()
    await callback.message.answer(feedback, parse_mode="Markdown")

    next_idx = idx + 1
    total = len(questions)

    if next_idx >= total:
        await state.update_data(selected_option_ids=[])
        await _finish_test(callback.message, state, lang)
    else:
        await state.update_data(selected_option_ids=[], current_index=next_idx)
        await _send_question(callback.message, state)

    await callback.answer()


# My results

RESULTS_MAX_LINES = 15


@router.message(F.text.in_([
    i18n("menu_my_results", "uk"),
    i18n("menu_my_results", "en"),
    "Мої результати", "My Results",
]))
async def my_results(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()

    sessions = await queries.get_student_sessions(user["id"])
    if not sessions:
        await message.answer(i18n("no_results_student", lang))
        return

    subjects = _student_subject_stats(sessions)
    text, reply_markup = _student_results_reply(subjects, sessions, lang)

    await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    await state.set_state(StudentStates.viewing_my_results)
    await state.update_data(my_results_sessions=sessions)


@router.callback_query(StudentStates.viewing_my_results, StudentResultsCallback.filter())
async def my_results_callback(
    callback: CallbackQuery, callback_data: StudentResultsCallback, state: FSMContext,
) -> None:
    user = await _require_student(callback)
    if not user:
        return
    lang = user.get("language", "uk")

    data = await state.get_data()
    sessions = data.get("my_results_sessions")
    if not sessions:
        sessions = await queries.get_student_sessions(user["id"])
        await state.update_data(my_results_sessions=sessions)

    if not sessions:
        await callback.message.edit_text(i18n("no_results_student", lang))
        await state.clear()
        await callback.answer()
        return

    subjects = _student_subject_stats(sessions)
    single_subject = len(subjects) == 1

    if callback_data.action == "test" and callback_data.id:
        subject_id = callback_data.sub
        if subject_id:
            scope = _sessions_for_subject(sessions, subject_id)
        else:
            scope = sessions
        test_sessions = [s for s in scope if s.get("test_id") == callback_data.id]
        if not test_sessions:
            await callback.answer(i18n("test_not_found", lang), show_alert=True)
            return
        if not subject_id:
            test = test_sessions[0].get("tests") or {}
            subject_id = test.get("subject_id") or (test.get("subjects") or {}).get("id", 0)
        title = (test_sessions[0].get("tests") or {}).get("title", "—")
        await callback.message.edit_text(
            _format_student_test_detail(title, test_sessions, lang),
            reply_markup=student_results_test_back_keyboard(
                subject_id, lang, single_subject=single_subject,
            ),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    if callback_data.action == "subject" and callback_data.id:
        text, keyboard = _student_subject_reply(
            subjects, sessions, callback_data.id, lang,
            show_overview_back=not single_subject,
        )
        if not text:
            await callback.answer(i18n("subject_not_found", lang), show_alert=True)
            return
        await callback.message.edit_text(
            text, reply_markup=keyboard, parse_mode="Markdown",
        )
        await callback.answer()
        return

    text, reply_markup = _student_results_reply(subjects, sessions, lang)
    await callback.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="Markdown",
    )
    await callback.answer()


# Helpers

def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)


def _grade(pct: int) -> str:
    # Backwards-compatible fallback for older call sites.
    return _grade_i18n(pct, "uk")


def _format_date(dt: str | None) -> str:
    if not dt:
        return "—"
    try:
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        date_obj = datetime.fromisoformat(dt)
        return date_obj.strftime("%d.%m.%Y")
    except Exception:
        return dt


def _format_student_attempt_line(session: dict, lang: str, *, show_title: bool = True) -> str:
    pct = round(session.get("percentage", 0))
    score = queries.format_points_value(session.get("score", 0))
    total = queries.format_points_value(queries.session_points_total(session))
    date = _format_date(session.get("completed_at"))
    if show_title:
        return i18n(
            "results_student_line", lang,
            title=session.get("tests", {}).get("title", "—"),
            pct=pct, score=score, total=total, date=date,
        )
    return i18n(
        "results_student_attempt_line", lang,
        pct=pct, score=score, total=total, date=date,
    )


def _best_session(sessions: list[dict]) -> dict:
    return max(
        sessions,
        key=lambda s: (
            s.get("percentage", 0),
            s.get("score", 0),
            s.get("completed_at") or "",
        ),
    )


def _group_sessions_by_test(sessions: list[dict]) -> list[dict]:
    """One entry per test with best session and all attempts."""
    by_test: dict[int, list[dict]] = {}
    for session in sessions:
        test_id = session.get("test_id")
        if test_id is None:
            continue
        by_test.setdefault(test_id, []).append(session)

    tests = []
    for test_id, test_sessions in by_test.items():
        best = _best_session(test_sessions)
        title = (best.get("tests") or {}).get("title", "—")
        tests.append({
            "test_id": test_id,
            "title": title,
            "best_session": best,
            "best_percentage": best.get("percentage", 0),
            "attempts": sorted(
                test_sessions,
                key=lambda s: s.get("completed_at") or "",
                reverse=True,
            ),
        })
    return sorted(tests, key=lambda t: t["title"].casefold())


def _student_subject_stats(sessions: list[dict]) -> list[dict]:
    """Group student sessions by subject with average score and counts."""
    by_subject: dict[int, dict] = {}
    for session in sessions:
        test = session.get("tests") or {}
        subj = test.get("subjects") or {}
        subject_id = test.get("subject_id") or subj.get("id")
        if subject_id is None:
            continue
        if subject_id not in by_subject:
            by_subject[subject_id] = {
                "subject_id": subject_id,
                "subject_name": subj.get("name", "—"),
                "sessions": [],
            }
        by_subject[subject_id]["sessions"].append(session)

    result = []
    for item in by_subject.values():
        subject_sessions = item["sessions"]
        avg = round(
            sum(round(s.get("percentage", 0)) for s in subject_sessions) / len(subject_sessions),
            1,
        )
        result.append({
            "subject_id": item["subject_id"],
            "subject_name": item["subject_name"],
            "sessions": subject_sessions,
            "total_sessions": len(subject_sessions),
            "test_count": len({s.get("test_id") for s in subject_sessions}),
            "average_score": avg,
        })
    return sorted(result, key=lambda x: x["subject_name"].casefold())


def _sessions_for_subject(sessions: list[dict], subject_id: int) -> list[dict]:
    return [
        s for s in sessions
        if ((s.get("tests") or {}).get("subject_id") or (s.get("tests") or {}).get("subjects", {}).get("id"))
        == subject_id
    ]


def _format_student_results_overview(
    sessions: list[dict], subjects: list[dict], lang: str,
) -> str:
    total = len(sessions)
    avg_pct = round(sum(round(s.get("percentage", 0)) for s in sessions) / total)
    lines = [
        i18n("results_student_title", lang),
        i18n(
            "results_student_overview", lang,
            bar=_progress_bar(avg_pct),
            avg=f"{avg_pct}%",
            count=total,
            subjects=len(subjects),
        ),
    ]
    if len(subjects) > 1:
        lines.extend(["", i18n("results_student_pick_subject", lang)])
    return "\n".join(lines)


def _format_student_subject_detail(
    subject: dict, sessions: list[dict], lang: str, *, max_lines: int = RESULTS_MAX_LINES,
) -> str:
    tests = _group_sessions_by_test(sessions)
    avg = int(round(subject["average_score"]))
    lines = [
        i18n("results_student_subject_title", lang, name=subject["subject_name"]),
        i18n(
            "results_student_subject_result", lang,
            bar=_progress_bar(avg),
            avg=f"{subject['average_score']}%",
            attempts=subject["total_sessions"],
            tests=subject["test_count"],
        ),
        "",
        i18n("results_student_tests_header", lang),
    ]
    for test in tests[:max_lines]:
        lines.append(_format_student_attempt_line(test["best_session"], lang))
    if len(tests) > max_lines:
        lines.append(i18n("results_student_more", lang, count=len(tests) - max_lines))
    return "\n".join(lines)


def _format_student_test_detail(
    title: str, sessions: list[dict], lang: str, *, max_lines: int = RESULTS_MAX_LINES,
) -> str:
    best = _best_session(sessions)
    lines = [
        i18n("results_student_test_title", lang, title=title),
        i18n(
            "results_student_test_best", lang,
            pct=round(best.get("percentage", 0)),
            score=queries.format_points_value(best.get("score", 0)),
            total=queries.format_points_value(queries.session_points_total(best)),
        ),
        "",
        i18n("results_student_attempts_header", lang),
    ]
    sorted_sessions = sorted(
        sessions, key=lambda s: s.get("completed_at") or "", reverse=True,
    )
    for session in sorted_sessions[:max_lines]:
        lines.append(_format_student_attempt_line(session, lang, show_title=False))
    if len(sorted_sessions) > max_lines:
        lines.append(i18n("results_student_more", lang, count=len(sorted_sessions) - max_lines))
    return "\n".join(lines)


def _student_subject_reply(
    subjects: list[dict],
    sessions: list[dict],
    subject_id: int,
    lang: str,
    *,
    show_overview_back: bool,
) -> tuple[str | None, InlineKeyboardMarkup | None]:
    subj = next((s for s in subjects if s["subject_id"] == subject_id), None)
    if not subj:
        return None, None
    subject_sessions = _sessions_for_subject(sessions, subject_id)
    tests = _group_sessions_by_test(subject_sessions)
    text = _format_student_subject_detail(subj, subject_sessions, lang)
    show_test_buttons = len(tests) > 0
    keyboard = student_results_subject_view_keyboard(
        tests, subject_id, lang,
        show_test_buttons=show_test_buttons,
        show_overview_back=show_overview_back,
    )
    return text, keyboard


def _student_results_reply(
    subjects: list[dict], sessions: list[dict], lang: str,
) -> tuple[str, InlineKeyboardMarkup | None]:
    if len(subjects) == 1:
        return _student_subject_reply(
            subjects, sessions, subjects[0]["subject_id"], lang,
            show_overview_back=False,
        )
    return (
        _format_student_results_overview(sessions, subjects, lang),
        student_results_subjects_keyboard(subjects),
    )


# Search and filter

@router.message(F.text.in_(["🔍 Пошук", "🔍 Search", "Пошук", "Search"]))
async def search_tests(message: Message, state: FSMContext) -> None:
    """Open search menu."""
    user = await _require_student(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()
    
    await message.answer(
        i18n("search_title", lang),
        reply_markup=search_menu_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_name"))
async def search_by_name_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Ask for search query."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await callback.message.edit_text(
        i18n("search_by_name_prompt", lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_by_name)
    await callback.answer()


@router.message(StudentStates.searching_by_name, F.text)
async def search_by_name(message: Message, state: FSMContext) -> None:
    """Search tests by name."""
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    query = message.text.strip()
    if len(query) < 2:
        await message.answer(i18n("search_query_too_short", lang))
        return
    
    tests = await queries.search_tests_by_name(query)
    
    if not tests:
        await message.answer(
            i18n("search_not_found", lang, query=query),
            parse_mode="Markdown",
        )
        return
    
    await message.answer(
        i18n("search_results", lang, query=query, count=len(tests)),
        reply_markup=tests_keyboard(tests, lang=lang),
        parse_mode="Markdown",
        )
    await state.set_state(StudentStates.browsing_tests)


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_subject"))
async def search_by_subject(callback: CallbackQuery, state: FSMContext) -> None:
    """Show subjects for filtering."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subjects = await queries.get_subjects()
    
    if not subjects:
        await callback.answer(i18n("no_subjects_yet", lang), show_alert=True)
        return
    
    await callback.message.edit_text(
        i18n("select_subject", lang),
        reply_markup=subjects_keyboard(subjects, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.filtering_by_subject)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_subject, SubjectCallback.filter())
async def show_tests_by_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    """Show tests for selected subject."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subject = await queries.get_subject(callback_data.id)
    tests = await queries.get_public_tests_by_subject(callback_data.id)
    
    if not tests:
        await callback.answer(i18n("no_tests_in_subject", lang), show_alert=True)
        return
    
    await callback.message.edit_text(
        i18n("tests_in_subject", lang, subject=subject["name"], count=len(tests)),
        reply_markup=tests_keyboard(tests, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)
    await callback.answer()


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_teacher"))
async def search_by_teacher_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Show list of teachers."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    teachers = await queries.get_all_teachers()
    
    if not teachers:
        await callback.answer(i18n("no_teachers_yet", lang), show_alert=True)
        return
    
    await callback.message.edit_text(
        i18n("select_teacher", lang),
        reply_markup=teachers_list_keyboard(teachers, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.filtering_by_teacher)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_teacher, TeacherFilterCallback.filter())
async def show_tests_by_teacher(callback: CallbackQuery, callback_data: TeacherFilterCallback, state: FSMContext) -> None:
    """Show tests for selected teacher."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    teacher = await queries.get_user_by_id(callback_data.id)
    if not teacher:
        await callback.answer(i18n("teacher_not_found", lang), show_alert=True)
        return

    tests = await queries.get_tests_by_teacher(callback_data.id)
    
    if not tests:
        await callback.answer(i18n("no_tests_for_teacher", lang, name=teacher["name"]), show_alert=True)
        return
    
    await callback.message.edit_text(
        i18n("teacher_tests_title", lang, name=teacher["name"], count=len(tests)),
        reply_markup=tests_keyboard(tests, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)
    await callback.answer()


# Handle Back button during search

@router.callback_query(StudentStates.searching_tests, BackCallback.filter())
async def back_from_search_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to student menu from search menu."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    
    await callback.message.edit_text(
        i18n("student_menu_title", lang),
        reply_markup=student_menu(lang),
        parse_mode="Markdown",
    )
    await state.clear()
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_subject, BackCallback.filter())
async def back_from_subject_filter(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to search menu from subject filter."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await callback.message.edit_text(
        i18n("search_title", lang),
        reply_markup=search_menu_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_teacher, BackCallback.filter())
async def back_from_teacher_filter(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to search menu from teacher filter."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    await callback.message.edit_text(
        i18n("search_title", lang),
        reply_markup=search_menu_keyboard(lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)
    await callback.answer()


@router.callback_query(StudentStates.browsing_tests, BackCallback.filter())
async def back_from_test_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to subjects from test selection."""
    user = await queries.get_user(callback.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    subjects = await queries.get_subjects()
    await callback.message.edit_text(
        i18n("select_subject", lang),
        reply_markup=subjects_keyboard(subjects, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)
    await callback.answer()
