import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import queries
from keyboards.keyboards import teacher_menu, student_menu, language_keyboard, profile_menu_keyboard, language_select_keyboard
from keyboards.callbacks import ProfileCallback, LangCallback, BackCallback
from states.states import AuthStates, ProfileStates
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


# Profile handlers

@router.message(F.text.contains("👤"))
async def view_profile(message: Message, state: FSMContext) -> None:
    """Open user profile."""
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return
    
    lang = user.get("language", "uk")
    lang_display = "🇺🇦 Українська" if lang == "uk" else "🇬🇧 English"
    
    profile_text = i18n("profile_title", lang, name=user["name"], language=lang_display)
    await message.answer(profile_text, reply_markup=profile_menu_keyboard(lang), parse_mode="Markdown")
    await state.set_state(ProfileStates.choosing_action)


@router.callback_query(ProfileStates.choosing_action, ProfileCallback.filter(F.action == "change_lang"))
async def profile_change_language(callback: CallbackQuery, state: FSMContext) -> None:
    """Show language selection for profile."""
    user = await queries.get_user(callback.from_user.id)
    if not user:
        await callback.answer(i18n("not_registered", "uk"), show_alert=True)
        return
    
    lang = user.get("language", "uk")
    await callback.message.edit_text(
        i18n("language_select", lang),
        reply_markup=language_select_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(ProfileStates.changing_language)


@router.callback_query(ProfileStates.changing_language, LangCallback.filter())
async def profile_language_selected(callback: CallbackQuery, callback_data: LangCallback, state: FSMContext) -> None:
    """Update user language."""
    user = await queries.get_user(callback.from_user.id)
    if not user:
        await callback.answer(i18n("not_registered", "uk"), show_alert=True)
        return
    
    new_lang = callback_data.value
    await queries.update_user_language(callback.from_user.id, new_lang)
    
    lang_display = "🇺🇦 Українська" if new_lang == "uk" else "🇬🇧 English"
    await callback.message.edit_text(
        i18n("profile_language_changed", new_lang, language=lang_display),
        parse_mode="Markdown",
    )
    
    await state.clear()
    menu = teacher_menu(new_lang) if user["role"] == "teacher" else student_menu(new_lang)
    await callback.message.answer(i18n("welcome_back", new_lang, name=user["name"], role=i18n(f"role_{user['role']}", new_lang)), reply_markup=menu, parse_mode="Markdown")


@router.callback_query(ProfileStates.choosing_action, ProfileCallback.filter(F.action == "change_name"))
async def profile_change_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt for new name."""
    user = await queries.get_user(callback.from_user.id)
    if not user:
        await callback.answer(i18n("not_registered", "uk"), show_alert=True)
        return
    
    lang = user.get("language", "uk")
    await callback.message.edit_text(i18n("profile_name_prompt", lang))
    await state.set_state(ProfileStates.changing_name)


@router.message(ProfileStates.changing_name)
async def profile_name_entered(message: Message, state: FSMContext) -> None:
    """Update user name."""
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return
    
    lang = user.get("language", "uk")
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer(i18n("name_too_short", lang))
        await state.set_state(ProfileStates.changing_name)
        return
    
    if len(name) > 64:
        await message.answer(i18n("name_too_long", lang))
        await state.set_state(ProfileStates.changing_name)
        return
    
    await queries.update_user_name(message.from_user.id, name)
    await message.answer(i18n("profile_name_changed", lang, name=name), parse_mode="Markdown")
    
    await state.clear()
    menu = teacher_menu(lang) if user["role"] == "teacher" else student_menu(lang)
    await message.answer(i18n("welcome_back", lang, name=name, role=i18n(f"role_{user['role']}", lang)), reply_markup=menu, parse_mode="Markdown")


@router.callback_query(ProfileStates.choosing_action, BackCallback.filter(F.to == "menu"))
async def profile_back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle back button in profile menu - return to main menu."""
    user = await queries.get_user(callback.from_user.id)
    if not user:
        await callback.answer(i18n("not_registered", "uk"), show_alert=True)
        return
    
    lang = user.get("language", "uk")
    await state.clear()
    menu = teacher_menu(lang) if user["role"] == "teacher" else student_menu(lang)
    await callback.message.edit_text(
        i18n("welcome_back", lang, name=user["name"], role=i18n(f"role_{user['role']}", lang)),
        reply_markup=menu,
        parse_mode="Markdown",
    )
    await callback.answer()

