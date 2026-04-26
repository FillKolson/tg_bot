"""
All Supabase database queries.
Call `init(client)` once at startup before using any query.
"""
from __future__ import annotations

import logging
from typing import Optional

from supabase import AsyncClient

logger = logging.getLogger(__name__)
supabase: AsyncClient = None


def init(client: AsyncClient) -> None:
    global supabase
    supabase = client


# ── Users ──────────────────────────────────────────────────────────────────

async def get_user(telegram_id: int) -> Optional[dict]:
    res = await supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


async def create_user(telegram_id: int, name: str, role: str) -> dict:
    res = await supabase.table("users").insert(
        {"telegram_id": telegram_id, "name": name, "role": role}
    ).execute()
    return res.data[0]


# ── Subjects ────────────────────────────────────────────────────────────────

async def get_subjects() -> list[dict]:
    res = await supabase.table("subjects").select("*").order("name").execute()
    return res.data or []


async def get_subject(subject_id: int) -> Optional[dict]:
    res = await supabase.table("subjects").select("*").eq("id", subject_id).execute()
    return res.data[0] if res.data else None


async def create_subject(name: str) -> dict:
    # Use upsert to avoid duplicates
    res = await supabase.table("subjects").upsert(
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
) -> dict:
    res = await supabase.table("tests").insert({
        "title": title,
        "subject_id": subject_id,
        "teacher_id": teacher_id,
        "is_public": is_public,
        "access_code": access_code,
        "description": description,
    }).execute()
    return res.data[0]


async def get_teacher_tests(teacher_id: int) -> list[dict]:
    res = (
        await supabase.table("tests")
        .select("*, subjects(name)")
        .eq("teacher_id", teacher_id)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_public_tests_by_subject(subject_id: int) -> list[dict]:
    res = (
        await supabase.table("tests")
        .select("*, users(name)")
        .eq("subject_id", subject_id)
        .eq("is_public", True)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_test_by_code(access_code: str) -> Optional[dict]:
    res = (
        await supabase.table("tests")
        .select("*, subjects(name)")
        .eq("access_code", access_code.upper())
        .eq("is_active", True)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test(test_id: int) -> Optional[dict]:
    res = (
        await supabase.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("id", test_id)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test_with_questions(test_id: int) -> Optional[dict]:
    """Returns test + ordered questions + options."""
    test = await get_test(test_id)
    if not test:
        return None

    q_res = (
        await supabase.table("questions")
        .select("*, options(*)")
        .eq("test_id", test_id)
        .order("question_order")
        .execute()
    )
    test["questions"] = q_res.data or []
    return test


async def deactivate_test(test_id: int, teacher_id: int) -> bool:
    res = (
        await supabase.table("tests")
        .update({"is_active": False})
        .eq("id", test_id)
        .eq("teacher_id", teacher_id)
        .execute()
    )
    return bool(res.data)


# ── Questions & Options ─────────────────────────────────────────────────────

async def add_question(test_id: int, text: str, order: int) -> dict:
    res = await supabase.table("questions").insert(
        {"test_id": test_id, "text": text, "question_order": order}
    ).execute()
    return res.data[0]


async def add_option(question_id: int, text: str, is_correct: bool) -> dict:
    res = await supabase.table("options").insert(
        {"question_id": question_id, "text": text, "is_correct": is_correct}
    ).execute()
    return res.data[0]


async def bulk_insert_questions_options(test_id: int, questions: list[dict]) -> None:
    """
    questions: [{"text": str, "options": [{"text": str, "is_correct": bool}]}]
    """
    for order, q in enumerate(questions):
        q_row = await add_question(test_id, q["text"], order)
        for opt in q["options"]:
            await add_option(q_row["id"], opt["text"], opt["is_correct"])


# ── Sessions & Answers ──────────────────────────────────────────────────────

async def create_session(test_id: int, student_id: int, total_questions: int) -> dict:
    res = await supabase.table("test_sessions").insert({
        "test_id": test_id,
        "student_id": student_id,
        "total_questions": total_questions,
    }).execute()
    return res.data[0]


async def save_answer(
    session_id: int, question_id: int, option_id: int, is_correct: bool
) -> None:
    await supabase.table("session_answers").insert({
        "session_id": session_id,
        "question_id": question_id,
        "option_id": option_id,
        "is_correct": is_correct,
    }).execute()


async def complete_session(session_id: int, score: int) -> None:
    from datetime import datetime, timezone
    await supabase.table("test_sessions").update({
        "score": score,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", session_id).execute()


async def get_test_results(test_id: int) -> list[dict]:
    """All completed sessions for a test, newest first."""
    res = (
        await supabase.table("test_sessions")
        .select("*, users(name)")
        .eq("test_id", test_id)
        .not_.is_("completed_at", "null")
        .order("completed_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_student_sessions(student_id: int) -> list[dict]:
    """Completed sessions for a student with test titles."""
    res = (
        await supabase.table("test_sessions")
        .select("*, tests(title, subjects(name))")
        .eq("student_id", student_id)
        .not_.is_("completed_at", "null")
        .order("completed_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_question_count(test_id: int) -> int:
    res = (
        await supabase.table("questions")
        .select("id", count="exact")
        .eq("test_id", test_id)
        .execute()
    )
    return res.count or 0
