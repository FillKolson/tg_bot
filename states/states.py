from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    choosing_role = State()
    choosing_language = State()
    entering_name = State()


class TeacherStates(StatesGroup):
    # ── Create test wizard ──────────────────────────────
    entering_title = State()
    selecting_subject = State()
    creating_subject = State()
    entering_description = State()
    choosing_answer_visibility = State()
    choosing_attempts = State()
    choosing_limited_attempts = State()
    choosing_visibility = State()

    # ── Adding questions ────────────────────────────────
    entering_question_text = State()
    entering_option = State()       # collecting option texts
    marking_correct = State()       # picking correct option via inline btn

    # ── Managing existing tests ─────────────────────────
    viewing_tests_and_results = State()


class StudentStates(StatesGroup):
    browsing_subjects = State()
    browsing_tests = State()
    entering_access_code = State()
    taking_test = State()
    viewing_my_results = State()
