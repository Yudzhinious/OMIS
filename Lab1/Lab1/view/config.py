import streamlit as st
from model.view import *
from model.check import *
from model.infrastructure import *
CSS_STYLES = """
<style>
    .stApp {
        background: linear-gradient(90deg, #667eea, #27ae60);
        min-height: 100vh;
    }

    .top-banner {
        background: white !important;
        color: #6a11cb !important;
        padding: 15px 25px;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999 !important;
        width: 100%;
        height: 60px;
        border-bottom: 2px solid #f0f0f0;
    }

    .top-banner-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        position: relative;
    }

    .top-banner-icon {
        font-size: 28px;
        color: #6a11cb;
    }

    .top-banner-title {
        font-size: 22px;
        font-weight: 700;
        color: #6a11cb;
        text-align: center;
    }

    .user-circle {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        border-radius: 50%;
        display: flex !important;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 3px 10px rgba(255, 126, 95, 0.3);
        position: absolute;
        right: 0;
        z-index: 1000000;
    }

    .main .block-container {
        padding-top: 80px !important;
    }

    section[data-testid="stSidebar"] {
        top: 60px !important;
        height: calc(100vh - 60px) !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        transform: translateX(0) !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }

    .stSidebar {
        display: block !important;
    }

    .main {
        margin-left: 250px !important;
    }

    .hide-banner .top-banner {
        display: none !important;
    }

    .hide-banner .main .block-container {
        padding-top: 20px !important;
    }

    .hide-banner section[data-testid="stSidebar"] {
        top: 0 !important;
        height: 100vh !important;
        display: none !important;
    }

    .hide-banner .main {
        margin-left: 0 !important;
    }

    .auth-title {
        text-align: center;
        color: #2c3e50;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #667eea, #27ae60);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .auth-subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .auth-tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #f0f0f0;
    }

    .auth-tab {
        padding: 12px 30px;
        cursor: pointer;
        font-weight: 600;
        color: #7f8c8d;
        transition: all 0.3s ease;
        border-bottom: 3px solid transparent;
    }

    .auth-tab.active {
        color: #667eea;
        border-bottom: 3px solid #667eea;
    }

    .auth-tab:hover {
        color: #667eea;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 16px;
    }

    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .stButton>button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }

    .auth-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        cursor: pointer;
    }

    .auth-link:hover {
        text-decoration: underline;
    }

    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }

    .logo-container {
        text-align: center;
        margin-bottom: 10px;
        font-size: 62px;
    }

    .logo-text {
        font-size: 42px;
        font-weight: 800;
        background: black;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .sidebar-content {
        padding: 1rem;
    }

    .survey-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }

    .survey-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    .report-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }

    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .report-title {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }

    .report-meta {
        font-size: 12px;
        color: #7f8c8d;
    }

    .chart-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }

    .participant-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-top: 4px solid #667eea;
    }

    .participant-stat {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
"""


class RegularUser(User):
    def __init__(self, login: str, email: str, password: str):
        super().__init__(login, email, password)
        self.accessType = AccessType.PARTICIPANT

    def updateProfile(self, new_data: Dict[str, Any]) -> None:
        print(f"Профиль пользователя {self.login} обновлён")

    def changePassword(self, old_password: str, new_password: str) -> bool:
        if self.authenticate(old_password):
            self.passwordHash = hash(new_password)
            return True
        return False


@st.cache_resource
def init_views():
    views = {
        'survey_editor': SurveyEditorView(),
        'analytics_dashboard': AnalyticsDashboardView(),
        'notification_view': NotificationView(),
        'survey_creation': SurveyCreationView(),
        'system_monitoring': SystemMonitoringView(),
        'survey_history': SurveyHistoryView(),
        'user_management': UserManagementView(),
        'report_view': ReportView(),
        'navigation_view': NavigationView(),
        'auth_view': AuthView(),
        'system_settings': SystemSettingsView()
    }
    return views


@st.cache_resource
def init_services():
    services = {
        'logger': Logger(),
        'cache': CacheService(),
        'auth': AuthenticationService(),
        'file': FileService(),
        'notification': NotificationService(),
        'session': SessionManager(),
        'stats': StatisticsEngine(),
        'survey_service': SurveyService(),
        'validation': ValidationService(),
        'report_gen': ReportGenerator(),
        'chart': ChartService()
    }
    services['logger'].logInfo("Сервисы инициализированы")
    return services


def init_app():
    """Инициализация приложения"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    services = init_services()
    views = init_views()
    return services, views


def init_session_state():
    """Инициализация состояния сессии"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'current_survey' not in st.session_state:
        st.session_state.current_survey = None
    if 'surveys' not in st.session_state:
        st.session_state.surveys = []
    if 'users' not in st.session_state:
        st.session_state.users = []
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    if 'survey_preview' not in st.session_state:
        st.session_state.survey_preview = {}
    if 'saved_reports' not in st.session_state:
        st.session_state.saved_reports = []
    if 'saved_surveys' not in st.session_state:
        st.session_state.saved_surveys = []


def get_role_info():
    """Определение информации о роли пользователя"""
    if st.session_state.is_authenticated and st.session_state.current_user:
        if st.session_state.user_role == "admin":
            role_text = "Admin"
            user_initial = st.session_state.current_user.login[0].upper() if hasattr(st.session_state.current_user,
                                                                                     'login') and st.session_state.current_user.login else "A"
        elif st.session_state.user_role == "organizer":
            role_text = "Organizer"
            user_initial = st.session_state.current_user.login[0].upper() if hasattr(st.session_state.current_user,
                                                                                     'login') and st.session_state.current_user.login else "O"
        elif st.session_state.user_role == "participant":
            role_text = "Participant"
            user_initial = st.session_state.current_user.login[0].upper() if hasattr(st.session_state.current_user,
                                                                                     'login') and st.session_state.current_user.login else "P"
        else:
            role_text = "User"
            user_initial = "U"
    else:
        role_text = "Guest"
        user_initial = "G"

    return role_text, user_initial