"""
Database queries module.
Initialize with init() before use. Uses admin client to bypass RLS.
"""
from __future__ import annotations

import logging
import os
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from supabase import AsyncClient
from supabase.lib.client_options import AsyncClientOptions
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
supabase_admin: AsyncClient = None  # Admin client (bypasses RLS)
supabase_url: str = None
jwt_secret: str = None
supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")


def init(admin_client: AsyncClient, jwt_secret_key: str, supabase_url_str: str) -> None:
    """Set up the admin client for database operations."""
    global supabase_admin, jwt_secret, supabase_url
    supabase_admin = admin_client
    jwt_secret = jwt_secret_key
    supabase_url = supabase_url_str
    logger.info("✅ Supabase admin client initialized")


# Users

async def get_user(telegram_id: int) -> Optional[dict]:
    """Fetch user by telegram ID."""
    res = await supabase_admin.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


async def create_user(telegram_id: int, name: str, role: str, language: str = "uk") -> dict:
    """Insert new user into database."""
    res = await supabase_admin.table("users").insert(
        {"telegram_id": telegram_id, "name": name, "role": role, "language": language}
    ).execute()
    return res.data[0]


async def update_user_language(telegram_id: int, language: str) -> Optional[dict]:
    """Change user's language setting."""
    res = await supabase_admin.table("users").update(
        {"language": language}
    ).eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


async def update_user_name(telegram_id: int, name: str) -> Optional[dict]:
    """Change user's name."""
    res = await supabase_admin.table("users").update(
        {"name": name}
    ).eq("telegram_id", telegram_id).execute()
    return res.data[0] if res.data else None


# Subjects

async def get_subjects(telegram_id: int = None) -> list[dict]:
    """Return all available subjects, sorted by name."""
    # Note: telegram_id parameter kept for backwards compatibility
    # but RLS is not enforced via JWT anymore
    res = await supabase_admin.table("subjects").select("*").order("name").execute()
    return res.data or []


async def get_subject(subject_id: int) -> Optional[dict]:
    """Fetch single subject by ID."""
    res = await supabase_admin.table("subjects").select("*").eq("id", subject_id).execute()
    return res.data[0] if res.data else None


async def create_subject(name: str) -> dict:
    """Add new subject or return existing if name already exists."""
    # Use upsert to avoid duplicates
    res = await supabase_admin.table("subjects").upsert(
        {"name": name}, on_conflict="name"
    ).execute()
    return res.data[0]


# Tests

async def create_test(
    title: str,
    subject_id: int,
    teacher_id: int,
    is_public: bool,
    access_code: Optional[str],
    description: Optional[str],
    show_answer_correctness: bool = True,
    max_attempts: Optional[int] = None,
) -> dict:
    """Create new test with given parameters."""
    res = await supabase_admin.table("tests").insert({
        "title": title,
        "subject_id": subject_id,
        "teacher_id": teacher_id,
        "is_public": is_public,
        "access_code": access_code,
        "description": description,
        "show_answer_correctness": show_answer_correctness,
        "max_attempts": max_attempts,
    }).execute()
    return res.data[0]


