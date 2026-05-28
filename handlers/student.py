"""
Student handlers - browse subjects, take tests, view results.
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from db import queries
from db.queries import QuestionType
from config.i18n import i18n
from keyboards.callbacks import SubjectCallback, TestCallback, BackCallback, SearchCallback, TeacherFilterCallback
from keyboards.keyboards import (
    student_menu, subjects_keyboard, tests_keyboard,
    answer_keyboard, start_test_keyboard, search_menu_keyboard, teachers_list_keyboard,
)
from states.states import StudentStates

logger = logging.getLogger(__name__)
router = Router()


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


async def _expiry_watcher(session_id: int, expires_iso: str, chat_id: int, bot) -> None:
    """Background task that waits until expires_iso, then completes session if not finished and notifies student."""
    try:
        from datetime import datetime, timezone

        ex = expires_iso
        if ex.endswith("Z"):
            ex = ex[:-1] + "+00:00"
        exp_dt = datetime.fromisoformat(ex)
        now = datetime.now(timezone.utc)
        wait = (exp_dt - now).total_seconds()
        if wait > 0:
            await asyncio.sleep(wait)

        # Re-check session status
        session = await queries.get_session(session_id)
        if not session:
            return
        if session.get("completed_at"):
            return

        # Compute current score and finalize
        score = await queries.get_session_score(session_id)
        total = session.get("total_questions") or 0
        pct = round(score / total * 100) if total > 0 else 0
        await queries.complete_session(session_id, score, pct)

        # Notify student
        user = await queries.get_user(session.get("student_id"))
        lang = user.get("language", "uk") if user else "uk"
        try:
            await bot.send_message(chat_id, i18n("time_up", lang))
        except Exception:
            # best-effort notify
            pass
    except Exception:
        return

def _attempts_label(max_attempts: int, lang: str) -> str:
    if lang == "en":
        return "1 attempt" if max_attempts == 1 else f"{max_attempts} attempts"
    return "1 спроба" if max_attempts == 1 else f"{max_attempts} спроб"


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
    subjects = await queries.get_subjects(message.from_user.id)

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
    tests = await queries.get_public_tests_by_subject(callback_data.id, callback.from_user.id)

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
    subjects = await queries.get_subjects(callback.from_user.id)
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
    test = await queries.get_test_by_code(code, message.from_user.id)

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

    test = await queries.get_test(callback_data.id, callback.from_user.id)
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

    test = await queries.get_test_with_questions(callback_data.id, callback.from_user.id)
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

    session = await queries.create_session(test["id"], user["id"], len(test["questions"]), expires_at=expires_at)

    # Start background watcher to auto-complete and notify when time expires
    if expires_at:
        try:
            asyncio.create_task(_expiry_watcher(session["id"], expires_at, callback.from_user.id, callback.bot))
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

    # Show different keyboard for multiple choice questions
    if question_type == QuestionType.MULTIPLE_CHOICE:
        keyboard = _multiple_answer_keyboard(q["id"], q["options"], [])
        instruction = "\n\n📌 *Оберіть одну або кілька правильних відповідей, потім натисніть «Підтвердити»*"
    else:
        keyboard = answer_keyboard(q["id"], q["options"])
        instruction = ""

    await message.answer(
        f"{i18n('question_counter', lang, current=idx + 1, total=total)}\n\n{q['text']}{instruction}",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


# Answer question (single choice)

@router.callback_query(StudentStates.taking_test, F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
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
    # Check if session expired
    expires_at = data.get("expires_at")
    if expires_at:
        try:
            from datetime import datetime, timezone

            ex = expires_at
            if ex.endswith("Z"):
                ex = ex[:-1] + "+00:00"
            exp_dt = datetime.fromisoformat(ex)
            now = datetime.now(timezone.utc)
            if now >= exp_dt:
                # finalize session as expired
                score_so_far = data.get("score", 0)
                total_q = len(questions)
                pct = round(score_so_far / total_q * 100) if total_q > 0 else 0
                await queries.complete_session(data["session_id"], score_so_far, pct)
                await state.clear()
                await callback.message.answer(i18n("time_up", lang), reply_markup=student_menu(lang))
                await callback.answer()
                return
        except Exception:
            # If parsing fails, ignore and continue
            pass

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
        # Test finished
        pct = round(score / total * 100)
        await queries.complete_session(data["session_id"], score, pct)
        await state.clear()
        bar = _progress_bar(pct)
        grade = _grade_i18n(pct, lang)
        title = data.get("test_title", "Тест")
        subject_name = data.get("subject_name", "—")

        await callback.message.answer(
            f"🏁 *Тест завершено!*\n\n"
            f"📝 *{title}*\n"
            f"📖 Предмет: {subject_name}\n"
            f"📊 Результат: *{score} / {total}* ({pct}%)\n"
            f"{bar}\n"
            f"{grade}\n\n"
            "📌 Перегляньте історію у меню *📈 Мої результати*.",
            reply_markup=student_menu(lang),
            parse_mode="Markdown",
        )
    else:
        await state.update_data(current_index=next_idx, score=score)
        await _send_question(callback.message, state)

    await callback.answer()


# Handle multiple answer confirmation

@router.callback_query(StudentStates.taking_test, F.data.startswith("mult_ans_confirm:"))
async def handle_multiple_answer_confirm(callback: CallbackQuery, state: FSMContext) -> None:
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

    # Check if session expired
    expires_at = data.get("expires_at")
    if expires_at:
        try:
            from datetime import datetime, timezone

            ex = expires_at
            if ex.endswith("Z"):
                ex = ex[:-1] + "+00:00"
            exp_dt = datetime.fromisoformat(ex)
            now = datetime.now(timezone.utc)
            if now >= exp_dt:
                # finalize session as expired
                score_so_far = data.get("score", 0)
                total_q = len(questions)
                pct = round(score_so_far / total_q * 100) if total_q > 0 else 0
                await queries.complete_session(data["session_id"], score_so_far, pct)
                await state.clear()
                await callback.message.answer(i18n("time_up", lang), reply_markup=student_menu(lang))
                await callback.answer()
                return
        except Exception:
            pass

    # Save multiple answers
    await queries.save_multiple_answers(data["session_id"], question_id, selected_option_ids)

    # Calculate partial credit
    question_score = await queries.get_question_score(data["session_id"], question_id)
    score = data["score"] + question_score

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

    # Clear selected options
    await state.update_data(selected_option_ids=[], current_index=idx + 1, score=score)

    next_idx = idx + 1
    total = len(questions)

    if next_idx >= total:
        # Test finished
        pct = round(score / total * 100)
        await queries.complete_session(data["session_id"], score, pct)
        await state.clear()
        bar = _progress_bar(pct)
        grade = _grade_i18n(pct, lang)
        title = data.get("test_title", "Тест")
        subject_name = data.get("subject_name", "—")

        await callback.message.answer(
            f"🏁 *Тест завершено!*\n\n"
            f"📝 *{title}*\n"
            f"📖 Предмет: {subject_name}\n"
            f"📊 Результат: *{score} / {total}* ({pct}%)\n"
            f"{bar}\n"
            f"{grade}\n\n"
            "📌 Перегляньте історію у меню *📈 Мої результати*.",
            reply_markup=student_menu(lang),
            parse_mode="Markdown",
        )
    else:
        await _send_question(callback.message, state)

    await callback.answer()


# My results

@router.message(F.text.in_(["📈 Мої результати", "📈 My Results", "Мої результати", "My Results"]))
async def my_results(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    lang = user.get("language", "uk")
    await state.clear()

    sessions = await queries.get_student_sessions(user["id"], message.from_user.id)

    if not sessions:
        await message.answer(i18n("no_results_student", lang))
        return

    text = _student_results_summary(sessions)
    await message.answer(text, parse_mode="Markdown")


# Helpers

def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)


def _grade(pct: int) -> str:
    # Backwards-compatible fallback for older call sites.
    return _grade_i18n(pct, "uk")


def _grade_short(pct: int) -> str:
    if pct >= 80:
        return "✅ Успішно"
    if pct >= 60:
        return "⚠️ Добре"
    return "❌ Потрібно повторити"


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


def _student_results_summary(sessions: list[dict]) -> str:
    total = len(sessions)
    avg_pct = round(sum(round(s.get("percentage", 0)) for s in sessions) / total)
    best = max(sessions, key=lambda s: round(s.get("percentage", 0)))
    latest = sessions[0]
    subjects = {
        s.get("tests", {}).get("subjects", {}).get("name", "—")
        for s in sessions if s.get("tests")
    }
    subject_count = len(subjects)

    lines = [
        "📈 *Ваші результати*",
        f"   • Тестів: {total}",
        f"   • Середній бал: {avg_pct}%",
        f"   • Кращий результат: *{best.get('tests', {}).get('title', '—')}* ({round(best.get('percentage', 0))}%)",
        f"   • Останній тест: *{latest.get('tests', {}).get('title', '—')}* ({round(latest.get('percentage', 0))}%)",
        f"   • Предметів: {subject_count}",
        "",
    ]

    for s in sessions:
        pct = round(s.get("percentage", 0))
        bar = _progress_bar(pct, length=8)
        title = s.get("tests", {}).get("title", "—")
        subject_name = s.get("tests", {}).get("subjects", {}).get("name", "—")
        date = _format_date(s.get("completed_at"))
        status = _grade_short(pct)
        lines.extend([
            f"*{title}* [{subject_name}]",
            f"   {bar} {pct}% ({s.get('score', 0)}/{s.get('total_questions', 0)})",
            f"   {date} · {status}",
            "",
        ])

    return "\n".join(lines)


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
    tests = await queries.get_public_tests_by_subject(callback_data.id, callback.from_user.id)
    
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
    teacher = await queries.get_user(callback_data.id)
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
    subjects = await queries.get_subjects(callback.from_user.id)
    await callback.message.edit_text(
        i18n("select_subject", lang),
        reply_markup=subjects_keyboard(subjects, lang=lang),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)
    await callback.answer()
