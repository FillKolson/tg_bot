"""
Script to populate the database with sample tests.
Run this after the bot schema is initialized in Supabase.

Usage:
    python populate_sample_tests.py
"""
import asyncio
from supabase import create_async_client
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")

# Sample tests data structure
SAMPLE_TESTS = {
    "Географія": {
        "description": "Тест на знання столиць та географії світу",
        "show_answer_correctness": True,
        "questions": [
            {
                "text": "Яка столиця Франції?",
                "options": [
                    {"text": "Париж", "is_correct": True},
                    {"text": "Ліон", "is_correct": False},
                    {"text": "Марсель", "is_correct": False},
                    {"text": "Тулуза", "is_correct": False},
                ]
            },
            {
                "text": "Який найбільший континент?",
                "options": [
                    {"text": "Азія", "is_correct": True},
                    {"text": "Африка", "is_correct": False},
                    {"text": "Європа", "is_correct": False},
                    {"text": "Північна Америка", "is_correct": False},
                ]
            },
            {
                "text": "Яка столиця Японії?",
                "options": [
                    {"text": "Токіо", "is_correct": True},
                    {"text": "Киото", "is_correct": False},
                    {"text": "Осака", "is_correct": False},
                    {"text": "Йокогама", "is_correct": False},
                ]
            },
        ]
    },
    "Астрономія": {
        "description": "Тест про планети Сонячної системи та космос",
        "show_answer_correctness": True,
        "questions": [
            {
                "text": "Яка найбільша планета Сонячної системи?",
                "options": [
                    {"text": "Юпітер", "is_correct": True},
                    {"text": "Сатурн", "is_correct": False},
                    {"text": "Нептун", "is_correct": False},
                    {"text": "Марс", "is_correct": False},
                ]
            },
            {
                "text": "Скільки місяців у Землі?",
                "options": [
                    {"text": "Один", "is_correct": True},
                    {"text": "Два", "is_correct": False},
                    {"text": "Три", "is_correct": False},
                    {"text": "Чотири", "is_correct": False},
                ]
            },
            {
                "text": "Яка температура поверхні Сонця (приблизно)?",
                "options": [
                    {"text": "5500°C", "is_correct": True},
                    {"text": "1000°C", "is_correct": False},
                    {"text": "10000°C", "is_correct": False},
                    {"text": "15000°C", "is_correct": False},
                ]
            },
        ]
    },
    "Англійська мова": {
        "description": "Базовий тест англійської граматики",
        "show_answer_correctness": True,
        "questions": [
            {
                "text": "What is the past tense of 'go'?",
                "options": [
                    {"text": "went", "is_correct": True},
                    {"text": "going", "is_correct": False},
                    {"text": "goed", "is_correct": False},
                    {"text": "goes", "is_correct": False},
                ]
            },
            {
                "text": "Choose the correct sentence:",
                "options": [
                    {"text": "She goes to school every day", "is_correct": True},
                    {"text": "She go to school every day", "is_correct": False},
                    {"text": "She going to school every day", "is_correct": False},
                    {"text": "She gone to school every day", "is_correct": False},
                ]
            },
            {
                "text": "What does 'hello' mean in Ukrainian?",
                "options": [
                    {"text": "Привіт", "is_correct": True},
                    {"text": "До побачення", "is_correct": False},
                    {"text": "Спасибі", "is_correct": False},
                    {"text": "Будь ласка", "is_correct": False},
                ]
            },
        ]
    },
    "Німецька мова": {
        "description": "Базовий тест німецької мови",
        "show_answer_correctness": True,
        "questions": [
            {
                "text": "Was ist die Übersetzung von 'Hallo'?",
                "options": [
                    {"text": "Привіт", "is_correct": True},
                    {"text": "До побачення", "is_correct": False},
                    {"text": "Гарячий", "is_correct": False},
                    {"text": "Голова", "is_correct": False},
                ]
            },
            {
                "text": "Wie heißen Sie? — Ich heiße...",
                "options": [
                    {"text": "Alle Optionen sind möglich", "is_correct": True},
                    {"text": "John", "is_correct": False},
                    {"text": "Berlin", "is_correct": False},
                    {"text": "Deutsche", "is_correct": False},
                ]
            },
            {
                "text": "Was ist das deutsche Wort für 'Wasser'?",
                "options": [
                    {"text": "Wasser", "is_correct": True},
                    {"text": "Waiter", "is_correct": False},
                    {"text": "Wald", "is_correct": False},
                    {"text": "Wand", "is_correct": False},
                ]
            },
        ]
    },
}


async def create_sample_tests():
    """Create sample tests in the database."""
    client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get or create a test teacher user
    teachers = await client.table("users").select("*").eq("role", "teacher").limit(1).execute()
    
    if not teachers.data:
        print("❌ No teacher user found. Please create a teacher first.")
        return
    
    teacher_id = teachers.data[0]["id"]
    print(f"✅ Using teacher ID: {teacher_id}")
    
    # Process each subject
    for subject_name, test_data in SAMPLE_TESTS.items():
        print(f"\n📖 Processing '{subject_name}'...")
        
        # Get or create subject
        subjects = await client.table("subjects").select("*").eq("name", subject_name).execute()
        if subjects.data:
            subject_id = subjects.data[0]["id"]
            print(f"   ✅ Subject exists (ID: {subject_id})")
        else:
            new_subject = await client.table("subjects").insert({"name": subject_name}).execute()
            subject_id = new_subject.data[0]["id"]
            print(f"   ✅ Subject created (ID: {subject_id})")
        
        # Create test
        test_title = f"Тест: {subject_name}"
        test_res = await client.table("tests").insert({
            "title": test_title,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "is_public": True,
            "description": test_data["description"],
            "show_answer_correctness": test_data["show_answer_correctness"],
        }).execute()
        
        test_id = test_res.data[0]["id"]
        print(f"   ✅ Test created: '{test_title}' (ID: {test_id})")
        
        # Add questions
        for q_idx, question in enumerate(test_data["questions"]):
            q_res = await client.table("questions").insert({
                "test_id": test_id,
                "text": question["text"],
                "question_order": q_idx,
            }).execute()
            
            question_id = q_res.data[0]["id"]
            
            # Add options
            for opt in question["options"]:
                await client.table("options").insert({
                    "question_id": question_id,
                    "text": opt["text"],
                    "is_correct": opt["is_correct"],
                }).execute()
            
            print(f"      ✅ Question {q_idx + 1}: '{question['text'][:50]}...'")
    
    print("\n✅ All sample tests created successfully!")


if __name__ == "__main__":
    asyncio.run(create_sample_tests())
