import streamlit as st
from datetime import datetime

class UserManager:
    def show_page(self, services, views):
        """Страница управления пользователями"""
        st.markdown("## Управление пользователями")

        if 'user_management' in views:
            views['user_management'].updateUsersTable(st.session_state.users)

        current_user = st.session_state.current_user
        is_admin = (current_user and hasattr(current_user, '__class__') and
                    current_user.__class__.__name__ == "Administrator")

        if not is_admin:
            st.error("⚠️ Доступно только для администраторов")
            if 'notification_view' in views:
                views['notification_view'].showError("⚠️ Доступно только для администраторов")
            return

        tab1, tab2 = st.tabs(["👥 Пользователи", "🔐 Права доступа"])

        with tab1:
            self._show_users_management(services, views, current_user)

    def create_demo(self):
        """Создание демонстрационных пользователей"""
        return [
            {
                "id": "demo_1",
                "login": "admin",
                "email": "admin@surveypro.ru",
                "role": "Администратор",
                "status": "Активен",
                "registration_date": "15.10.2024",
                "last_login": "Сегодня",
                "surveys": 24,
                "is_real_user": False
            },
            {
                "id": "demo_2",
                "login": "organizer",
                "email": "org@surveypro.ru",
                "role": "Организатор опросов",
                "status": "Активен",
                "registration_date": "08.11.2024",
                "last_login": "10.01.2025",
                "surveys": 12,
                "is_real_user": False
            },
            {
                "id": "demo_3",
                "login": "user",
                "email": "user@surveypro.ru",
                "role": "Участник опросов",
                "status": "Активен",
                "registration_date": "20.11.2024",
                "last_login": "11.01.2025",
                "surveys": 15,
                "is_real_user": False
            }
        ]

    def update_status(self, user_id, new_status):
        """Обновление статуса пользователя"""
        if 'registered_users' not in st.session_state:
            return

        for i, user in enumerate(st.session_state.registered_users):
            if user.get('id') == user_id:
                st.session_state.registered_users[i]['status'] = new_status
                break

    def update(self, user_id, updates):
        """Обновление данных пользователя"""
        if 'registered_users' not in st.session_state:
            return

        for i, user in enumerate(st.session_state.registered_users):
            if user.get('id') == user_id:
                for key, value in updates.items():
                    st.session_state.registered_users[i][key] = value
                break

    def delete_user(self, user_id):
        """Удаление пользователя"""
        if 'registered_users' not in st.session_state:
            return

        st.session_state.registered_users = [
            u for u in st.session_state.registered_users
            if u.get('id') != user_id
        ]

    def _show_users_management(self, services, views, admin_user):
        """Управление пользователями"""
        if 'registered_users' not in st.session_state:
            st.session_state.registered_users = []

        self._render_users_management_header()
        self._render_add_user_form()
        self._render_users_filter()
        self._render_users_list()

    def _render_users_management_header(self):
        """Рендеринг заголовка управления пользователями"""
        col_title, col_stats = st.columns([3, 1])
        with col_title:
            st.markdown("")

    def _render_add_user_form(self):
        """Рендеринг формы добавления пользователя"""
        if st.button("➕ Добавить нового пользователя", type="primary", use_container_width=True):
            show_form = st.session_state.get('show_add_user_form', False)
            st.session_state.show_add_user_form = not show_form

        if not st.session_state.get('show_add_user_form', False):
            return

        with st.expander("📝 Форма добавления пользователя", expanded=True):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_login = st.text_input("Логин *", placeholder="username")
                    new_email = st.text_input("Email *", placeholder="user@example.com")

                with col2:
                    new_role = st.selectbox("Роль *",
                                            ["Участник опросов", "Организатор опросов", "Администратор"])
                    new_status = st.selectbox("Статус", ["Активен", "Неактивен"])

                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    new_password = st.text_input("Пароль *", type="password")
                with col_pass2:
                    confirm_password = st.text_input("Подтвердите пароль *", type="password")

                submitted = st.form_submit_button("Создать пользователя", use_container_width=True)
                if submitted:
                    self._handle_user_creation(new_login, new_email, new_role,
                                               new_status, new_password, confirm_password)

    def _handle_user_creation(self, login, email, role, status, password, confirm_password):
        """Обработка создания пользователя"""
        if not login or not email or not password:
            st.error("Заполните все обязательные поля (отмечены *)")
            return

        if password != confirm_password:
            st.error("Пароли не совпадают!")
            return

        real_users = st.session_state.registered_users
        new_user_id = f"user_{len(real_users) + 1}"
        new_user = {
            'id': new_user_id,
            'login': login,
            'email': email,
            'role': role,
            'status': status,
            'registration_date': datetime.now().strftime("%d.%m.%Y"),
            'last_login': "Сегодня",
            'surveys': 0,
            'is_real_user': True
        }

        st.session_state.registered_users.append(new_user)
        st.success(f"Пользователь {login} успешно создан!")
        st.session_state.show_add_user_form = False
        st.rerun()

    def _render_users_filter(self):
        """Рендеринг фильтров пользователей"""
        col_top1, col_top2, col_top3, col_top4 = st.columns([2, 1, 1, 1])

        with col_top1:
            search_query = st.text_input(
                "Поиск пользователей",
                placeholder="Логин, email или роль...",
                label_visibility="collapsed"
            )
            st.session_state.users_search_query = search_query

        with col_top2:
            filter_role = st.selectbox(
                "Роль",
                ["Все роли", "Администратор", "Организатор опросов", "Участник опросов"],
                label_visibility="collapsed"
            )
            st.session_state.users_filter_role = filter_role

        with col_top3:
            filter_status = st.selectbox(
                "Статус",
                ["Все статусы", "Активен", "Неактивен", "Заблокирован"],
                label_visibility="collapsed"
            )
            st.session_state.users_filter_status = filter_status

        with col_top4:
            if st.button("🔄 Обновить", use_container_width=True):
                st.success("Список пользователей обновлен!")
                st.rerun()

        st.divider()

    def _render_users_list(self):
        """Рендеринг списка пользователей"""
        real_users = st.session_state.registered_users
        filtered_users = self._filter_users(real_users)

        if not filtered_users:
            filtered_users = self.create_demo()
            st.info("Пока нет зарегистрированных пользователей. Отображаются демо-данные.")

        self._render_users_stats(filtered_users)
        self._render_users_cards(filtered_users)
        self._render_user_edit_form(filtered_users)

    def _filter_users(self, users):
        """Фильтрация пользователей"""
        filtered_users = users.copy()

        search_query = st.session_state.get('users_search_query', '')
        if search_query:
            search_lower = search_query.lower()
            filtered_users = [
                u for u in filtered_users
                if search_lower in u.get("login", "").lower()
                   or search_lower in u.get("email", "").lower()
                   or search_lower in u.get("role", "").lower()
            ]

        filter_role = st.session_state.get('users_filter_role', 'Все роли')
        if filter_role != "Все роли":
            role_mapping = {
                "Администратор": "Администратор",
                "Организатор опросов": "Организатор опросов",
                "Участник опросов": "Участник опросов"
            }
            target_role = role_mapping.get(filter_role, filter_role)
            filtered_users = [u for u in filtered_users if u.get("role") == target_role]

        filter_status = st.session_state.get('users_filter_status', 'Все статусы')
        if filter_status != "Все статусы":
            filtered_users = [u for u in filtered_users if u.get("status", "Активен") == filter_status]

        return filtered_users

    def _render_users_stats(self, users):
        """Рендеринг статистики пользователей"""
        active_count = sum(1 for u in users if u.get("status", "Активен") == "Активен")
        real_count = sum(1 for u in users if u.get('is_real_user', False))

        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Всего пользователей", len(users))
        with col_stat2:
            st.metric("Активных", active_count)
        with col_stat3:
            st.metric("Неактивных", len(users) - active_count)

    def _render_users_cards(self, users):
        """Рендеринг карточек пользователей"""
        for user in users:
            with st.container():
                col_user1, col_user2, col_user3 = st.columns([1, 3, 2])

                with col_user1:
                    self._render_user_avatar(user)

                with col_user2:
                    self._render_user_info(user)

                with col_user3:
                    self._render_user_status_role(user)
                    self._render_user_actions(user)

                st.divider()

    def _render_user_avatar(self, user):
        """Рендеринг аватара пользователя"""
        avatar_colors = {
            "Администратор": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "Организатор опросов": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            "Организатор": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            "Участник опросов": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
            "Участник": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        }

        login = user.get("login", "")
        initials = login[:2].upper() if len(login) >= 2 else login[0].upper() if login else "??"

        html = f"""
        <div style="width: 60px; height: 60px; 
                    background: {avatar_colors.get(user.get("role", ""), "#667eea")}; 
                    border-radius: 50%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 18px;">
            {initials}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _render_user_info(self, user):
        """Рендеринг информации о пользователе"""
        st.markdown(f"**{user.get('login', 'Без имени')}**")
        st.caption(user.get("email", "Нет email"))

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.caption(f"📅 {user.get('registration_date', 'Нет данных')}")
        with col_info2:
            st.caption(f"🔑 {user.get('last_login', 'Никогда')}")
        with col_info3:
            surveys_count = user.get('surveys', 0)
            st.caption(f"📊 {surveys_count} опросов")

    def _render_user_status_role(self, user):
        """Рендеринг статуса и роли пользователя"""
        status_colors = {
            "Активен": ("green", "✅"),
            "Неактивен": ("red", "❌"),
            "Заблокирован": ("orange", "⚠️")
        }

        role_colors = {
            "Администратор": ("violet", "👑"),
            "Организатор опросов": ("blue", "📊"),
            "Организатор": ("blue", "📊"),
            "Участник опросов": ("green", "👤"),
            "Участник": ("green", "👤")
        }

        status = user.get("status", "Активен")
        status_color, status_icon = status_colors.get(status, ("gray", "❓"))
        role_color, role_icon = role_colors.get(user.get("role", ""), ("gray", "👤"))

        col_status, col_role = st.columns(2)
        with col_status:
            st.markdown(f"{status_icon} {status}")
        with col_role:
            st.markdown(f"{role_icon} {user.get('role', 'Нет роли')}")

    def _render_user_actions(self, user):
        """Рендеринг действий с пользователем"""
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("✏️", key=f"edit_{user.get('id', 'unknown')}", help="Редактировать"):
                st.session_state.selected_user_id = user.get('id', 'unknown')
                st.rerun()

        with col_btn2:
            self._render_block_unblock_button(user)

        with col_btn3:
            if st.button("🗑️", key=f"delete_{user.get('id', 'unknown')}", help="Удалить"):
                st.session_state.user_to_delete = user.get('id', 'unknown')
                st.session_state.user_to_delete_name = user.get('login', 'Пользователь')

        self._render_delete_confirmation(user)

    def _render_block_unblock_button(self, user):
        """Рендеринг кнопки блокировки/разблокировки"""
        status = user.get("status", "Активен")

        if status == 'Активен':
            if st.button("🔒", key=f"block_{user.get('id', 'unknown')}", help="Заблокировать"):
                self.update_status(user.get('id'), 'Заблокирован')
                st.success(f"Пользователь {user.get('login')} заблокирован")
                st.rerun()
        else:
            if st.button("🔓", key=f"unblock_{user.get('id', 'unknown')}", help="Разблокировать"):
                self.update_status(user.get('id'), 'Активен')
                st.success(f"Пользователь {user.get('login')} разблокирован")
                st.rerun()

    def _render_delete_confirmation(self, user):
        """Рендеринг подтверждения удаления"""
        if st.session_state.get('user_to_delete') != user.get('id', 'unknown'):
            return

        with st.expander(f"⚠️ Подтверждение удаления", expanded=True):
            st.warning(f"Вы уверены, что хотите удалить пользователя {st.session_state.user_to_delete_name}?")

            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Да, удалить", type="primary", use_container_width=True):
                    self.delete_user(user.get('id'))
                    st.success(f"Пользователь {st.session_state.user_to_delete_name} удален")
                    self._cleanup_user_delete_state()
                    st.rerun()

            with col_confirm2:
                if st.button("❌ Отмена", type="secondary", use_container_width=True):
                    self._cleanup_user_delete_state()
                    st.rerun()

    def _cleanup_user_delete_state(self):
        """Очистка состояния удаления пользователя"""
        if 'user_to_delete' in st.session_state:
            del st.session_state.user_to_delete
        if 'user_to_delete_name' in st.session_state:
            del st.session_state.user_to_delete_name

    def _render_user_edit_form(self, users):
        """Рендеринг формы редактирования пользователя"""
        if 'selected_user_id' not in st.session_state:
            return

        user_to_edit = next((u for u in users if u.get('id') == st.session_state.selected_user_id), None)
        if not user_to_edit:
            return

        with st.expander(f"Редактирование: {user_to_edit.get('login', 'Пользователь')}", expanded=True):
            with st.form(f"edit_form_{user_to_edit.get('id', 'unknown')}"):
                col_edit1, col_edit2 = st.columns(2)

                with col_edit1:
                    edit_login = st.text_input("Логин", value=user_to_edit.get('login', ''))
                    edit_email = st.text_input("Email", value=user_to_edit.get('email', ''))

                with col_edit2:
                    edit_role = st.selectbox(
                        "Роль",
                        ["Участник опросов", "Организатор опросов", "Администратор"],
                        index=self._get_role_index(user_to_edit.get('role', 'Участник опросов'))
                    )
                    edit_status = st.selectbox(
                        "Статус",
                        ["Активен", "Неактивен", "Заблокирован"],
                        index=["Активен", "Неактивен", "Заблокирован"].index(
                            user_to_edit.get('status', 'Активен')
                        )
                    )

                col_submit1, col_submit2 = st.columns(2)
                with col_submit1:
                    if st.form_submit_button("Сохранить изменения", use_container_width=True):
                        self._handle_user_update(user_to_edit.get('id'), edit_login,
                                                 edit_email, edit_role, edit_status)

                with col_submit2:
                    if st.form_submit_button("Отмена", use_container_width=True, type="secondary"):
                        del st.session_state.selected_user_id
                        st.rerun()

    def _get_role_index(self, role):
        """Получение индекса роли для selectbox"""
        roles = ["Участник опросов", "Организатор опросов", "Администратор"]
        return roles.index(role) if role in roles else 0

    def _handle_user_update(self, user_id, login, email, role, status):
        """Обработка обновления пользователя"""
        updates = {
            'login': login,
            'email': email,
            'role': role,
            'status': status
        }

        self.update(user_id, updates)
        st.success(f"Изменения сохранены для {login}")
        del st.session_state.selected_user_id
        st.rerun()