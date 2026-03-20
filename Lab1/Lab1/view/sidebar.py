import streamlit as st

def show_sidebar(services, views, role_text, user_initial):
    """Отображение боковой панели"""
    with st.sidebar:
        # Используем NavigationView для навигации
        views['navigation_view'].showBreadcrumbs()

        views['notification_view'].showNotification(f"Роль: {st.session_state.user_role}")
        st.info(f"Роль: {st.session_state.user_role}")

        if st.button("Выйти из системы"):
            logout_user(services, views)

        st.markdown("---")

        # Меню в зависимости от роли
        if st.session_state.user_role == "admin":
            menu_options = ["📊 Dashboard", "👥 Пользователи", "📋 Опросы", "📈 Статистика", "⚙️ Настройки"]
        elif st.session_state.user_role == "organizer":
            menu_options = ["📊 Dashboard", "📝 Создать опрос", "📈 Аналитика"]
        else:  # participant
            menu_options = ["📊 Dashboard", "📋 Опросы", "📜 История"]

        selected_menu = st.radio("Меню", menu_options)

    return selected_menu


def logout_user(services, views):
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    services['auth'].logout("token")
    services['session'].destroySession("user_id")
    views['notification_view'].showSuccess("Вы успешно вышли из системы")
    views['auth_view'].processAuthenticationResult(False, "Сессия завершена")
    st.rerun()