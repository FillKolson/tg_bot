"""
Teacher flow
============
«Створити тест» → title → subject → description → visibility
→ [generate access_code if private]
→ question loop: question_text → options (text, text …) → mark_correct
→ «Додати ще» | «Завершити»
"""
import logging
import random
import string
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import queries
from keyboards.callbacks import (
    SubjectCallback, VisibilityCallback, OptionCallback,
    QuestionNextCallback, DoneOptionsCallback, NewSubjectCallback,
    TestCallback, BackCallback, AnswerVisibilityCallback,
)
from keyboards.keyboards import (
    teacher_menu, subjects_keyboard, visibility_keyboard,
    options_input_keyboard, correct_option_keyboard,
    question_next_keyboard, my_tests_keyboard, answer_visibility_keyboard,
)
from states.states import TeacherStates

logger = logging.getLogger(__name__)
router = Router()

MAX_OPTIONS = 4  # per question


# ── Guard: only teachers ────────────────────────────────────────────────────

async def _require_teacher(message_or_cq) -> Optional[dict]:
    tid = (
        message_or_cq.from_user.id
        if isinstance(message_or_cq, (Message, CallbackQuery))
        else None
    )
    user = await queries.get_user(tid)
    if not user or user["role"] != "teacher":
        text = "⛔ Ця функція доступна лише для вчителів."
        if isinstance(message_or_cq, CallbackQuery):
            await message_or_cq.answer(text, show_alert=True)
        else:
            await message_or_cq.answer(text)
        return None
    return user


# ── Helpers ─────────────────────────────────────────────────────────────────

def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _question_summary(data: dict) -> str:
    qs = data.get("questions", [])
    cq = data.get("current_question", {})
    total = len(qs) + (1 if cq else 0)
    return f"Питань збережено: {len(qs)}"


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Enter title
# ══════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "➕ Створити тест")
async def create_test_start(message: Message, state: FSMContext) -> None:
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    await state.set_state(TeacherStates.entering_title)
    await message.answer(
        "📝 *Майстер створення тесту*\n\n"
        "*Крок 1/4* — Введіть назву тесту:\n\n"
        "_/cancel — скасувати_",
        parse_mode="Markdown",
    )


@router.message(TeacherStates.entering_title, F.text)
async def enter_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    if len(title) < 3:
        await message.answer("⚠️ Назва занадто коротка (мін. 3 символи):")
        return
    await state.update_data(title=title, questions=[])

    subjects = await queries.get_subjects()
    await state.set_state(TeacherStates.selecting_subject)

    if subjects:
        await message.answer(
            f"✅ Назва: *{title}*\n\n"
            "*Крок 2/4* — Оберіть предмет або створіть новий:",
            reply_markup=subjects_keyboard(subjects, for_teacher=True),
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            f"✅ Назва: *{title}*\n\n"
            "*Крок 2/4* — Предметів ще немає. Введіть назву нового предмету:",
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.creating_subject)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — Select or create subject
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TeacherStates.selecting_subject, SubjectCallback.filter())
async def select_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    subject = await queries.get_subject(callback_data.id)
    await state.update_data(subject_id=callback_data.id, subject_name=subject["name"])
    await callback.message.edit_text(
        f"✅ Предмет: *{subject['name']}*\n\n"
        "*Крок 3/4* — Введіть короткий опис тесту\n_(або надішліть /skip, щоб пропустити)_",
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_description)
    await callback.answer()


@router.callback_query(TeacherStates.selecting_subject, NewSubjectCallback.filter())
async def new_subject_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("📖 Введіть назву нового предмету:")
    await state.set_state(TeacherStates.creating_subject)
    await callback.answer()


