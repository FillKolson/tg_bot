"""
Student handlers - browse subjects, take tests, view results.
"""
import logging
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import queries
from keyboards.callbacks import SubjectCallback, TestCallback, BackCallback, SearchCallback, TeacherFilterCallback
from keyboards.keyboards import (
    student_menu, subjects_keyboard, tests_keyboard,
    answer_keyboard, start_test_keyboard, search_menu_keyboard, teachers_list_keyboard,
)
from states.states import StudentStates

logger = logging.getLogger(__name__)
router = Router()


async def _require_student(msg_or_cq) -> Optional[dict]:
    tid = msg_or_cq.from_user.id
    user = await queries.get_user(tid)
    if not user or user["role"] != "student":
        text = "⛔ Ця функція доступна лише для студентів."
        if isinstance(msg_or_cq, CallbackQuery):
            await msg_or_cq.answer(text, show_alert=True)
        else:
            await msg_or_cq.answer(text)
        return None
    return user


# Browse subjects

@router.message(F.text == "📚 Предмети")
async def browse_subjects(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    await state.clear()
    subjects = await queries.get_subjects(message.from_user.id)

    if not subjects:
        await message.answer("😔 Публічних предметів ще немає.\nСпробуйте ввести код приватного тесту через 🔑.")
        return

    await message.answer(
        "📚 *Оберіть предмет:*",
        reply_markup=subjects_keyboard(subjects),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)


@router.callback_query(StudentStates.browsing_subjects, SubjectCallback.filter())
async def browse_tests(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    subject = await queries.get_subject(callback_data.id)
    tests = await queries.get_public_tests_by_subject(callback_data.id, callback.from_user.id)

    if not tests:
        await callback.answer("😔 У цьому предметі ще немає публічних тестів.", show_alert=True)
        return

    await callback.message.edit_text(
        f"📖 *{subject['name']}* — тести ({len(tests)}):",
        reply_markup=tests_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)
    await callback.answer()


@router.callback_query(StudentStates.browsing_tests, BackCallback.filter(F.data.endswith("subjects")))
@router.callback_query(StudentStates.browsing_subjects, BackCallback.filter())
async def back_to_subjects(callback: CallbackQuery, state: FSMContext) -> None:
    subjects = await queries.get_subjects(callback.from_user.id)
    await callback.message.edit_text(
        "📚 *Оберіть предмет:*",
        reply_markup=subjects_keyboard(subjects),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)
    await callback.answer()


# Private test - access code

@router.message(F.text == "🔑 Ввести код")
async def enter_code_prompt(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    await state.clear()
    await message.answer(
        "🔑 Введіть код доступу до приватного тесту:\n\n"
        "_/cancel — скасувати_",
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.entering_access_code)


@router.message(StudentStates.entering_access_code, F.text)
async def process_access_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip().upper()
    test = await queries.get_test_by_code(code, message.from_user.id)

    if not test:
        await message.answer("❌ Тест із таким кодом не знайдено. Перевірте код та спробуйте ще раз:")
        return

    q_count = await queries.get_question_count(test["id"])
    subject_name = test["subjects"]["name"] if test.get("subjects") else "—"
    teacher_name = test["users"]["name"] if test.get("users") else "—"

    await message.answer(
        f"✅ Знайдено тест:\n\n"
        f"📝 *{test['title']}*\n"
        f"📖 Предмет: {subject_name}\n"
        f"👨‍🏫 Вчитель: {teacher_name}\n"
        f"❓ Питань: {q_count}\n"
        + (f"📄 {test['description']}\n" if test.get("description") else ""),
        reply_markup=start_test_keyboard(test["id"]),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)


# Test preview (from public list)

@router.callback_query(StudentStates.browsing_tests, TestCallback.filter(F.action == "preview"))
async def test_preview(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await _require_student(callback)
    if not user:
        return

    test = await queries.get_test(callback_data.id, callback.from_user.id)
    if not test:
        await callback.answer("⚠️ Тест не знайдено.", show_alert=True)
        return

    q_count = await queries.get_question_count(test["id"])
    teacher_name = test["users"]["name"] if test.get("users") else "—"

    # Build attempts info
    attempts_info = ""
    if test.get("max_attempts"):
        attempt_count = await queries.get_student_attempt_count(test["id"], user["id"])
        remaining = test["max_attempts"] - attempt_count
        attempts_text = f"Спроб залишилось: {remaining}/{test['max_attempts']}"
        if remaining <= 0:
            attempts_text = f"❌ Спроби вичерпані ({test['max_attempts']}/{test['max_attempts']})"
        else:
            attempts_text = f"⏱️ {attempts_text}"
        attempts_info = f"{attempts_text}\n"
    else:
        attempts_info = "♾️ Спроби: необмежено\n"

    await callback.message.edit_text(
        f"📝 *{test['title']}*\n"
        f"👨‍🏫 Вчитель: {teacher_name}\n"
        f"❓ Питань: {q_count}\n"
        f"{attempts_info}"
        + (f"📄 {test['description']}\n" if test.get("description") else "")
        + "\nНатисніть *▶️ Розпочати тест*, коли будете готові.",
        reply_markup=start_test_keyboard(test["id"]),
        parse_mode="Markdown",
    )
    await callback.answer()


# Start test

@router.callback_query(TestCallback.filter(F.action == "start"))
async def start_test(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await _require_student(callback)
    if not user:
        return

    test = await queries.get_test_with_questions(callback_data.id, callback.from_user.id)
    if not test or not test.get("questions"):
        await callback.answer("⚠️ У цьому тесті немає питань.", show_alert=True)
        return

    # Check attempt limit
    if test.get("max_attempts"):
        attempt_count = await queries.get_student_attempt_count(test["id"], user["id"])
        if attempt_count >= test["max_attempts"]:
            attempts_text = "1 спроба" if test["max_attempts"] == 1 else f"{test['max_attempts']} спроб"
            await callback.answer(
                f"❌ Ви вичерпали всі спроби ({attempts_text}) для цього тесту.",
                show_alert=True
            )
            return

    session = await queries.create_session(test["id"], user["id"], len(test["questions"]))

    await state.set_state(StudentStates.taking_test)
    await state.update_data(
        test_id=test["id"],
        session_id=session["id"],
        questions=test["questions"],
        current_index=0,
        score=0,
        show_answer_correctness=test.get("show_answer_correctness", False),
    )

    await callback.message.edit_text(
        f"🚀 *{test['title']}* розпочато!\n"
        f"❓ Всього питань: {len(test['questions'])}\n\n"
        "Відповідайте на питання нижче:",
        parse_mode="Markdown",
    )
    await _send_question(callback.message, state)
    await callback.answer()


async def _send_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]
    total = len(questions)

    await message.answer(
        f"*Питання {idx + 1} / {total}*\n\n{q['text']}",
        reply_markup=answer_keyboard(q["id"], q["options"]),
        parse_mode="Markdown",
    )


# Answer question

@router.callback_query(StudentStates.taking_test, F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
    _, q_id_str, opt_id_str = callback.data.split(":")
    question_id = int(q_id_str)
    option_id = int(opt_id_str)

    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_index"]
    q = questions[idx]

    # Find selected option
    selected_opt = next((o for o in q["options"] if o["id"] == option_id), None)
    if not selected_opt:
        await callback.answer("⚠️ Помилка вибору. Спробуйте ще раз.", show_alert=True)
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
            feedback = "✅ *Правильно!*"
        else:
            correct_text = correct_opt["text"] if correct_opt else "—"
            feedback = f"❌ *Неправильно.*\nПравильна відповідь: _{correct_text}_"
    else:
        # Hide correctness info, only confirm answer was saved
        feedback = "✅ Відповідь збережено"

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
        grade = _grade(pct)

        await callback.message.answer(
            f"🏁 *Тест завершено!*\n\n"
            f"📊 Результат: *{score} / {total}* ({pct}%)\n"
            f"{bar}\n"
            f"{grade}\n\n"
            "Повернення до меню:",
            reply_markup=student_menu(),
            parse_mode="Markdown",
        )
    else:
        await state.update_data(current_index=next_idx, score=score)
        await _send_question(callback.message, state)

    await callback.answer()


# My results

@router.message(F.text == "📈 Мої результати")
async def my_results(message: Message, state: FSMContext) -> None:
    user = await _require_student(message)
    if not user:
        return
    await state.clear()

    sessions = await queries.get_student_sessions(user["id"], message.from_user.id)

    if not sessions:
        await message.answer("📭 Ви ще не проходили жодного тесту.")
        return

    lines = [f"📈 *Ваші результати* ({len(sessions)} тестів):\n"]
    for s in sessions:
        pct = round(s.get("percentage", 0))
        bar = _progress_bar(pct, length=8)
        title = s["tests"]["title"] if s.get("tests") else "—"
        subj = ""
        if s.get("tests") and s["tests"].get("subjects"):
            subj = f" [{s['tests']['subjects']['name']}]"
        lines.append(
            f"📝 *{title}*{subj}\n"
            f"   {bar} {pct}% ({s['score']}/{s['total_questions']})\n"
        )

    await message.answer("\n".join(lines), parse_mode="Markdown")


# Helpers

def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)


def _grade(pct: int) -> str:
    if pct == 100:
        return "🏆 Відмінно! Бездоганний результат!"
    elif pct >= 80:
        return "🥇 Добре! Ви добре знаєте матеріал."
    elif pct >= 60:
        return "🥈 Задовільно. Є що покращити."
    elif pct >= 40:
        return "🥉 Слабо. Варто повторити тему."
    else:
        return "📚 Потрібно більше вчитись."


# Search and filter

@router.message(F.text == "🔍 Пошук")
async def search_tests(message: Message, state: FSMContext) -> None:
    """Open search menu."""
    user = await _require_student(message)
    if not user:
        return
    await state.clear()
    
    await message.answer(
        "🔍 *Пошук тестів*\n\n"
        "Оберіть як шукати:",
        reply_markup=search_menu_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_name"))
async def search_by_name_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Ask for search query."""
    await callback.message.edit_text(
        "🔍 Введіть назву тесту для пошуку:",
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_by_name)
    await callback.answer()


@router.message(StudentStates.searching_by_name, F.text)
async def search_by_name(message: Message, state: FSMContext) -> None:
    """Search tests by name."""
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("⚠️ Запит занадто короткий (мін. 2 символи):")
        return
    
    tests = await queries.search_tests_by_name(query)
    
    if not tests:
        await message.answer(
            f"😔 Тестів з назвою *{query}* не знайдено.",
            parse_mode="Markdown",
        )
        return
    
    await message.answer(
        f"🔍 *Результати пошуку за \"{query}\"* ({len(tests)}):",
        reply_markup=tests_keyboard(tests),
        parse_mode="Markdown",
        )
    await state.set_state(StudentStates.browsing_tests)


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_subject"))
async def search_by_subject(callback: CallbackQuery, state: FSMContext) -> None:
    """Show subjects for filtering."""
    subjects = await queries.get_subjects()
    
    if not subjects:
        await callback.answer("😔 Предметів ще немає.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📖 *Оберіть предмет:*",
        reply_markup=subjects_keyboard(subjects),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.filtering_by_subject)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_subject, SubjectCallback.filter())
async def show_tests_by_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    """Show tests for selected subject."""
    subject = await queries.get_subject(callback_data.id)
    tests = await queries.get_public_tests_by_subject(callback_data.id, callback.from_user.id)
    
    if not tests:
        await callback.answer("😔 У цьому предметі ще немає публічних тестів.", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"📖 *{subject['name']}* — тести ({len(tests)}):",
        reply_markup=tests_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_tests)
    await callback.answer()


@router.callback_query(StudentStates.searching_tests, SearchCallback.filter(F.action == "by_teacher"))
async def search_by_teacher_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Show list of teachers."""
    teachers = await queries.get_all_teachers()
    
    if not teachers:
        await callback.answer("😔 Вчителів ще немає.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👨‍🏫 *Оберіть вчителя:*",
        reply_markup=teachers_list_keyboard(teachers),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.filtering_by_teacher)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_teacher, TeacherFilterCallback.filter())
async def show_tests_by_teacher(callback: CallbackQuery, callback_data: TeacherFilterCallback, state: FSMContext) -> None:
    """Show tests for selected teacher."""
    teacher = await queries.get_user(callback_data.id)
    tests = await queries.get_tests_by_teacher(callback_data.id)
    
    if not tests:
        await callback.answer(f"😔 У вчителя {teacher['name']} ще немає публічних тестів.", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"👨‍🏫 *Тести вчителя {teacher['name']}* ({len(tests)}):",
        reply_markup=tests_keyboard(tests),
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
        "📚 *Меню студента*",
        reply_markup=student_menu(lang),
        parse_mode="Markdown",
    )
    await state.clear()
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_subject, BackCallback.filter())
async def back_from_subject_filter(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to search menu from subject filter."""
    await callback.message.edit_text(
        "🔍 *Пошук тестів*\n\n"
        "Оберіть як шукати:",
        reply_markup=search_menu_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)
    await callback.answer()


@router.callback_query(StudentStates.filtering_by_teacher, BackCallback.filter())
async def back_from_teacher_filter(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to search menu from teacher filter."""
    await callback.message.edit_text(
        "🔍 *Пошук тестів*\n\n"
        "Оберіть як шукати:",
        reply_markup=search_menu_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.searching_tests)
    await callback.answer()


@router.callback_query(StudentStates.browsing_tests, BackCallback.filter())
async def back_from_test_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to subjects from test selection."""
    subjects = await queries.get_subjects(callback.from_user.id)
    await callback.message.edit_text(
        "📚 *Оберіть предмет:*",
        reply_markup=subjects_keyboard(subjects),
        parse_mode="Markdown",
    )
    await state.set_state(StudentStates.browsing_subjects)
    await callback.answer()
