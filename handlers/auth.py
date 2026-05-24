import logging
import os

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

    # If teacher role chosen, require teacher signup code before name
    if callback_data.value == "teacher":
        await callback.message.answer(i18n("enter_teacher_code", lang))
        await state.set_state(AuthStates.entering_teacher_code)
    else:
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

    # For teachers: ask for password before creating account
    if role == "teacher":
        await state.update_data(pending_name=name)
        await message.answer(i18n("enter_teacher_password_prompt", lang))
        await state.set_state(AuthStates.entering_teacher_password)
        return

    # For students and others: create user immediately
    user = await queries.create_user(message.from_user.id, name, role, lang)
    await state.clear()

    menu = teacher_menu(lang) if role == "teacher" else student_menu(lang)
    tip = i18n("teacher_tip", lang) if role == "teacher" else i18n("student_tip", lang)

    role_label = i18n(f"role_{role}", lang)
    await message.answer(
        i18n("registration_complete", lang, name=name, role=role_label, tip=tip),
        reply_markup=menu,
        parse_mode="Markdown",
    )


@router.message(AuthStates.entering_teacher_code, F.text)
async def enter_teacher_code(message: Message, state: FSMContext) -> None:
    """Validate teacher signup code before asking for name."""
    data = await state.get_data()
    lang = data.get("language", "uk")
    code = message.text.strip()

    expected = os.getenv("TEACHER_SIGNUP_CODE", "TEACHER2026")
    if code == expected:
        await message.answer(i18n("teacher_code_accepted", lang))
        await state.set_state(AuthStates.entering_name)
    else:
        await message.answer(i18n("teacher_code_invalid", lang))


@router.message(AuthStates.entering_teacher_password, F.text)
async def enter_teacher_password(message: Message, state: FSMContext) -> None:
    """Validate and store teacher password, then create user with hashed password."""
    data = await state.get_data()
    lang = data.get("language", "uk")
    name = data.get("pending_name")
    role = data.get("role")

    pwd = message.text.strip()
    if len(pwd) < 8:
        await message.answer(i18n("password_too_short", lang))
        return

    # Hash password and create user
    from security import hash_password

    pwd_hash = hash_password(pwd)
    user = await queries.create_user(message.from_user.id, name, role, lang, password_hash=pwd_hash)
    await state.clear()

    menu = teacher_menu(lang)
    tip = i18n("teacher_tip", lang)
    role_label = i18n(f"role_{role}", lang)
    await message.answer(
        i18n("registration_complete", lang, name=name, role=role_label, tip=tip),
        reply_markup=menu,
        parse_mode="Markdown",
    )
