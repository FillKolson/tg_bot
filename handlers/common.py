import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import queries
from keyboards.keyboards import teacher_menu, student_menu, language_keyboard, profile_menu_keyboard, language_select_keyboard
from keyboards.callbacks import ProfileCallback, LangCallback
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


@router.callback_query(ProfileStates.choosing_action, ProfileCallback.filter(F.action == "change_password"))
async def profile_change_password(callback: CallbackQuery, state: FSMContext) -> None:
    """Initiate change password flow: ask for current password."""
    user = await queries.get_user(callback.from_user.id)
    if not user or user.get("role") != "teacher":
        await callback.answer(i18n("teacher_only", user.get("language", "uk") if user else "uk"), show_alert=True)
        return

    lang = user.get("language", "uk")
    # Check locked_until
    locked = user.get("locked_until")
    if locked:
        await callback.answer(i18n("account_locked", lang, until=locked), show_alert=True)
        return

    await callback.message.edit_text(i18n("enter_current_password", lang))
    await state.set_state(ProfileStates.changing_password_current)
    await callback.answer()


@router.message(ProfileStates.changing_password_current, F.text)
async def profile_current_password_entered(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return

    lang = user.get("language", "uk")
    if user.get("locked_until"):
        await message.answer(i18n("account_locked", lang, until=user.get("locked_until")))
        await state.clear()
        return

    from security import verify_password

    entered = message.text.strip()
    pwd_hash = user.get("password_hash")
    if not pwd_hash or not verify_password(entered, pwd_hash):
        # increment failed attempts
        fa = await queries.increment_failed_attempts(message.from_user.id)
        MAX_FAIL = 5
        if fa >= MAX_FAIL:
            # lock user
            from datetime import datetime, timedelta, timezone
            until = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            await queries.lock_user_until(message.from_user.id, until)
            await message.answer(i18n("too_many_attempts", lang))
            await state.clear()
            return
        await message.answer(i18n("password_incorrect", lang))
        return

    # success
    await queries.reset_failed_attempts(message.from_user.id)
    await message.answer(i18n("enter_new_password_prompt", lang))
    await state.set_state(ProfileStates.changing_password_new)


@router.message(ProfileStates.changing_password_new, F.text)
async def profile_new_password_entered(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return

    lang = user.get("language", "uk")
    new_pwd = message.text.strip()
    from security import is_common_password, hash_password

    if is_common_password(new_pwd):
        await message.answer(i18n("password_too_common", lang))
        return
    if len(new_pwd) < 8:
        await message.answer(i18n("password_too_short", lang))
        return

    new_hash = hash_password(new_pwd)
    await queries.update_user_password(message.from_user.id, new_hash)
    await message.answer(i18n("password_changed", lang))
    await state.clear()
    menu = teacher_menu(lang)
    await message.answer(i18n("welcome_back", lang, name=user["name"], role=i18n(f"role_{user['role']}", lang)), reply_markup=menu, parse_mode="Markdown")


@router.callback_query(ProfileStates.choosing_action, ProfileCallback.filter(F.action == "reset_password"))
async def profile_reset_password(callback: CallbackQuery, state: FSMContext) -> None:
    user = await queries.get_user(callback.from_user.id)
    if not user or user.get("role") != "teacher":
        await callback.answer(i18n("teacher_only", user.get("language", "uk") if user else "uk"), show_alert=True)
        return
    lang = user.get("language", "uk")
    await callback.message.edit_text(i18n("enter_teacher_code", lang))
    await state.set_state(ProfileStates.resetting_password_code)
    await callback.answer()


@router.message(ProfileStates.resetting_password_code, F.text)
async def profile_reset_code_entered(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "uk") or "uk"
    code = message.text.strip()
    expected = __import__("os").getenv("TEACHER_SIGNUP_CODE", "TEACHER2026")
    if code != expected:
        await message.answer(i18n("teacher_code_invalid", lang))
        return
    await message.answer(i18n("enter_new_password_prompt", lang))
    await state.set_state(ProfileStates.resetting_password_new)


@router.message(ProfileStates.resetting_password_new, F.text)
async def profile_reset_new_password(message: Message, state: FSMContext) -> None:
    user = await queries.get_user(message.from_user.id)
    if not user:
        await message.answer(i18n("not_registered", "uk"))
        return
    lang = user.get("language", "uk")
    new_pwd = message.text.strip()
    from security import is_common_password, hash_password

    if is_common_password(new_pwd):
        await message.answer(i18n("password_too_common", lang))
        return
    if len(new_pwd) < 8:
        await message.answer(i18n("password_too_short", lang))
        return

    new_hash = hash_password(new_pwd)
    await queries.update_user_password(message.from_user.id, new_hash)
    await queries.reset_failed_attempts(message.from_user.id)
    await message.answer(i18n("password_reset_success", lang))
    await state.clear()


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

