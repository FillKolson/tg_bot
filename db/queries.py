"""
All Supabase database queries.
Call `init(admin_client, jwt_secret, url)` once at startup before using any query.

Uses custom JWT with telegram_id for RLS (Row Level Security).
"""
from __future__ import annotations

import logging
import os
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from supabase import AsyncClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
supabase_admin: AsyncClient = None  # Admin client (bypasses RLS)
supabase_url: str = None
jwt_secret: str = None


def init(admin_client: AsyncClient, jwt_secret_key: str, supabase_url_str: str) -> None:
    """Initialize Supabase clients with JWT support for RLS."""
    global supabase_admin, jwt_secret, supabase_url
    supabase_admin = admin_client
    jwt_secret = jwt_secret_key
    supabase_url = supabase_url_str
    logger.info("✅ Supabase clients initialized with JWT support")


def _create_jwt_for_user(telegram_id: int) -> str:
    """
    Creates a JWT token with telegram_id for RLS policies.
    Token expires in 24 hours.
    """
    payload = {
        "sub": str(telegram_id),
        "telegram_id": telegram_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "role": "authenticated",
    }
    token = pyjwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


def _get_rls_client(telegram_id: int) -> AsyncClient:
    """Creates a Supabase client with JWT for RLS enforcement."""
    token = _create_jwt_for_user(telegram_id)
    return AsyncClient(supabase_url, token)


# ── Users ──────────────────────────────────────────────────────────────────

async def get_user(telegram_id: int) -> Optional[dict]:
    """Get user data (admin bypass for reading own profile)."""
    res = await supabase_admin.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


async def create_user(telegram_id: int, name: str, role: str, language: str = "uk") -> dict:
    """Create new user (admin insert, bypasses RLS)."""
    res = await supabase_admin.table("users").insert(
        {"telegram_id": telegram_id, "name": name, "role": role, "language": language}
    ).execute()
    return res.data[0]


async def update_user_language(telegram_id: int, language: str) -> Optional[dict]:
    """Update user language preference (admin update)."""
    res = await supabase_admin.table("users").update(
        {"language": language}
    ).eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


# ── Subjects ────────────────────────────────────────────────────────────────

async def get_subjects(telegram_id: int = None) -> list[dict]:
    """Get all subjects (public read via RLS or admin bypass)."""
    client = _get_rls_client(telegram_id) if telegram_id else supabase_admin
    res = await client.table("subjects").select("*").order("name").execute()
    return res.data or []


async def get_subject(subject_id: int) -> Optional[dict]:
    """Get subject by ID (admin bypass)."""
    res = await supabase_admin.table("subjects").select("*").eq("id", subject_id).execute()
    return res.data[0] if res.data else None


async def create_subject(name: str) -> dict:
    """Create subject (admin insert, bypasses RLS)."""
    # Use upsert to avoid duplicates
    res = await supabase_admin.table("subjects").upsert(
        {"name": name}, on_conflict="name"
    ).execute()
    return res.data[0]


# ── Tests ───────────────────────────────────────────────────────────────────

async def create_test(
    title: str,
    subject_id: int,
    teacher_id: int,
    is_public: bool,
    access_code: Optional[str],
    description: Optional[str],
    show_answer_correctness: bool = True,
) -> dict:
    """Create test (admin insert, bypasses RLS)."""
    res = await supabase_admin.table("tests").insert({
        "title": title,
        "subject_id": subject_id,
        "teacher_id": teacher_id,
        "is_public": is_public,
        "access_code": access_code,
        "description": description,
        "show_answer_correctness": show_answer_correctness,
    }).execute()
    return res.data[0]


