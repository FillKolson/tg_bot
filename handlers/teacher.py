"""
Teacher handlers - create tests, manage questions, view results.
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
    AttemptsCallback, LimitedAttemptsCallback,
    EditTestCallback, EditQuestionCallback, EditOptionCallback,
    StatisticsCallback, ConfirmDeleteCallback,
)
from keyboards.keyboards import (
    teacher_menu, subjects_keyboard, visibility_keyboard,
    options_input_keyboard, correct_option_keyboard,
    question_next_keyboard, my_tests_keyboard, answer_visibility_keyboard,
    attempts_keyboard, limited_attempts_keyboard,
    edit_test_menu_keyboard, edit_questions_list_keyboard, edit_options_list_keyboard,
    statistics_keyboard, confirm_delete_keyboard, back_keyboard,
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
        text = "⛔ Ця функція доступна лише для вчителів."
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


# Step 1 - Enter title

@router.message(F.text.in_(["➕ Створити тест", "➕ Create Test"]))
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


# Step 2 - Select or create subject

@router.callback_query(TeacherStates.selecting_subject, SubjectCallback.filter())
async def select_subject(callback: CallbackQuery, callback_data: SubjectCallback, state: FSMContext) -> None:
    subject = await queries.get_subject(callback_data.id)
    await state.update_data(subject_id=callback_data.id, subject_name=subject["name"])
    await callback.message.edit_text(
        f"✅ Предмет: *{subject['name']}*\n\n"
        "*Крок 3/6* — Введіть короткий опис тесту\n_(або надішліть /skip, щоб пропустити)_",
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


# Step 3 - Description

@router.message(TeacherStates.entering_description, F.text)
async def enter_description(message: Message, state: FSMContext) -> None:
    desc: Optional[str] = None
    if message.text.strip().lower() != "/skip":
        desc = message.text.strip()

    await state.update_data(description=desc)
    await message.answer(
        (f"✅ Опис: _{desc}_\n\n" if desc else "⏭ Опис пропущено.\n\n")
        + "*Крок 4/6* — Чи показувати студентам правильність відповідей?",
        reply_markup=answer_visibility_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_answer_visibility)


# Step 4 - Answer visibility

@router.callback_query(TeacherStates.choosing_answer_visibility, AnswerVisibilityCallback.filter())
async def choose_answer_visibility(callback: CallbackQuery, callback_data: AnswerVisibilityCallback, state: FSMContext) -> None:
    show_answers = callback_data.value == "yes"
    await state.update_data(show_answer_correctness=show_answers)
    
    visibility_text = "✅ Показувати" if show_answers else "❌ Приховувати"
    await callback.message.edit_text(
        f"✅ Правильність відповідей: {visibility_text}\n\n"
        "*Крок 5/6* — Можливість повторного проходження тесту:",
        reply_markup=attempts_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_attempts)
    await callback.answer()


# Step 5 - Attempts configuration

@router.callback_query(TeacherStates.choosing_attempts, AttemptsCallback.filter())
async def choose_attempts(callback: CallbackQuery, callback_data: AttemptsCallback, state: FSMContext) -> None:
    if callback_data.value == "unlimited":
        await state.update_data(max_attempts=None)
        await callback.message.edit_text(
            "✅ Студенти можуть повторно проходити цей тест необмежену кількість разів.\n\n"
            "*Крок 6/6* — Тип доступу:",
            reply_markup=visibility_keyboard(),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.choosing_visibility)
    else:
        await callback.message.edit_text(
            "Скільки спроб дозволити студентам?",
            reply_markup=limited_attempts_keyboard(),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.choosing_limited_attempts)
    await callback.answer()


@router.callback_query(TeacherStates.choosing_limited_attempts, LimitedAttemptsCallback.filter())
async def choose_limited_attempts(callback: CallbackQuery, callback_data: LimitedAttemptsCallback, state: FSMContext) -> None:
    max_att = callback_data.count
    await state.update_data(max_attempts=max_att)
    
    attempts_text = "1 спроба" if max_att == 1 else f"{max_att} спроб"
    await callback.message.edit_text(
        f"✅ Максимум спроб: *{attempts_text}*\n\n"
        "*Крок 6/6* — Тип доступу:",
        reply_markup=visibility_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.choosing_visibility)
    await callback.answer()


# Step 6 - Visibility

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


# Questions loop - question text

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


# Questions loop - collecting options

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


# Questions loop - mark correct answer

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


# Questions loop - continue or finish

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
        max_attempts=data.get("max_attempts"),
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

    await callback.message.edit_text(
        "🎉 *Тест успішно створено!*\n\n"
        f"📝 Назва: *{data['title']}*\n"
        f"📖 Предмет: *{data['subject_name']}*\n"
        f"❓ Питань: *{len(questions)}*\n"
        f"{'🌐 Публічний' if data['is_public'] else '🔒 Приватний'}\n"
        f"{attempts_info}"
        f"{code_line}",
        parse_mode="Markdown",
    )
    await callback.message.answer("Повернення до меню:", reply_markup=teacher_menu())
    await callback.answer()


# Tests and Results

@router.message(F.text == "📋 Мої тести")
@router.message(F.text == "📊 Результати")
@router.message(F.text == "📋 Мої тести та результати")
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

    await message.answer(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Натисніть назву — переглянути результати.\n"
        "🗑 — видалити тест.",
        reply_markup=my_tests_keyboard(tests),
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
    
    text = "📊 *Статистика по предметах*\n\n"
    for stat in stats:
        text += (
            f"📖 *{stat['subject_name']}*\n"
            f"   Тестів: {stat['test_count']}\n"
            f"   Середній бал: {stat['average_score']:.1f}%\n\n"
        )
    
    await message.answer(text, parse_mode="Markdown")


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
    
    text = "📊 *Статистика по предметах*\n\n"
    for stat in stats:
        text += (
            f"📖 *{stat['subject_name']}*\n"
            f"   Тестів: {stat['test_count']}\n"
            f"   Проходжень: {stat['total_sessions']}\n"
            f"   Середній бал: {stat['average_score']}%\n\n"
        )
    
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
    data = await state.get_data()
    test_id = data.get("deleting_test_id")
    
    if not test_id:
        await callback.answer("⚠️ Помилка: тест не знайдено.", show_alert=True)
        return
    
    if callback_data.action == "yes":
        user = await queries.get_user(callback.from_user.id)
        deleted = await queries.deactivate_test(test_id, user["id"])
        if deleted:
            user = await queries.get_user(callback.from_user.id)
            tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
            await callback.message.edit_text(
                f"📋 *Ваші тести* ({len(tests)}):",
                reply_markup=my_tests_keyboard(tests),
                parse_mode="Markdown",
            )
            await callback.answer("🗑 Тест видалено.")
        else:
            user = await queries.get_user(callback.from_user.id)
            tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
            await callback.message.edit_text(
                f"📋 *Ваші тести* ({len(tests)}):",
                reply_markup=my_tests_keyboard(tests),
                parse_mode="Markdown",
            )
            await callback.answer("⚠️ Помилка.")
    else:
        # Cancel deletion
        user = await queries.get_user(callback.from_user.id)
        tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
        await callback.message.edit_text(
            f"📋 *Ваші тести* ({len(tests)}):\n\n"
            "Натисніть назву — переглянути результати.\n"
            "🗑 — видалити тест.",
            reply_markup=my_tests_keyboard(tests),
            parse_mode="Markdown",
        )
        await callback.answer("❌ Скасовано.")
        await state.set_state(TeacherStates.viewing_tests_and_results)


@router.callback_query(TeacherStates.confirming_delete_test, BackCallback.filter())
async def back_from_delete_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to tests list from delete confirmation."""
    user = await queries.get_user(callback.from_user.id)
    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    await callback.message.edit_text(
        f"📋 *Ваші тести* ({len(tests)}):\n\n"
        "Натисніть назву — переглянути результати.\n"
        "🗑 — видалити тест.",
        reply_markup=my_tests_keyboard(tests),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.viewing_tests_and_results)
    await callback.answer()


