from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    choosing_role = State()
    choosing_language = State()
    entering_name = State()


class TeacherStates(StatesGroup):
    # Create test wizard
    entering_title = State()
    selecting_subject = State()
    creating_subject = State()
    entering_description = State()
    choosing_answer_visibility = State()
    choosing_attempts = State()
    choosing_limited_attempts = State()
    choosing_visibility = State()

    # Adding questions
    entering_question_text = State()
    entering_option = State()       # collecting option texts
    marking_correct = State()       # picking correct option via inline btn

    # Managing existing tests
    viewing_tests_and_results = State()
    viewing_tests_by_subject = State()

    # Edit test
    editing_test = State()              # viewing edit menu
    editing_test_title = State()
    editing_test_description = State()
    editing_test_visibility = State()
    editing_test_attempts = State()
    editing_test_limited_attempts = State()
    editing_questions_menu = State()    # viewing list of questions
    selecting_question_to_edit = State()
    editing_question_text = State()
    editing_question_options = State()
    editing_question_option_index = State()  # which option to edit
    editing_question_correct = State()  # picking correct answer after edits

    # Statistics
    viewing_statistics = State()

    # Delete confirmation
    confirming_delete_test = State()


class StudentStates(StatesGroup):
    browsing_subjects = State()
    browsing_tests = State()
    entering_access_code = State()
    taking_test = State()
    viewing_my_results = State()
    
    # Search and filter
    searching_tests = State()           # main search menu
    searching_by_name = State()         # entering search query
    filtering_by_subject = State()      # choosing subject filter
    filtering_by_teacher = State()      # choosing teacher filter
    viewing_search_results = State()    # viewing filtered results