async def get_teacher_tests(teacher_id: int, telegram_id: int) -> list[dict]:
    """Get teacher's tests (with JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id)
    res = (
        await client.table("tests")
        .select("*, subjects(name)")
        .eq("teacher_id", teacher_id)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_public_tests_by_subject(subject_id: int, telegram_id: int) -> list[dict]:
    """Get public tests by subject (with JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id)
    res = (
        await client.table("tests")
        .select("*, users(name)")
        .eq("subject_id", subject_id)
        .eq("is_public", True)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_test_by_code(access_code: str, telegram_id: int) -> Optional[dict]:
    """Get test by access code (with JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id)
    res = (
        await client.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("access_code", access_code.upper())
        .eq("is_active", True)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test(test_id: int, telegram_id: int = None) -> Optional[dict]:
    """Get test by ID (with optional JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id) if telegram_id else supabase_admin
    res = (
        await client.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("id", test_id)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test_with_questions(test_id: int, telegram_id: int = None) -> Optional[dict]:
    """Returns test + ordered questions + options (with optional JWT RLS enforcement)."""
    test = await get_test(test_id, telegram_id)
    if not test:
        return None

    client = _get_rls_client(telegram_id) if telegram_id else supabase_admin
    q_res = (
        await client.table("questions")
        .select("*, options(*)")
        .eq("test_id", test_id)
        .order("question_order")
        .execute()
    )
    test["questions"] = q_res.data or []
    return test


async def deactivate_test(test_id: int, teacher_id: int) -> bool:
    """Deactivate test (admin operation)."""
    res = (
        await supabase_admin.table("tests")
        .update({"is_active": False})
        .eq("id", test_id)
        .eq("teacher_id", teacher_id)
        .execute()
    )
    return bool(res.data)


# ── Questions & Options ─────────────────────────────────────────────────────

async def add_question(test_id: int, text: str, order: int) -> dict:
    """Add question (admin insert, bypasses RLS)."""
    res = await supabase_admin.table("questions").insert(
        {"test_id": test_id, "text": text, "question_order": order}
    ).execute()
    return res.data[0]


async def add_option(question_id: int, text: str, is_correct: bool) -> dict:
    """Add option (admin insert, bypasses RLS)."""
    res = await supabase_admin.table("options").insert(
        {"question_id": question_id, "text": text, "is_correct": is_correct}
    ).execute()
    return res.data[0]


async def bulk_insert_questions_options(test_id: int, questions: list[dict]) -> None:
    """
    Bulk insert questions and options (admin operation).
    questions: [{"text": str, "options": [{"text": str, "is_correct": bool}]}]
    """
    for order, q in enumerate(questions):
        q_row = await add_question(test_id, q["text"], order)
        for opt in q["options"]:
            await add_option(q_row["id"], opt["text"], opt["is_correct"])


# ── Sessions & Answers ──────────────────────────────────────────────────────

async def create_session(test_id: int, student_id: int, total_questions: int) -> dict:
    """Create test session (admin insert, bypasses RLS)."""
    res = await supabase_admin.table("test_sessions").insert({
        "test_id": test_id,
        "student_id": student_id,
        "total_questions": total_questions,
    }).execute()
    return res.data[0]


async def save_answer(
    session_id: int, question_id: int, option_id: int, is_correct: bool
) -> None:
    """Save student answer (admin insert, bypasses RLS)."""
    await supabase_admin.table("session_answers").insert({
        "session_id": session_id,
        "question_id": question_id,
        "option_id": option_id,
        "is_correct": is_correct,
    }).execute()


async def complete_session(session_id: int, score: int) -> None:
    """Mark session as completed (admin update)."""
    await supabase_admin.table("test_sessions").update({
        "score": score,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", session_id).execute()


async def get_test_results(test_id: int, telegram_id: int) -> list[dict]:
    """Get all completed sessions for a test (with JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id)
    res = (
        await client.table("test_sessions")
        .select("*, users(name)")
        .eq("test_id", test_id)
        .not_.is_("completed_at", "null")
        .order("completed_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_student_sessions(student_id: int, telegram_id: int) -> list[dict]:
    """Get completed sessions for a student (with JWT RLS enforcement)."""
    client = _get_rls_client(telegram_id)
    res = (
        await client.table("test_sessions")
        .select("*, tests(title, subjects(name))")
        .eq("student_id", student_id)
        .not_.is_("completed_at", "null")
        .order("completed_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_question_count(test_id: int) -> int:
    """Get count of questions in test (admin read)."""
    res = (
        await supabase_admin.table("questions")
        .select("id", count="exact")
        .eq("test_id", test_id)
        .execute()
    )
    return res.count or 0