@router.message(TeacherStates.creating_subject, F.text)
async def create_new_subject(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Занадто коротка назва. Спробуйте ще раз:")
        return
    subject = await queries.create_subject(name)
    await state.update_data(subject_id=subject["id"], subject_name=subject["name"])
    await message.answer(
        f"✅ Предмет *«{name}»* створено!\n\n"
        "*Крок 3/4* — Введіть короткий опис тесту\n_(або /skip для пропуску)_",
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_description)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Description
# ══════════════════════════════════════════════════════════════════════════════

@router.message(TeacherStates.entering_description, F.text)
async def enter_description(message: Message, state: FSMContext) -> None:
    desc: Optional[str] = None
    if message.text.strip().lower() != "/skip":
        desc = message.text.strip()

    await state.update_data(description=desc)
    await message.answer(
        (f"✅ Опис: _{desc}_\n\n" if desc else "⏭ Опис пропущено.\n\n")
        + "*Крок 4/5* — Чи показувати студентам правильність відповідей?",
        reply_markup=answer_visibility_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_answer_visibility)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — Answer visibility
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TeacherStates.choosing_answer_visibility, AnswerVisibilityCallback.filter())
async def choose_answer_visibility(callback: CallbackQuery, callback_data: AnswerVisibilityCallback, state: FSMContext) -> None:
    show_answers = callback_data.value == "yes"
    await state.update_data(show_answer_correctness=show_answers)
    
    visibility_text = "✅ Показувати" if show_answers else "❌ Приховувати"
    await callback.message.edit_text(
        f"✅ Правильність відповідей: {visibility_text}\n\n"
        "*Крок 5/5* — Тип доступу:",
        reply_markup=visibility_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_visibility)
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — Visibility
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TeacherStates.choosing_visibility, VisibilityCallback.filter())
async def choose_visibility(callback: CallbackQuery, callback_data: VisibilityCallback, state: FSMContext) -> None:
    is_public = callback_data.value == "public"
    access_code = None if is_public else _generate_code()
    await state.update_data(is_public=is_public, access_code=access_code)

    if is_public:
        note = "🌐 Тест буде публічним — студенти знайдуть його в меню."
    else:
        note = (
            f"🔒 Тест буде приватним.\n"
            f"Код доступу: `{access_code}`\n"
            f"_(поділіться ним зі студентами)_"
        )

    await callback.message.edit_text(
        f"{note}\n\n"
        "✏️ *Тепер додайте питання.*\n\n"
        "Введіть текст *першого питання*:",
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_question_text)
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════════
#  Questions loop — question text
# ══════════════════════════════════════════════════════════════════════════════

@router.message(TeacherStates.entering_question_text, F.text)
async def enter_question_text(message: Message, state: FSMContext) -> None:
    q_text = message.text.strip()
    if len(q_text) < 3:
        await message.answer("⚠️ Текст питання занадто короткий:")
        return
    await state.update_data(current_question={"text": q_text, "options": []})
    await message.answer(
        f"❓ Питання: *{q_text}*\n\n"
        f"Введіть *варіант відповіді 1* (максимум {MAX_OPTIONS}):",
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.entering_option)


# ══════════════════════════════════════════════════════════════════════════════
#  Questions loop — collecting options
# ══════════════════════════════════════════════════════════════════════════════

