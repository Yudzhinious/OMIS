import streamlit as st
from controller.participant.participant_state import ParticipantState


class ParticipantDashboard:

    def __init__(self):
        self.participant_state = ParticipantState()
        self.organizer_storage = None
        self._init_storage()

    def _init_storage(self):
        """Инициализация хранилища организатора"""
        try:
            from controller.organizer.organizer_pages import OrganizerStorage
            self.organizer_storage = OrganizerStorage()
        except ImportError:
            st.warning("Хранилище организатора недоступно")

    def show(self):
        """Отображение дашборда для участника"""
        self.participant_state.init_session_state()

        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 30px;'>Доступные опросы</h1>",
            unsafe_allow_html=True
        )

        self._display_dashboard_stats()
        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1, 2, 1])

        with col_left:
            self._display_achievements()

        with col_center:
            self._display_available_surveys()

        with col_right:
            st.markdown("")

    def _display_dashboard_stats(self):
        """Отображение статистики на дашборде"""
        real_surveys = st.session_state.get('real_surveys', [])
        published_surveys = [s for s in real_surveys
                             if s.get('status') in ['Опубликован', 'Активный', 'Опубликованный']]
        available_count = len(published_surveys)
        achievements = len([s for s in st.session_state.completed_surveys
                            if s.get('raw_score', 0) >= 80])

        col1, col2, col3, col4 = st.columns(4)

        stats_data = [
            (st.session_state.user_stats['total_surveys'], "Пройдено опросов"),
            (available_count, "Доступно сейчас"),
            (st.session_state.user_points, "Баллов заработано"),
            (achievements, "Достижений")
        ]

        for i, (value, label) in enumerate(stats_data):
            with [col1, col2, col3, col4][i]:
                st.markdown(self._create_stat_card_html(value, label), unsafe_allow_html=True)

    def _create_stat_card_html(self, value, label):
        """Создание HTML для карточки статистики"""
        return f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="font-size: 32px; font-weight: bold; color: #667eea;">{value}</div>
            <div style="font-size: 14px; color: #7f8c8d;">{label}</div>
        </div>
        """

    def _display_achievements(self):
        """Отображение достижений"""
        recent_surveys = st.session_state.completed_surveys[-3:] \
            if st.session_state.completed_surveys else []
        achievements = []

        for survey in recent_surveys:
            title = survey['title'][:15] + "..." if len(survey['title']) > 15 else survey['title']
            achievements.append({
                "title": title,
                "description": f"Пройден {survey['date'].split()[0]}",
                "completed": True
            })

        if len(achievements) < 5:
            self._add_demo_achievements(achievements)

        for achievement in achievements[:5]:
            self._display_achievement_card(achievement)

    def _add_demo_achievements(self, achievements):
        """Добавление демо-достижений"""
        demo_achievements = [
            {"title": "Эксперт", "description": "10 опросов",
             "completed": len(st.session_state.completed_surveys) >= 10},
            {"title": "Активный", "description": "7 дней подряд",
             "completed": len(st.session_state.completed_surveys) >= 7},
            {"title": "Отличник", "description": "Средний балл >90",
             "completed": st.session_state.user_stats['avg_score'] > 90},
            {"title": "Быстрый", "description": "Менее 5 мин",
             "completed": any(s.get('time_spent', 0) < 5
                              for s in st.session_state.completed_surveys)},
        ]
        achievements.extend(demo_achievements)

    def _display_achievement_card(self, achievement):
        """Отображение карточки достижения"""
        status_icon = "✅" if achievement["completed"] else "⬜"
        color = "#27ae60" if achievement["completed"] else "#7f8c8d"

        html = f"""
        <div style="background: white; border-radius: 8px; padding: 15px; 
                    margin-bottom: 10px; box-shadow: 0 1px 5px rgba(0,0,0,0.05); 
                    border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; 
                        justify-content: space-between;">
                <div>
                    <strong style="color: {color};">{achievement['title']}</strong><br>
                    <span style="font-size: 12px; color: #7f8c8d;">
                        {achievement['description']}
                    </span>
                </div>
                <div style="font-size: 20px;">{status_icon}</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _display_available_surveys(self):
        """Отображение доступных опросов"""
        real_surveys = st.session_state.get('real_surveys', [])
        published_surveys = [s for s in real_surveys
                             if s.get('status') in ['Опубликован', 'Активный', 'Опубликованный']]

        if not published_surveys:
            st.info("📭 В данный момент нет доступных опросов. Загляните позже!")
            return

        completed_ids = [s.get('id') for s in st.session_state.completed_surveys]

        for i, survey in enumerate(published_surveys):
            survey_id = survey.get('id', '')
            survey_data = self.organizer_storage.generate_real_survey_data(
                survey_id) if survey_id and self.organizer_storage else {'total_responses': 0}
            is_completed = survey_id in completed_ids

            self._display_survey_card(survey, survey_id, survey_data, is_completed, completed_ids)

    def _display_survey_card(self, survey, survey_id, survey_data, is_completed, completed_ids):
        """Отображение карточки опроса"""
        status_color = "#27ae60" if is_completed else "#667eea"
        status_text = "✅ Пройден" if is_completed else "🚀 Начать"

        description, time_display, points = self._get_survey_details(
            survey, survey_id, survey_data, is_completed, completed_ids
        )

        html = f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    border-top: 4px solid {status_color};">
            <div style="display: flex; justify-content: space-between; 
                        align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <h4 style="margin: 0 0 5px 0; color: #2c3e50;">
                        {survey.get('name', 'Без названия')}
                    </h4>
                    <p style="margin: 0; color: #7f8c8d; font-size: 14px;">
                        {description}
                    </p>
                </div>
                <div style="background: {status_color}; color: white; 
                            padding: 5px 12px; border-radius: 20px; 
                            font-size: 12px; font-weight: bold;">
                    {status_text}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; 
                        color: #7f8c8d; font-size: 13px;">
                <div>📝 {len(survey.get('questions', []))} вопросов</div>
                <div>⏱️ {time_display}</div>
                <div>⭐ +{points} баллов</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        self._add_survey_button(survey, survey_id)

    def _get_survey_details(self, survey, survey_id, survey_data, is_completed, completed_ids):
        """Получение деталей опроса"""
        if is_completed:
            completed_info = next(
                (s for s in st.session_state.completed_surveys if s.get('id') == survey_id),
                None
            )
            description = f"Ваша оценка: {completed_info['score']}" if completed_info else "Пройден"
            time_display = "Пройти еще раз"
        else:
            estimated_time = len(survey.get('questions', [])) * 2  # 2 минуты на вопрос
            time_display = f"{estimated_time} мин"
            description = survey.get('description', 'Описание отсутствует')

        points = min(20, len(survey.get('questions', [])) * 2)
        return description, time_display, points

    def _add_survey_button(self, survey, survey_id):
        """Добавление кнопки для прохождения опроса"""
        col_start1, col_start2 = st.columns([3, 1])
        with col_start2:
            if st.button("Пройти", key=f"start_{survey_id}", use_container_width=True):
                st.session_state.selected_survey_for_take = survey
                st.rerun()