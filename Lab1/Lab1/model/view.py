from abc import ABC, abstractmethod
from datetime import datetime
from queue import Queue
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class DeviceType(Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"

class ScreenSize:
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


class ISurveyView(ABC):
    @abstractmethod
    def adaptToDeviceType(self, device_type: DeviceType) -> None:
        pass

    @abstractmethod
    def getScreenSize(self) -> ScreenSize:
        pass


class SurveyEditorView(ISurveyView):
    def __init__(self):
        self.questionList: List[str] = []
        self.redactorPanel: Dict[str, Any] = {"visible": True, "elements": []}
        self.propertiesPanel: Dict[str, Any] = {"visible": True}
        self.current_device: DeviceType = DeviceType.DESKTOP

    def adaptToDeviceType(self, device_type: DeviceType) -> None:
        self.current_device = device_type
        if device_type == DeviceType.MOBILE:
            print("Редактор адаптирован для мобильного устройства: упрощенный интерфейс")
            self.redactorPanel["visible"] = False
        else:
            print("Редактор адаптирован для десктопного устройства: полный интерфейс")
            self.redactorPanel["visible"] = True

    def getScreenSize(self) -> ScreenSize:
        if self.current_device == DeviceType.MOBILE:
            return ScreenSize(375, 812)
        elif self.current_device == DeviceType.TABLET:
            return ScreenSize(768, 1024)
        return ScreenSize(1920, 1080)

    def showRedactor(self) -> None:
        if self.redactorPanel["visible"]:
            print("Показ редактора вопросов")
        else:
            print("Редактор скрыт на этом устройстве")

    def addElementToQuestionPanel(self, element: str) -> None:
        self.redactorPanel["elements"].append(element)
        print(f"Добавлен элемент: {element}. Всего элементов: {len(self.redactorPanel['elements'])}")

    def showPrewatch(self) -> None:
        print("Предпросмотр опроса:")
        for i, question in enumerate(self.questionList, 1):
            print(f"  {i}. {question}")

    def saveChanges(self) -> None:
        print(f"Сохранено {len(self.questionList)} вопросов")
        return len(self.questionList)


class AnalyticsDashboardView(ISurveyView):
    def __init__(self):
        self.containerPanel: Dict[str, List[str]] = {"charts": [], "tables": []}
        self.statisticsPanel: Dict[str, float] = {"completion_rate": 0.0, "avg_score": 0.0}
        self.filtrationElements: List[str] = ["date_range", "user_type", "score_filter"]
        self.current_device: DeviceType = DeviceType.DESKTOP

    def adaptToDeviceType(self, device_type: DeviceType) -> None:
        self.current_device = device_type
        if device_type == DeviceType.MOBILE:
            print("Аналитика адаптирована для мобильных: упрощенные диаграммы")
            self.containerPanel["charts"] = ["pie_chart_mobile"]
        else:
            print("Аналитика адаптирована для десктопов: полные диаграммы")
            self.containerPanel["charts"] = ["bar_chart", "line_chart", "pie_chart"]

    def getScreenSize(self) -> ScreenSize:
        return ScreenSize(1200, 800) if self.current_device == DeviceType.DESKTOP else ScreenSize(375, 812)

    def showPanel(self) -> None:
        print("Панель аналитики:")
        print(f"  Диаграммы: {self.containerPanel['charts']}")
        print(f"  Фильтры: {self.filtrationElements}")

    def drawDiagrams(self) -> None:
        for chart in self.containerPanel["charts"]:
            print(f"Отрисована диаграмма: {chart}")

    def updateStatistics(self, completion_rate: float, avg_score: float) -> None:
        self.statisticsPanel["completion_rate"] = completion_rate
        self.statisticsPanel["avg_score"] = avg_score
        print(f"Статистика обновлена: завершение={completion_rate * 100}%, средний балл={avg_score}")

    def exportData(self, format: str = "csv") -> str:
        data = f"completion_rate,avg_score\n{self.statisticsPanel['completion_rate']},{self.statisticsPanel['avg_score']}"
        print(f"Данные экспортированы в формате {format}")
        return data


class NotificationView:
    def __init__(self):
        self.notificationBurst: Queue = Queue()

    def showNotification(self, message: str) -> None:
        print(f"Уведомление: {message}")
        self.notificationBurst.put(message)

    def showError(self, error_message: str) -> None:
        print(f"Ошибка: {error_message}")

    def showWarning(self, warning_message: str) -> None:
        print(f"Предупреждение: {warning_message}")

    def showSuccess(self, success_message: str) -> None:
        print(f"Успех: {success_message}")


class SurveyCreationView(ISurveyView):
    def __init__(self):
        self.questionsContainer: List[Dict[str, Any]] = []
        self.progressBar: Dict[str, float] = {"current": 0.0, "total": 100.0}
        self.current_device: DeviceType = DeviceType.DESKTOP

    def adaptToDeviceType(self, device_type: DeviceType) -> None:
        self.current_device = device_type
        print(f"Создание опроса адаптировано для {device_type.value}")

    def getScreenSize(self) -> ScreenSize:
        sizes = {
            DeviceType.DESKTOP: ScreenSize(1280, 720),
            DeviceType.TABLET: ScreenSize(768, 1024),
            DeviceType.MOBILE: ScreenSize(375, 812)
        }
        return sizes.get(self.current_device, ScreenSize())

    def showQuestion(self, question_text: str, options: List[str]) -> None:
        question = {"text": question_text, "options": options, "id": str(uuid.uuid4())[:8]}
        self.questionsContainer.append(question)
        print(f"Вопрос показан: {question_text}")
        print(f"  Варианты: {options}")

    def showProgress(self, progress: float) -> None:
        self.progressBar["current"] = progress
        print(f"Прогресс: {progress}%")

    def showReport(self, results: Dict[str, Any]) -> None:
        print("Отчет по опросу:")
        for key, value in results.items():
            print(f"  {key}: {value}")

    def showAnswer(self, question_id: str, answer: str) -> None:
        print(f"Ответ на вопрос {question_id}: {answer}")


class SystemMonitoringView:
    def __init__(self):
        self.metricsPanel: Dict[str, float] = {"cpu": 0.0, "memory": 0.0, "disk": 0.0}
        self.progressViewer: Dict[str, List[float]] = {"cpu_history": [], "memory_history": []}
        self.listOfActions: List[str] = []

    def updateMetrics(self, cpu: float, memory: float, disk: float) -> None:
        self.metricsPanel = {"cpu": cpu, "memory": memory, "disk": disk}
        self.progressViewer["cpu_history"].append(cpu)
        self.progressViewer["memory_history"].append(memory)
        print(f"Метрики обновлены: CPU={cpu}%, Memory={memory}%, Disk={disk}%")

    def showProgress(self) -> None:
        print("Прогресс системы:")
        print(f"  CPU: {self.metricsPanel['cpu']}%")
        print(f"  Memory: {self.metricsPanel['memory']}%")
        print(f"  История CPU (последние 3): {self.progressViewer['cpu_history'][-3:]}")

    def showNotifications(self) -> None:
        for action in self.listOfActions[-5:]:
            print(f"Действие системы: {action}")


class SurveyHistoryView:
    def __init__(self):
        self.listOfSurveys: List[Dict[str, Any]] = []
        self.filterOptions: Dict[str, List[str]] = {
            "status": ["all", "completed", "pending"],
            "date": ["last_week", "last_month", "all_time"]
        }

    def updateList(self, surveys: List[Dict[str, Any]]) -> None:
        self.listOfSurveys = surveys
        print(f"Список опросов обновлен. Всего: {len(surveys)}")

    def applyFilter(self, filter_type: str, value: str) -> List[Dict[str, Any]]:
        filtered = [s for s in self.listOfSurveys if s.get(filter_type, "") == value]
        print(f"Применен фильтр {filter_type}={value}. Найдено: {len(filtered)}")
        return filtered

    def openSurvey(self, survey_id: str) -> Optional[Dict[str, Any]]:
        for survey in self.listOfSurveys:
            if survey.get("id") == survey_id:
                print(f"Открыт опрос: {survey.get('name')}")
                return survey
        print(f"Опрос с ID {survey_id} не найден")
        return None


class Controller:
    def __init__(self):
        self.name = "BaseController"


class Model:
    def __init__(self):
        self.data = {}


class BaseView(ABC):
    def __init__(self):
        self.controller: Controller = Controller()
        self.model: Model = Model()

    def update(self) -> None:
        print("Представление обновлено")

    def updateData(self, data: Dict[str, Any]) -> None:
        self.model.data.update(data)
        print(f"Данные обновлены: {list(data.keys())}")

    def showError(self, error: str) -> None:
        print(f"Ошибка в представлении: {error}")

    def showMessage(self, message: str) -> None:
        print(f"Сообщение: {message}")

    def showLoading(self, show: bool = True) -> None:
        if show:
            print("Загрузка...")
        else:
            print("Загрузка завершена")


class UserManagementView:
    def __init__(self):
        self.usersTable: List[Dict[str, str]] = []
        self.searchPanel: Dict[str, str] = {"query": "", "filter": "all"}

    def updateUsersTable(self, users: List[Dict[str, str]]) -> None:
        self.usersTable = users
        print(f"Таблица пользователей обновлена. Всего пользователей: {len(users)}")

    def showAddUserDialog(self) -> Dict[str, str]:
        print("Диалог добавления пользователя открыт")
        return {"name": "", "email": "", "role": "user"}

    def showEditUserDialog(self, user_id: str) -> Optional[Dict[str, str]]:
        for user in self.usersTable:
            if user.get("id") == user_id:
                print(f"Редактирование пользователя: {user.get('name')}")
                return user
        return None


class ReportView:
    def __init__(self):
        self.reportContainer: Dict[str, Any] = {"data": {}, "charts": []}
        self.diagramContainer: Dict[str, List[float]] = {"values": [], "labels": []}

    def updateResults(self, results: Dict[str, Any]) -> None:
        self.reportContainer["data"] = results
        print(f"Результаты отчета обновлены: {list(results.keys())}")

    def showReport(self) -> None:
        print("Отчет:")
        for key, value in self.reportContainer["data"].items():
            print(f"  {key}: {value}")

    def exportReport(self, format: str = "pdf") -> str:
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        print(f"Отчет экспортирован как {filename}")
        return filename

    def shareReport(self, platform: str = "email") -> None:
        print(f"Отчет отправлен через {platform}")


class NavigationView:
    def __init__(self):
        self.menuItems: List[Dict[str, str]] = [
            {"name": "Главная", "url": "/"},
            {"name": "Опросы", "url": "/surveys"},
            {"name": "Аналитика", "url": "/analytics"}
        ]
        self.breadcrumbs: List[str] = ["Главная"]

    def updateMenu(self, new_items: List[Dict[str, str]]) -> None:
        self.menuItems.extend(new_items)
        print(f"Меню обновлено. Всего пунктов: {len(self.menuItems)}")

    def showBreadcrumbs(self) -> None:
        print("Навигация: " + " > ".join(self.breadcrumbs))

    def updateBreadcrumbs(self, new_crumb: str) -> None:
        self.breadcrumbs.append(new_crumb)
        print(f"Добавлена навигация: {new_crumb}")

    def showUserMenu(self, username: str) -> None:
        print(f"Меню пользователя: {username}")
        print("  • Профиль")
        print("  • Настройки")
        print("  • Выход")


class ReportPreview:
    def __init__(self):
        self.reportContainer: Dict[str, Any] = {"content": "", "style": "default"}

    def showReport(self) -> None:
        print("Предпросмотр отчета:")
        print(f"Стиль: {self.reportContainer['style']}")
        if self.reportContainer['content']:
            print(f"Содержимое: {self.reportContainer['content'][:50]}...")

    def updateReport(self, content: str) -> None:
        self.reportContainer["content"] = content
        print(f"Отчет обновлен. Длина: {len(content)} символов")

    def configureReport(self, style: str, options: Dict[str, Any]) -> None:
        self.reportContainer["style"] = style
        self.reportContainer.update(options)
        print(f"Отчет настроен. Стиль: {style}, Опции: {list(options.keys())}")


class AuthView:
    def __init__(self):
        self.loginForm: Dict[str, str] = {"username": "", "password": ""}
        self.registrationForm: Dict[str, str] = {"email": "", "password": "", "confirm_password": ""}

    def showLoginForm(self) -> Dict[str, str]:
        print("Форма входа показана")
        return self.loginForm.copy()

    def showRegistrationForm(self) -> Dict[str, str]:
        print("Форма регистрации показана")
        return self.registrationForm.copy()

    def showForgotPasswordForm(self) -> Dict[str, str]:
        print("Форма восстановления пароля показана")
        return {"email": ""}

    def processAuthenticationResult(self, success: bool, message: str) -> None:
        if success:
            print(f"Аутентификация успешна: {message}")
        else:
            print(f"Аутентификация не удалась: {message}")


class SystemSettingsView:
    def __init__(self):
        self.settingsForm: Dict[str, Any] = {
            "theme": "light",
            "language": "ru",
            "notifications": True
        }

    def updateSettings(self, new_settings: Dict[str, Any]) -> None:
        self.settingsForm.update(new_settings)
        print(f"Настройки обновлены: {new_settings}")

    def showSettings(self) -> None:
        print("Текущие настройки системы:")
        for key, value in self.settingsForm.items():
            print(f"  {key}: {value}")

    def saveSettingsToConfig(self) -> Dict[str, Any]:
        print("Настройки сохранены в конфигурационный файл")
        return self.settingsForm.copy()

