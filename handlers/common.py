import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import queries
from keyboards.keyboards import teacher_menu, student_menu, role_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await queries.get_user(message.from_user.id)

    if user:
        menu = teacher_menu() if user["role"] == "teacher" else student_menu()
        role_label = "вчитель" if user["role"] == "teacher" else "студент"
        await message.answer(
            f"👋 З поверненням, *{user['name']}*!\n"
            f"Роль: _{role_label}_",
            reply_markup=menu,
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            "👋 *Вітаємо в боті для тестування знань!*\n\n"
            "Будь ласка, оберіть вашу роль:",
            reply_markup=role_keyboard(),
            parse_mode="Markdown",
        )
        from states.states import AuthStates
        await state.set_state(AuthStates.choosing_role)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer("Використайте /start для реєстрації.")
        return

    if user["role"] == "teacher":
        text = (
            "📖 *Довідка для вчителя*\n\n"
            "➕ *Створити тест* — запуск майстра створення тесту\n"
            "📋 *Мої тести* — перегляд усіх ваших тестів\n"
            "📊 *Результати* — результати студентів по тесту\n\n"
            "При створенні тесту можна обрати:\n"
            "• *Публічний* — студенти знайдуть через меню «Предмети»\n"
            "• *Приватний* — доступний лише за унікальним кодом\n\n"
            "/cancel — скасувати поточну дію"
        )
    else:
        text = (
            "📖 *Довідка для студента*\n\n"
            "📚 *Предмети* — перегляд публічних тестів по предметах\n"
            "🔑 *Ввести код* — доступ до приватного тесту за кодом\n"
            "📈 *Мої результати* — ваша статистика\n\n"
            "/cancel — скасувати поточну дію"
        )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("Немає активних дій для скасування.")
        return
    await state.clear()
    user = await queries.get_user(message.from_user.id)
    menu = teacher_menu() if (user and user["role"] == "teacher") else student_menu()
    await message.answer("❌ Дію скасовано.", reply_markup=menu)
