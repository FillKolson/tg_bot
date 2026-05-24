from aiogram.filters.callback_data import CallbackData


class RoleCallback(CallbackData, prefix="role"):
    value: str  # "student" | "teacher"


class LangCallback(CallbackData, prefix="lang"):
    value: str  # "uk" | "en"


class ProfileCallback(CallbackData, prefix="prof"):
    action: str  # "view" | "change_lang" | "change_name" | "change_password" | "reset_password"


class SubjectCallback(CallbackData, prefix="subj"):
    id: int


class TestCallback(CallbackData, prefix="test"):
    id: int
    action: str  # "start" | "results" | "delete" | "back"


class VisibilityCallback(CallbackData, prefix="vis"):
    value: str  # "public" | "private"


class AnswerVisibilityCallback(CallbackData, prefix="ansvis"):
    value: str  # "yes" | "no"


class AttemptsCallback(CallbackData, prefix="att"):
    value: str  # "unlimited" | "limited"


class LimitedAttemptsCallback(CallbackData, prefix="liatt"):
    count: int  # 1, 2, 3, etc.


class OptionCallback(CallbackData, prefix="opt"):
    """Used when marking the correct answer."""
    index: int   # 0-based index in options list


class QuestionNextCallback(CallbackData, prefix="qnext"):
    action: str  # "add" (another question) | "finish"


class DoneOptionsCallback(CallbackData, prefix="doneopt"):
    pass


class BackCallback(CallbackData, prefix="back"):
    to: str  # "teacher_menu" | "student_menu" | "subjects"


class NewSubjectCallback(CallbackData, prefix="newsubj"):
    pass


# Edit test

class EditTestCallback(CallbackData, prefix="editest"):
    id: int
    action: str  # "menu" | "title" | "desc" | "vis" | "attempts" | "questions"


class EditQuestionCallback(CallbackData, prefix="editq"):
    id: int
    action: str  # "edit" | "text" | "options" | "delete"


class EditOptionCallback(CallbackData, prefix="edito"):
    id: int
    action: str  # "edit" | "delete" | "mark_correct"


# Search tests

class SearchCallback(CallbackData, prefix="search"):
    action: str  # "by_name" | "by_subject" | "by_teacher"


class TeacherFilterCallback(CallbackData, prefix="tfilter"):
    id: int  # teacher_id


# Statistics

class StatisticsCallback(CallbackData, prefix="stats"):
    action: str  # "view"


# Delete confirmation

class ConfirmDeleteCallback(CallbackData, prefix="delconf"):
    action: str  # "yes" | "no"


# Teacher tests by subject

class TeacherTestsSubjectCallback(CallbackData, prefix="tsubj"):
    id: int  # subject_id
