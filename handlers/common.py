import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import queries
from keyboards.keyboards import teacher_menu, student_menu, language_keyboard
from states.states import AuthStates
from config.i18n import i18n

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await queries.get_user(message.from_user.id)

    if user:
        lang = user.get("language", "uk")
        menu = teacher_menu(lang) if user["role"] == "teacher" else student_menu(lang)
        role_label = i18n(f"role_{user['role']}", lang)
        await message.answer(
            i18n("welcome_back", lang, name=user["name"], role=role_label),
            reply_markup=menu,
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            i18n("language_select", "uk"),
            reply_markup=language_keyboard(),
            parse_mode="Markdown",
        )
        await state.set_state(AuthStates.choosing_language)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return

    lang = user.get("language", "uk")
    if user["role"] == "teacher":
        text = i18n("help_teacher", lang)
    else:
        text = i18n("help_student", lang)
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer(i18n("cancel_no_action", "uk"))
        return
    
    user = await queries.get_user(message.from_user.id)
    lang = user.get("language", "uk") if user else "uk"
    
    await state.clear()
    menu = teacher_menu(lang) if (user and user["role"] == "teacher") else student_menu(lang)
    await message.answer(i18n("cancel_confirmed", lang), reply_markup=menu)
