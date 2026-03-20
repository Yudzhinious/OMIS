import streamlit as st
from model.check import Administrator, SurveyOrganizer
from view.config import RegularUser


def show_auth_page(services, views):
    """Отображение страницы аутентификации"""
    # Скрываем боковую панель и плашку
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        .main .block-container {
            max-width: 800px;
            padding-top: 20px !important;
            margin-left: 0 !important;
        }

        .top-banner {
            display: none !important;
        }

        .main {
            margin-left: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.markdown(
            '<div class="auth-container" style="background-color: white !important; padding: 40px !important;">',
            unsafe_allow_html=True)
        st.markdown('<div class="logo-container">📊SurveyPro</h2>', unsafe_allow_html=True)
        st.markdown('<div class="logo-container">Платформа интерактивных опросов</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Вход", "Регистрация"])

        with tab_login:
            show_login_form(services, views)

        with tab_register:
            show_register_form(services, views)

        st.markdown('</div>', unsafe_allow_html=True)


def show_login_form(services, views):
    """Отображение формы входа"""
    with st.form("login_form"):
        st.markdown('<h3 style="text-align: center; margin-bottom: 25px; color: #2c3e50;">Вход в систему</h3>',
                    unsafe_allow_html=True)

        login_type = st.radio(
            "Тип входа",
            ["Email", "Логин"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if login_type == "Email":
            username = st.text_input("Email", placeholder="example@email.com")
        else:
            username = st.text_input("Логин", placeholder="username")

        password = st.text_input("Пароль", type="password", placeholder="......")

        col_remember, col_forgot = st.columns([2, 1])
        with col_remember:
            remember = st.checkbox("Запомнить меня")

        login_submitted = st.form_submit_button("Войти в систему", use_container_width=True)

        if login_submitted and username and password:
            process_login(services, views, username, password)

    if st.button("Забыли пароль?", use_container_width=True):
        forgot_form = views['auth_view'].showForgotPasswordForm()
        st.info("Форма восстановления пароля будет добавлена в будущем")


def process_login(services, views, username, password):
    """Обработка входа пользователя"""
    if username == "admin" and password == "admin123":
        admin_user = Administrator("admin", "admin@surveypro.ru", "admin123")
        st.session_state.current_user = admin_user
        st.session_state.is_authenticated = True
        st.session_state.user_role = "admin"
        services['session'].createSession(admin_user.id)
        services['cache'].set(f"user_{admin_user.id}", admin_user)
        services['logger'].logInfo(f"Администратор {username} вошел в систему")

        views['notification_view'].showSuccess("✅ Успешный вход как администратор!")
        views['auth_view'].processAuthenticationResult(True, "Добро пожаловать, администратор!")
        st.success("✅ Успешный вход как администратор!")
        st.rerun()
    elif username == "organizer" and password == "org123":
        organizer_user = SurveyOrganizer("organizer", "org@surveypro.ru", "org123")
        st.session_state.current_user = organizer_user
        st.session_state.is_authenticated = True
        st.session_state.user_role = "organizer"
        services['session'].createSession(organizer_user.id)
        services['logger'].logInfo(f"Организатор {username} вошел в систему")

        views['notification_view'].showSuccess("✅ Успешный вход как организатор опросов!")
        views['auth_view'].processAuthenticationResult(True, "Добро пожаловать, организатор!")
        st.success("✅ Успешный вход как организатор опросов!")
        st.rerun()
    elif username == "user" and password == "user123":
        regular_user = RegularUser("user", "user@surveypro.ru", "user123")
        st.session_state.current_user = regular_user
        st.session_state.is_authenticated = True
        st.session_state.user_role = "participant"
        services['session'].createSession(regular_user.id)
        services['logger'].logInfo(f"Пользователь {username} вошел в систему")

        views['notification_view'].showSuccess("✅ Успешный вход как участник!")
        views['auth_view'].processAuthenticationResult(True, "Добро пожаловать, участник!")
        st.success("✅ Успешный вход как участник!")
        st.rerun()
    else:
        services['logger'].logWarning(f"Неудачная попытка входа: {username}")
        views['notification_view'].showError("❌ Неверный логин или пароль")
        views['auth_view'].processAuthenticationResult(False, "Неверные учетные данные")
        st.error("❌ Неверный логин или пароль")


def show_register_form(services, views):
    """Отображение формы регистрации"""
    with st.form("register_form"):
        st.markdown(
            '<h3 style="text-align: center; margin-bottom: 25px; color: #2c3e50;">Регистрация нового пользователя</h3>',
            unsafe_allow_html=True)

        # Поля формы
        col_email, col_login = st.columns(2)
        with col_email:
            email = st.text_input("Email", placeholder="example@email.com")
        with col_login:
            login = st.text_input("Логин", placeholder="username")

        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            password = st.text_input("Пароль", type="password", placeholder="......", key="reg_pass1")
        with col_pass2:
            confirm_password = st.text_input("Подтвердите пароль", type="password", placeholder="......",
                                             key="reg_pass2")

        role = st.selectbox(
            "Роль",
            ["Участник опросов", "Организатор опросов", "Администратор"],
            help="Выберите роль в системе"
        )

        agree = st.checkbox("Я согласен с условиями использования и политикой конфиденциальности")

        register_submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True)

        if register_submitted:
            process_registration(services, views, email, login, password, confirm_password, role, agree)


def process_registration(services, views, email, login, password, confirm_password, role, agree):
    """Обработка регистрации пользователя"""
    if not agree:
        views['notification_view'].showError("❌ Необходимо принять условия использования")
        st.error("❌ Необходимо принять условия использования")
    elif password != confirm_password:
        views['notification_view'].showError("❌ Пароли не совпадают!")
        st.error("❌ Пароли не совпадают!")
    elif not email or not login or not password:
        views['notification_view'].showError("❌ Заполните все обязательные поля!")
        st.error("❌ Заполните все обязательные поля!")
    else:
        # Определяем тип пользователя
        if role == "Администратор":
            new_user = Administrator(login, email, password)
            role_key = "admin"
        elif role == "Организатор опросов":
            new_user = SurveyOrganizer(login, email, password)
            role_key = "organizer"
        else:
            new_user = RegularUser(login, email, password)
            role_key = "participant"

        services['cache'].set(f"user_{new_user.id}", new_user)

        if 'registered_users' not in st.session_state:
            st.session_state.registered_users = []

        user_metadata = {
            'id': new_user.id,
            'login': new_user.login,
            'email': new_user.email,
            'role': role,
            'role_key': role_key,
            'registration_date': new_user.registrationDate.strftime("%Y-%m-%d %H:%M"),
            'status': 'Активен',
            'is_real_user': True,
            'user_object': new_user
        }

        existing_users = [u for u in st.session_state.registered_users if u['id'] == new_user.id]
        if not existing_users:
            st.session_state.registered_users.append(user_metadata)

        if 'users' not in st.session_state:
            st.session_state.users = []
        st.session_state.users.append(new_user)

        token = services['auth'].authenticateUser(login, password)
        services['session'].createSession(new_user.id)

        st.session_state.current_user = new_user
        st.session_state.is_authenticated = True
        st.session_state.user_role = role_key

        services['logger'].logInfo(f"Новый пользователь зарегистрирован: {login} ({role})")
        views['notification_view'].showSuccess(f"✅ Регистрация успешна! Добро пожаловать, {login}!")
        views['auth_view'].processAuthenticationResult(True, "Регистрация успешна")
        st.success(f"✅ Регистрация успешна! Добро пожаловать, {login}!")
        st.balloons()

        if 'user_management' in views:
            views['user_management'].updateUsersTable(st.session_state.registered_users)

        with st.expander("👤 Информация о профиле", expanded=True):
            user_info = {
                "ID": new_user.id,
                "Логин": new_user.login,
                "Email": new_user.email,
                "Роль": role,
                "Дата регистрации": new_user.registrationDate.strftime("%Y-%m-%d %H:%M")
            }
            st.json(user_info)

        st.info("ℹ️ Здесь была бы отправка подтверждающего email")