@router.message(TeacherStates.entering_option, F.text)
async def enter_option(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    cq = data.get("current_question", {})
    opts: list[str] = cq.get("options", [])

    opt_text = message.text.strip()
    if not opt_text:
        await message.answer("⚠️ Варіант не може бути порожнім:")
        return

    opts.append(opt_text)
    cq["options"] = opts
    await state.update_data(current_question=cq)

    n = len(opts)

    if n >= MAX_OPTIONS:
        # Auto-proceed to marking correct
        await message.answer(
            _options_list(opts)
            + "\n\n*Максимум варіантів досягнуто.*\n"
            "🎯 Оберіть *правильну відповідь*:",
            reply_markup=correct_option_keyboard(opts),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.marking_correct)
    else:
        remaining = MAX_OPTIONS - n
        await message.answer(
            _options_list(opts)
            + f"\n\n➕ Введіть варіант {n + 1}"
            + (f" (або натисніть «Готово», якщо варіантів достатньо):" if n >= 2 else ":"),
            reply_markup=options_input_keyboard(opts),
            parse_mode="Markdown",
        )


@router.callback_query(TeacherStates.entering_option, DoneOptionsCallback.filter())
async def done_options(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    opts = data["current_question"]["options"]
    if len(opts) < 2:
        await callback.answer("⚠️ Потрібно щонайменше 2 варіанти!", show_alert=True)
        return
    await callback.message.edit_text(
        _options_list(opts) + "\n\n🎯 Оберіть *правильну відповідь*:",
        reply_markup=correct_option_keyboard(opts),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.marking_correct)
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════════
#  Questions loop — mark correct answer
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TeacherStates.marking_correct, OptionCallback.filter())
async def mark_correct(callback: CallbackQuery, callback_data: OptionCallback, state: FSMContext) -> None:
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
        f"✅ *Питання {q_num} збережено!*\n"
        f"Правильна відповідь: _{correct_text}_\n\n"
        "Що далі?",
        reply_markup=question_next_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer("Збережено!")


# ══════════════════════════════════════════════════════════════════════════════
#  Questions loop — continue or finish
# ══════════════════════════════════════════════════════════════════════════════

@router.callback_query(TeacherStates.marking_correct, QuestionNextCallback.filter())
@router.callback_query(QuestionNextCallback.filter())
async def question_next(callback: CallbackQuery, callback_data: QuestionNextCallback, state: FSMContext) -> None:
    if callback_data.action == "add":
        data = await state.get_data()
        n = len(data.get("questions", []))
        await callback.message.edit_text(
            f"✏️ Введіть текст *питання {n + 1}*:",
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.entering_question_text)
        await callback.answer()
    else:
        await _finish_test(callback, state)


async def _finish_test(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("questions", [])

    if not questions:
        await callback.answer("⚠️ Додайте хоча б одне питання!", show_alert=True)
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
    )
    await queries.bulk_insert_questions_options(test["id"], questions)
    await state.clear()

    code_line = ""
    if not data["is_public"]:
        code_line = f"🔑 Код доступу: `{data['access_code']}`\n"

    await callback.message.edit_text(
        "🎉 *Тест успішно створено!*\n\n"
        f"📝 Назва: *{data['title']}*\n"
        f"📖 Предмет: *{data['subject_name']}*\n"
        f"❓ Питань: *{len(questions)}*\n"
        f"{'🌐 Публічний' if data['is_public'] else '🔒 Приватний'}\n"
        f"{code_line}",
        parse_mode="Markdown",
    )
    await callback.message.answer("Повернення до меню:", reply_markup=teacher_menu())
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════════
#  My Tests
# ══════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📋 Мої тести")
async def my_tests(message: Message, state: FSMContext) -> None:
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    tests = await queries.get_teacher_tests(user["id"], message.from_user.id)

    if not tests:
        await message.answer("📭 У вас ще немає жодного тесту.\nСтворіть перший через *➕ Створити тест*.",
                             parse_mode="Markdown")
        return

    await message.answer(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Натисніть назву — переглянути результати.\n"
        "🗑 — видалити тест.",
        reply_markup=my_tests_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_my_tests)


@router.callback_query(TeacherStates.viewing_my_tests, TestCallback.filter())
async def handle_test_action(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    if callback_data.action == "results":
        await _show_results(callback, callback_data.id, state)
    elif callback_data.action == "delete":
        await _delete_test(callback, callback_data.id, state)
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
        pct = round(s["score"] / s["total_questions"] * 100) if s["total_questions"] else 0
        bar = _progress_bar(pct)
        name = s["users"]["name"] if s.get("users") else "—"
        lines.append(f"{i}. *{name}*\n   {bar} {pct}% ({s['score']}/{s['total_questions']})\n")

    await callback.message.edit_text("\n".join(lines), parse_mode="Markdown")


async def _delete_test(callback: CallbackQuery, test_id: int, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    deleted = await queries.deactivate_test(test_id, user["id"])
    if deleted:
        await callback.answer("🗑 Тест видалено.", show_alert=True)
        # Refresh list
        tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
        if tests:
            await callback.message.edit_reply_markup(reply_markup=my_tests_keyboard(tests))
        else:
            await callback.message.edit_text("📭 Тестів більше немає.")
    else:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Results button from main menu
# ══════════════════════════════════════════════════════════════════════════════

@router.message(F.text == "📊 Результати")
async def results_menu(message: Message, state: FSMContext) -> None:
    user = await _require_teacher(message)
    if not user:
        return
    await state.clear()
    tests = await queries.get_teacher_tests(user["id"], message.from_user.id)

    if not tests:
        await message.answer("📭 У вас ще немає тестів.")
        return

    await message.answer(
        "📊 *Оберіть тест для перегляду результатів:*",
        reply_markup=my_tests_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_results)


@router.callback_query(TeacherStates.viewing_results, TestCallback.filter())
async def results_test_selected(callback: CallbackQuery, callback_data: TestCallback, state: FSMContext) -> None:
    if callback_data.action == "results":
        await _show_results(callback, callback_data.id, state)
    await callback.answer()


# ── Helpers ─────────────────────────────────────────────────────────────────

def _options_list(opts: list[str]) -> str:
    return "📋 Варіанти:\n" + "\n".join(f"  {i + 1}. {o}" for i, o in enumerate(opts))


def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)
