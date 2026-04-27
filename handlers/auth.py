import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import queries
from keyboards.callbacks import RoleCallback, LangCallback
from keyboards.keyboards import teacher_menu, student_menu, role_keyboard, language_keyboard
from states.states import AuthStates
from config.i18n import i18n

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(AuthStates.choosing_language, LangCallback.filter())
async def choose_language(callback: CallbackQuery, callback_data: LangCallback, state: FSMContext) -> None:
    await state.update_data(language=callback_data.value)
    
    await callback.message.edit_text(
        i18n("welcome", callback_data.value),
        reply_markup=role_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(AuthStates.choosing_role)
    await callback.answer()


@router.callback_query(AuthStates.choosing_role, RoleCallback.filter())
async def choose_role(callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "uk")
    
    await state.update_data(role=callback_data.value)
    label = i18n(f"role_{callback_data.value}", lang)

    await callback.message.edit_text(
        i18n("role_selected", lang, role=label),
        parse_mode="Markdown",
    )
    await state.set_state(AuthStates.entering_name)
    await callback.answer()


@router.message(AuthStates.entering_name, F.text)
async def enter_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    data = await state.get_data()
    lang = data.get("language", "uk")

    if len(name) < 2:
        await message.answer(i18n("name_too_short", lang))
        return
    if len(name) > 64:
        await message.answer(i18n("name_too_long", lang))
        return

    role = data["role"]

    user = await queries.create_user(message.from_user.id, name, role, lang)
    await state.clear()

    if role == "teacher":
        menu = teacher_menu(lang)
        tip = i18n("teacher_tip", lang)
    else:
        menu = student_menu(lang)
        tip = i18n("student_tip", lang)

    role_label = i18n(f"role_{role}", lang)
    await message.answer(
        i18n("registration_complete", lang, name=name, role=role_label, tip=tip),
        reply_markup=menu,
        parse_mode="Markdown",
    )