async def get_teacher_tests(teacher_id: int, telegram_id: int) -> list[dict]:
    """Get teacher's tests (with explicit teacher_id verification)."""
    # Use admin client with explicit where clause instead of RLS
    res = (
        await supabase_admin.table("tests")
        .select("*, subjects(name)")
        .eq("teacher_id", teacher_id)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_public_tests_by_subject(subject_id: int, telegram_id: int) -> list[dict]:
    """Get public tests by subject (public access, explicit filtering)."""
    # telegram_id parameter kept for backwards compatibility
    res = (
        await supabase_admin.table("tests")
        .select("*, users(name)")
        .eq("subject_id", subject_id)
        .eq("is_public", True)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_test_by_code(access_code: str, telegram_id: int) -> Optional[dict]:
    """Get test by access code (explicit filtering)."""
    # telegram_id parameter kept for backwards compatibility
    res = (
        await supabase_admin.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("access_code", access_code.upper())
        .eq("is_active", True)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test(test_id: int, telegram_id: int = None) -> Optional[dict]:
    """Get test by ID (explicit filtering)."""
    # telegram_id parameter kept for backwards compatibility
    res = (
        await supabase_admin.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("id", test_id)
        .execute()
    )
    return res.data[0] if res.data else None


async def get_test_with_questions(test_id: int, telegram_id: int = None) -> Optional[dict]:
    """Returns test + ordered questions + options (explicit filtering)."""
    test = await get_test(test_id, telegram_id)
    if not test:
        return None

    # telegram_id parameter kept for backwards compatibility
    q_res = (
        await supabase_admin.table("questions")
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


# Questions & Options

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


# Sessions & Answers

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


async def complete_session(session_id: int, score: int, percentage: float) -> None:
    """Save final score and percentage, mark as completed."""
    await supabase_admin.table("test_sessions").update({
        "score": score,
        "percentage": percentage,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", session_id).execute()


async def get_test_results(test_id: int, telegram_id: int) -> list[dict]:
    """Get all completed sessions for a test (explicit filtering)."""
    # telegram_id parameter kept for backwards compatibility
    res = (
        await supabase_admin.table("test_sessions")
        .select("*, users(name)")
        .eq("test_id", test_id)
        .not_.is_("completed_at", "null")
        .order("completed_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_student_sessions(student_id: int, telegram_id: int) -> list[dict]:
    """Get completed sessions for a student (explicit filtering)."""
    # telegram_id parameter kept for backwards compatibility
    res = (
        await supabase_admin.table("test_sessions")
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


async def get_student_attempt_count(test_id: int, student_id: int) -> int:
    """Get number of completed attempts for a student on a test (admin read)."""
    res = (
        await supabase_admin.table("test_sessions")
        .select("id", count="exact")
        .eq("test_id", test_id)
        .eq("student_id", student_id)
        .not_.is_("completed_at", "null")
        .execute()
    )
    return res.count or 0


# Edit test

async def update_test(
    test_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_public: Optional[bool] = None,
    access_code: Optional[str] = None,
    show_answer_correctness: Optional[bool] = None,
    max_attempts: Optional[int] = None,
) -> dict:
    """Update test fields (admin operation)."""
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if is_public is not None:
        update_data["is_public"] = is_public
    if access_code is not None:
        update_data["access_code"] = access_code
    if show_answer_correctness is not None:
        update_data["show_answer_correctness"] = show_answer_correctness
    if max_attempts is not None:
        update_data["max_attempts"] = max_attempts
    
    res = await supabase_admin.table("tests").update(update_data).eq("id", test_id).execute()
    return res.data[0] if res.data else {}


async def get_questions_by_test(test_id: int) -> list[dict]:
    """Get all questions with options for a test (admin read)."""
    res = (
        await supabase_admin.table("questions")
        .select("*, options(*)")
        .eq("test_id", test_id)
        .order("question_order")
        .execute()
    )
    return res.data or []


async def update_question(question_id: int, text: str) -> dict:
    """Update question text (admin operation)."""
    res = await supabase_admin.table("questions").update(
        {"text": text}
    ).eq("id", question_id).execute()
    return res.data[0] if res.data else {}


async def delete_question(question_id: int) -> bool:
    """Delete question and cascade options (admin operation)."""
    # First delete options
    await supabase_admin.table("options").delete().eq("question_id", question_id).execute()
    # Then delete question
    res = await supabase_admin.table("questions").delete().eq("id", question_id).execute()
    return bool(res.data)


async def get_options_by_question(question_id: int) -> list[dict]:
    """Get all options for a question (admin read)."""
    res = (
        await supabase_admin.table("options")
        .select("*")
        .eq("question_id", question_id)
        .execute()
    )
    return res.data or []


async def update_option(option_id: int, text: str, is_correct: bool) -> dict:
    """Update option text and correctness (admin operation)."""
    res = await supabase_admin.table("options").update(
        {"text": text, "is_correct": is_correct}
    ).eq("id", option_id).execute()
    return res.data[0] if res.data else {}


async def delete_option(option_id: int) -> bool:
    """Delete option (admin operation)."""
    res = await supabase_admin.table("options").delete().eq("id", option_id).execute()
    return bool(res.data)


# Search tests

async def search_tests_by_name(query: str) -> list[dict]:
    """Search tests by title (case-insensitive, public only)."""
    res = (
        await supabase_admin.table("tests")
        .select("*, subjects(name), users(name)")
        .ilike("title", f"%{query}%")
        .eq("is_public", True)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def get_all_teachers() -> list[dict]:
    """Get all users with teacher role (admin read)."""
    res = (
        await supabase_admin.table("users")
        .select("id, name")
        .eq("role", "teacher")
        .order("name")
        .execute()
    )
    return res.data or []


async def get_tests_by_teacher(teacher_id: int) -> list[dict]:
    """Get public tests by specific teacher (admin read)."""
    res = (
        await supabase_admin.table("tests")
        .select("*, subjects(name), users(name)")
        .eq("teacher_id", teacher_id)
        .eq("is_public", True)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


# Statistics

async def get_subject_statistics(teacher_id: int) -> list[dict]:
    """Get statistics per subject for a teacher: subject name, test count, average score."""
    # Get all active tests for the teacher with subject info
    tests_res = (
        await supabase_admin.table("tests")
        .select("id, subject_id, subjects(name)")
        .eq("teacher_id", teacher_id)
        .eq("is_active", True)
        .execute()
    )
    tests = tests_res.data or []
    
    if not tests:
        return []
    
    # Group tests by subject
    subject_stats = {}
    for test in tests:
        subj_id = test["subject_id"]
        subj_name = test["subjects"]["name"]
        if subj_id not in subject_stats:
            subject_stats[subj_id] = {
                "subject_id": subj_id,
                "subject_name": subj_name,
                "test_count": 0,
                "total_sessions": 0,
                "total_score": 0
            }
        subject_stats[subj_id]["test_count"] += 1
    
    # Get sessions for all tests
    test_ids = [t["id"] for t in tests]
    sessions_res = (
        await supabase_admin.table("test_sessions")
        .select("test_id, percentage")
        .in_("test_id", test_ids)
        .not_.is_("completed_at", "null")
        .execute()
    )
    sessions = sessions_res.data or []
    
    # Calculate totals using saved percentage
    for session in sessions:
        test_id = session["test_id"]
        # Find subject for this test
        for test in tests:
            if test["id"] == test_id:
                subj_id = test["subject_id"]
                subject_stats[subj_id]["total_sessions"] += 1
                subject_stats[subj_id]["total_score"] += session.get("percentage", 0)
                break
    
    # Calculate averages and format result
    result = []
    for stats in subject_stats.values():
        avg_score = (
            round(stats["total_score"] / stats["total_sessions"], 1)
            if stats["total_sessions"] > 0 else 0
        )
        result.append({
            "subject_name": stats["subject_name"],
            "test_count": stats["test_count"],
            "total_sessions": stats["total_sessions"],
            "average_score": avg_score
        })
    
    return sorted(result, key=lambda x: x["subject_name"])
