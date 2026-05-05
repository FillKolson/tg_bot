from aiogram.filters.callback_data import CallbackData


class RoleCallback(CallbackData, prefix="role"):
    value: str  # "student" | "teacher"


class LangCallback(CallbackData, prefix="lang"):
    value: str  # "uk" | "en"


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
