import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import queries
from keyboards.callbacks import RoleCallback
from keyboards.keyboards import teacher_menu, student_menu
from states.states import AuthStates

logger = logging.getLogger(__name__)
router = Router()

ROLE_LABELS = {"teacher": "👨‍🏫 Вчитель", "student": "🎓 Студент"}


@router.callback_query(AuthStates.choosing_role, RoleCallback.filter())
async def choose_role(callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext) -> None:
    await state.update_data(role=callback_data.value)
    label = ROLE_LABELS[callback_data.value]

    await callback.message.edit_text(
        f"Ви обрали роль: *{label}*\n\n"
        "Тепер введіть ваше повне ім'я (воно буде відображатися у результатах):",
        parse_mode="Markdown",
    )
    await state.set_state(AuthStates.entering_name)
    await callback.answer()


@router.message(AuthStates.entering_name, F.text)
async def enter_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("⚠️ Ім'я занадто коротке. Введіть щонайменше 2 символи:")
        return
    if len(name) > 64:
        await message.answer("⚠️ Ім'я занадто довге. Введіть не більше 64 символів:")
        return

    data = await state.get_data()
    role = data["role"]

    user = await queries.create_user(message.from_user.id, name, role)
    await state.clear()

    if role == "teacher":
        menu = teacher_menu()
        tip = (
            "Натисніть *➕ Створити тест*, щоб розпочати роботу.\n"
            "Введіть /help для перегляду можливостей."
        )
    else:
        menu = student_menu()
        tip = (
            "Натисніть *📚 Предмети*, щоб знайти тест,\n"
            "або *🔑 Ввести код*, якщо маєте код приватного тесту."
        )

    await message.answer(
        f"✅ *Реєстрацію завершено!*\n\n"
        f"Ім'я: *{name}*\n"
        f"Роль: *{ROLE_LABELS[role]}*\n\n"
        f"{tip}",
        reply_markup=menu,
        parse_mode="Markdown",
    )