# Helpers

def _options_list(opts: list[str]) -> str:
    return "📋 Варіанти:\n" + "\n".join(f"  {i + 1}. {o}" for i, o in enumerate(opts))


def _progress_bar(pct: int, length: int = 10) -> str:
    filled = round(pct / 100 * length)
    return "█" * filled + "░" * (length - filled)


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
    
    await callback.message.edit_text(
        f"✏️ *Редагування тесту*\n\n"
        f"📝 Назва: *{test['title']}*\n"
        f"🔍 Видимість: {badge} {vis_text}\n"
        f"⏱️ Спроби: {att_text}\n\n"
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
        f"� *Редагування тесту #{test_id}*\n\n"
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
        f"� *Редагування тесту #{test_id}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test_id),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "vis"))
async def edit_test_visibility_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new visibility."""
    test = await queries.get_test(callback_data.id)
    vis_text = "Публічний" if test["is_public"] else f"Приватний (код: {test['access_code']})"
    
    await callback.message.edit_text(
        f"🔍 Поточна видимість: {vis_text}\n\n"
        "Оберіть нову видимість:",
        reply_markup=visibility_keyboard(),
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
        f"� *Редагування тесту #{test['id']}*\n\n"
        "Оберіть, що хочете змінити:",
        reply_markup=edit_test_menu_keyboard(test['id']),
        parse_mode="Markdown",
    )
    await state.set_state(TeacherStates.editing_test)


@router.callback_query(TeacherStates.editing_test, EditTestCallback.filter(F.action == "attempts"))
async def edit_test_attempts_prompt(callback: CallbackQuery, callback_data: EditTestCallback, state: FSMContext) -> None:
    """Ask for new attempts limit."""
    test = await queries.get_test(callback_data.id)
    att_text = f"{test['max_attempts']} спроб" if test['max_attempts'] else "Необмежено"
    
    await callback.message.edit_text(
        f"⏱️ Поточне обмеження: {att_text}\n\n"
        "Оберіть нове:",
        reply_markup=attempts_keyboard(),
        parse_mode="Markdown",
    )
    await state.update_data(editing_test_id=callback_data.id)
    await state.set_state(TeacherStates.editing_test_attempts)
    await callback.answer()


@router.callback_query(TeacherStates.editing_test_attempts, AttemptsCallback.filter())
async def edit_test_attempts_select(callback: CallbackQuery, callback_data: AttemptsCallback, state: FSMContext) -> None:
    """Select attempts limit."""
    if callback_data.value == "unlimited":
        data = await state.get_data()
        test_id = data["editing_test_id"]
        
        await queries.update_test(test_id, max_attempts=None)
        await callback.message.edit_text(
            "✅ Тест може проходитися необмежену кількість разів.",
            parse_mode="Markdown",
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            "Скільки спроб дозволити?",
            reply_markup=limited_attempts_keyboard(),
            parse_mode="Markdown",
        )
        await state.set_state(TeacherStates.editing_test_limited_attempts)
        await callback.answer()


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
        f"� *Редагування тесту #{test_id}*\n\n"
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
    deleted = await queries.delete_question(callback_data.id)
    if deleted:
        await callback.answer("✅ Питання видалено.", show_alert=True)
    else:
        await callback.answer("⚠️ Помилка видалення.", show_alert=True)
    await callback.answer()


@router.callback_query(TeacherStates.editing_questions_menu, EditQuestionCallback.filter(F.action == "edit"))
async def edit_question_prompt(callback: CallbackQuery, callback_data: EditQuestionCallback, state: FSMContext) -> None:
    """Edit question text or options."""
    question = await queries.get_questions_by_test(0)  # This needs test_id, will update
    
    # Simplified: show edit menu
    await callback.message.edit_text(
        "❓ Редагування питання (базовий функціонал)\n\n"
        "_Переходиться на версію із UI для редагування тексту._",
        parse_mode="Markdown",
    )
    await callback.answer()


# Handle Back button during editing

@router.callback_query(TeacherStates.editing_test, BackCallback.filter())
async def back_from_edit_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to tests list from edit menu."""
    user = await queries.get_user(callback.from_user.id)
    tests = await queries.get_teacher_tests(user["id"], callback.from_user.id)
    
    await callback.message.edit_text(
        f"📋 *Ваші тести* ({len(tests)}):",
        reply_markup=my_tests_keyboard(tests),
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
