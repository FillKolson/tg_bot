"""
Student flow
============
📚 Предмети → [subject] → [test] → take_test → result
🔑 Ввести код → access_code → take_test → result
📈 Мої результати → list of completed sessions
"""
import logging
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import queries
from keyboards.callbacks import SubjectCallback, TestCallback, BackCallback
from keyboards.keyboards import (
    student_menu, subjects_keyboard, tests_keyboard,
    answer_keyboard, start_test_keyboard,
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


# ══════════════════════════════════════════════════════════════════════════════
#  Browse subjects
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
#  Private test — access code
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
#  Test preview (from public list)
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(StudentStates.browsing_tests, TestCallback.filter(F.action == "start"))
async def test_preview(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    test = await queries.get_test(callback_data.id, callback.from_user.id)
    if not test:
        await callback.answer("⚠️ Тест не знайдено.", show_alert=True)
        return

    q_count = await queries.get_question_count(test["id"])
    teacher_name = test["users"]["name"] if test.get("users") else "—"

    await callback.message.edit_text(
        f"📝 *{test['title']}*\n"
        f"👨‍🏫 Вчитель: {teacher_name}\n"
        f"❓ Питань: {q_count}\n"
        + (f"📄 {test['description']}\n" if test.get("description") else "")
        + "\nНатисніть *▶️ Розпочати тест*, коли будете готові.",
        reply_markup=start_test_keyboard(test["id"]),
        parse_mode="Markdown",
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════════
#  Start test
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TestCallback.filter(F.action == "start"))
async def start_test(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    user = await _require_student(callback)
    if not user:
        return

    test = await queries.get_test_with_questions(callback_data.id, callback.from_user.id)
    if not test or not test.get("questions"):
        await callback.answer("⚠️ У цьому тесті немає питань.", show_alert=True)
        return

    session = await queries.create_session(test["id"], user["id"], len(test["questions"]))

    await state.set_state(StudentStates.taking_test)
    await state.update_data(
        test_id=test["id"],
        session_id=session["id"],
        questions=test["questions"],
        current_index=0,
        score=0,
        show_answer_correctness=test.get("show_answer_correctness", True),
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


# ══════════════════════════════════════════════════════════════════════════════
#  Answer question
# ══════════════════════════════════════════════════════════════════════════════

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
    show_answers = data.get("show_answer_correctness", True)
    
    if is_correct:
        feedback = "✅ *Правильно!*"
    else:
        if show_answers:
            correct_text = correct_opt["text"] if correct_opt else "—"
            feedback = f"❌ *Неправильно.*\nПравильна відповідь: _{correct_text}_"
        else:
            feedback = "❌ *Неправильно!*"

    await callback.message.edit_reply_markup()  # remove buttons
    await callback.message.answer(feedback, parse_mode="Markdown")

    next_idx = idx + 1
    total = len(questions)

    if next_idx >= total:
        # Test finished
        await queries.complete_session(data["session_id"], score)
        await state.clear()
        pct = round(score / total * 100)
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


# ══════════════════════════════════════════════════════════════════════════════
#  My results
# ══════════════════════════════════════════════════════════════════════════════

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
        pct = round(s["score"] / s["total_questions"] * 100) if s["total_questions"] else 0
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


# ── Helpers ─────────────────────────────────────────────────────────────────

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
