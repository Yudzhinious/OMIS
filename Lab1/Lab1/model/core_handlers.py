import streamlit as st
from controller.participant.participant_pages import (
    ParticipantDashboard,
    ParticipantSurvey,
    ParticipantHistory
)
from controller.organizer.organizer_pages import (
    OrganizerStorage,
    DashboardRenderer,
    AnalyticsRenderer,
    SurveyManager as OrganizerSurveyManager,
    ReportManager
)
from controller.admin.storage import SurveyStorage
from controller.admin.user_management import UserManager
from controller.admin.survey_management import SurveyManager
from controller.admin.survey_creation import SurveyCreator
from controller.admin.settings_and_history import SettingsManager, HistoryManager
from controller.admin.admin_dashboard import AdminDashboard


survey_storage = SurveyStorage()
user_manager = UserManager()
admin_dashboard = AdminDashboard()
survey_manager = SurveyManager()
survey_creator = SurveyCreator()
settings_manager = SettingsManager()
history_manager = HistoryManager()

organizer_storage = OrganizerStorage()
dashboard_renderer = DashboardRenderer(organizer_storage)
analytics_renderer = AnalyticsRenderer(organizer_storage)
survey_manager_organizer = OrganizerSurveyManager(organizer_storage)
report_manager = ReportManager(organizer_storage)
participant_dashboard = ParticipantDashboard()
participant_survey = ParticipantSurvey()
participant_history = ParticipantHistory()


def show_content(selected_menu, services, views):
    """Отображение основного контента в зависимости от выбранного меню"""
    survey_storage.init()

    menu_handlers = {
        "📊 Dashboard": lambda: show_dashboard(services, views),
        "👥 Пользователи": lambda: show_users_page(services, views),
        "📋 Опросы": lambda: show_surveys_page(services, views),
        "📈 Отчеты": lambda: show_reports_page(services, views),
        "📈 Аналитика": lambda: analytics_renderer.show_organizer_analytics(),
        "📈 Статистика": lambda: analytics_renderer.show_organizer_analytics(),
        "⚙️ Настройки": lambda: show_settings_page(services, views),
        "📝 Создать опрос": lambda: show_create_survey_page(services, views),
        "📜 История": lambda: show_history_page(services, views)
    }

    handler = menu_handlers.get(selected_menu)
    if handler:
        handler()


def show_dashboard(services, views):
    """Отображение дашборда"""
    if st.session_state.user_role == "participant":
        participant_dashboard.show()
    elif st.session_state.user_role == "organizer":
        dashboard_renderer.show_organizer_dashboard()
    else:
        admin_dashboard.show(services, views)


def show_users_page(services, views):
    """Страница управления пользователями"""
    user_manager.show_page(services, views)


def show_surveys_page(services, views):
    """Страница опросов"""
    survey_storage.init()

    if st.session_state.user_role == "participant":
        participant_survey.show()
    elif st.session_state.user_role == "organizer":
        survey_manager_organizer.show_organizer_surveys()
    else:
        survey_manager.show_page(services, views)


def show_reports_page(services, views):
    """Страница отчетов"""
    if st.session_state.user_role == "organizer":
        report_manager.show_organizer_reports()


def show_settings_page(services, views):
    """Страница настроек системы"""
    settings_manager.show_page(services, views)


def show_create_survey_page(services, views):
    """Страница создания опроса"""
    survey_creator.show_page(services, views)


def show_history_page(services, views):
    """Страница истории"""
    if st.session_state.user_role == "participant":
        participant_history.show()
    elif st.session_state.user_role == "organizer":
        analytics_renderer.show_organizer_analytics()
    else:
        history_manager.show_page(services, views)