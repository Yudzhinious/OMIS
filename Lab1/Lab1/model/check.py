from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class User(ABC):
    def __init__(self, login: str, email: str, password: str):
        self.id = str(uuid.uuid4())
        self.login = login
        self.email = email
        self.passwordHash = hash(password)  # простая имитация хеша
        self.registrationDate = datetime.now()
        self.isActive = True

    def authenticate(self, password: str) -> bool:
        return hash(password) == self.passwordHash

    @abstractmethod
    def updateProfile(self, new_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def changePassword(self, old_password: str, new_password: str) -> bool:
        pass


class Administrator(User):
    def __init__(self, login: str, email: str, password: str):
        super().__init__(login, email, password)
        self.levelAdmin = 10

    def manageUser(self) -> None:
        print(f"Админ {self.login} управляет пользователями")

    def manageAccess(self) -> None:
        print("Управление доступом...")

    def monitorSystem(self) -> None:
        print("Мониторинг системы...")

    def viewLogs(self) -> List[str]:
        return ["Лог: вход в систему", "Лог: создание опроса"]

    def updateProfile(self, new_data: Dict[str, Any]) -> None:
        print(f"Профиль админа {self.login} обновлён")

    def changePassword(self, old_password: str, new_password: str) -> bool:
        if self.authenticate(old_password):
            self.passwordHash = hash(new_password)
            return True
        return False


class SurveyOrganizer(User):
    def __init__(self, login: str, email: str, password: str):
        super().__init__(login, email, password)
        self.organizerName = login

    def createSurvey(self) -> 'Survey':
        return Survey(f"Опрос от {self.login}")

    def manageSurvey(self) -> None:
        print(f"{self.login} редактирует опрос")

    def viewResults(self) -> 'Report':
        return Report()

    def exportData(self) -> str:
        return "данные_экспортированы.csv"

    def updateProfile(self, new_data: Dict[str, Any]) -> None:
        print(f"Организатор {self.login} обновил профиль")

    def changePassword(self, old_password: str, new_password: str) -> bool:
        if self.authenticate(old_password):
            self.passwordHash = hash(new_password)
            return True
        return False


class Participant:
    def __init__(self, code: str):
        self.codeParticipant = code
        self.entryDate = datetime.now()

    def fillSurvey(self, survey: 'Survey') -> 'Response':
        print(f"Участник {self.codeParticipant} проходит опрос: {survey.title}")
        return Response(survey)

    def leaveFeedback(self) -> str:
        return "Спасибо за участие!"

    def getHistory(self) -> List['Response']:
        return [Response(None)]


class Survey:
    def __init__(self, title: str):
        self.surveyId = str(uuid.uuid4())
        self.title = title
        self.description = "Тестовый опрос"
        self.creationDate = datetime.now()
        self.startDate = datetime.now()
        self.endDate = None
        self.isPublished = False
        self.maxResponses = 100
        self.questions: List[Question] = []
        self.responses: List[Response] = []

    def addQuestion(self, question: 'Question') -> None:
        self.questions.append(question)
        print(f"Добавлен вопрос: {question.text[:30]}...")

    def deleteQuestion(self, question_id: str) -> None:
        self.questions = [q for q in self.questions if q.questionId != question_id]

    def publish(self) -> None:
        self.isPublished = True
        print(f"Опрос '{self.title}' опубликован!")

    def checkStructure(self) -> bool:
        return len(self.questions) > 0


class Response:
    def __init__(self, survey: Optional[Survey]):
        self.responseId = str(uuid.uuid4())
        self.survey = survey
        self.dispatchDate = datetime.now()
        self.endTime = 0
        self.ipAddress = "192.168.1.1"
        self.deviceInfo = "Chrome/PC"
        self.answers: List[Answer] = []

    def isCompleted(self) -> bool:
        return len(self.answers) == len(self.survey.questions) if self.survey else False

    def check(self) -> bool:
        return all(a.check() for a in self.answers)

    def getPoints(self) -> float:
        return sum(a.value.isdigit() and float(a.value) or 0 for a in self.answers)


class Answer:
    def __init__(self, question: 'Question', value: str):
        self.answerId = str(uuid.uuid4())
        self.question = question
        self.value = value
        self.submissionDate = datetime.now()

    def check(self) -> bool:
        return self.question.checkAnswer(self.value)

    def getAnswerValue(self, value: str) -> str:
        return value.strip()

class QuestionType(Enum):
    TEXT = "text"
    SCALE = "scale"
    MULTIPLE_CHOICE = "multiple_choice"
    MEDIA = "media"

class AccessType(Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"

class ReportFormat(Enum):
    PDF = "pdf"
    EXCEL = "excel"

class ActionType(Enum):
    SHOW_QUESTION = "show"
    SKIP_TO = "skip"

class Question(ABC):
    def __init__(self, text: str, order: int):
        self.questionId = str(uuid.uuid4())
        self.text = text
        self.order = order
        self.isRequired = True
        self.logicRule = []

    @abstractmethod
    def checkAnswer(self, answer: str) -> bool:
        pass

    @abstractmethod
    def getNextQuestion(self, number: int) -> 'Question':
        pass

    @abstractmethod
    def getType(self) -> QuestionType:
        pass


class FreeTextQuestion(Question):
    def __init__(self, text: str, order: int):
        super().__init__(text, order)
        self.maxAnswerLength = 500
        self.regularExpressionPattern = ".*"

    def checkAnswer(self, answer: str) -> bool:
        return len(answer) <= self.maxAnswerLength

    def getNextQuestion(self, number: int) -> Question:
        return self

    def getType(self) -> QuestionType:
        return QuestionType.TEXT


class ScaleQuestion(Question):
    def __init__(self, text: str, order: int, min_val: int, max_val: int):
        super().__init__(text, order)
        self.minValue = min_val
        self.maxValue = max_val
        self.metaMinimum = "Совсем не согласен"
        self.metaMaximum = "Полностью согласен"

    def checkAnswer(self, answer: str) -> bool:
        try:
            val = int(answer)
            return self.minValue <= val <= self.maxValue
        except:
            return False

    def getNextQuestion(self, number: int) -> Question:
        return self

    def getType(self) -> QuestionType:
        return QuestionType.SCALE


class MultipleChoiceQuestion(Question):
    def __init__(self, text: str, order: int):
        super().__init__(text, order)
        self.multipleChoice = False
        self.randomVariantOrder = False
        self.options: List[Option] = []

    def addVariant(self, option: 'Option'):
        self.options.append(option)

    def checkAnswer(self, answer: str) -> bool:
        return any(opt.text == answer for opt in self.options)

    def getNextQuestion(self, number: int) -> Question:
        return self

    def getType(self) -> QuestionType:
        return QuestionType.MULTIPLE_CHOICE


class Option:
    def __init__(self, text: str, order: int):
        self.variantId = str(uuid.uuid4())
        self.text = text
        self.order = order
        self.urlImage = ""

    def check(self) -> bool:
        return True  # всегда валидный вариант


class Report:
    def __init__(self):
        self.reportId = str(uuid.uuid4())
        self.naming = "Отчёт по опросу"
        self.generationDate = datetime.now()
        self.format = ReportFormat.PDF

    def generate(self) -> None:
        print("Отчёт сгенерирован!")

    def addDiagram(self) -> None:
        print("Диаграмма добавлена")

    def export(self) -> str:
        return f"report_{self.reportId}.pdf"


class InvitationLink:
    def __init__(self, max_uses: int = 100):
        self.invitationLinkId = str(uuid.uuid4())
        self.token = str(uuid.uuid4())[:8]
        self.maxUses = max_uses
        self.currentUses = 0
        self.expirationDate = datetime.now()

    def generate(self) -> str:
        return f"https://survey.example/invite/{self.token}"

    def check(self) -> bool:
        return self.currentUses < self.maxUses

    def incrementUse(self) -> None:
        self.currentUses += 1
