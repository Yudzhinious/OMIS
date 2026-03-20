import streamlit as st
import pandas as pd
import plotly.graph_objects as go


class AdminDashboard:
    def show(self, services, views):
        from controller.admin.storage import SurveyStorage
        storage = SurveyStorage()
        storage.init()

        self._render_dashboard_header()
        self._render_dashboard_metrics()
        self._render_dashboard_content()

    def _render_dashboard_header(self):
        """Рендеринг заголовка дашборда"""
        html = """
        <div style="display: flex; justify-content: space-between; 
                    align-items: center; margin-bottom: 30px;">
            <h1 style="margin: 0;">Панель администратора</h1>
            <div style="color: #7f8c8d; font-size: 14px;">
                Последнее обновление: сегодня, 14:30
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _render_dashboard_metrics(self):
        """Рендеринг метрик дашборда"""
        real_users_count = len(st.session_state.get('registered_users', []))
        real_surveys_count = len(st.session_state.get('real_surveys', []))
        published_surveys_count = len(st.session_state.get('published_surveys', []))

        col1, col2, col3 = st.columns(3)

        metrics_data = [
            (real_users_count, "Зарегистрированных пользователей"),
            (real_surveys_count, "Созданных опросов"),
            (published_surveys_count, "Опубликованных опросов")
        ]

        for i, (value, label) in enumerate(metrics_data):
            with [col1, col2, col3][i]:
                st.markdown(self._create_metric_card(value, label), unsafe_allow_html=True)

    def _create_metric_card(self, value, label):
        """Создание HTML для карточки метрики"""
        return f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    color: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    text-align: center;">
            <div style="font-size: 36px; color: blue; font-weight: bold; margin: 10px 0;">
                {value}
            </div>
            <div style="font-size: 14px; opacity: 0.9;">{label}</div>
        </div>
        """

    def _render_dashboard_content(self):
        """Рендеринг основного содержимого дашборда"""
        col_left, col_right = st.columns([2, 1])

        with col_left:
            self._render_activity_chart()

        with col_right:
            self._render_recent_actions()

    def _render_activity_chart(self):
        """Рендеринг графика активности"""
        st.markdown("### Активность системы (24ч)")

        hours = list(range(24))
        activity_data = pd.DataFrame({
            'Время': [f'{h:02d}:00' for h in hours],
            'Активность': [50, 45, 30, 25, 20, 15, 10, 25, 60, 85, 90, 95,
                           85, 80, 75, 80, 85, 90, 95, 85, 70, 60, 55, 50]
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=activity_data['Время'],
            y=activity_data['Активность'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=None),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0',
                       title='Активность (%)', range=[0, 100]),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_recent_actions(self):
        """Рендеринг последних действий"""
        st.markdown("### Последние действия")

        actions = self._get_recent_actions()

        for i, action in enumerate(actions):
            st.markdown(self._create_action_card(action), unsafe_allow_html=True)

    def _get_recent_actions(self):
        """Получение списка последних действий"""
        registered_users = st.session_state.get('registered_users', [])
        real_surveys = st.session_state.get('real_surveys', [])

        recent_registrations = sorted(
            registered_users,
            key=lambda x: x.get('registration_date', ''),
            reverse=True
        )[:2]

        recent_surveys = sorted(
            real_surveys,
            key=lambda x: x.get('created_date', ''),
            reverse=True
        )[:1]

        actions = []

        for user in recent_registrations:
            actions.append({
                "action": "Новый пользователь",
                "detail": user.get('email', 'user@example.com'),
                "time": "недавно"
            })

        for survey in recent_surveys:
            actions.append({
                "action": "Создан новый опрос",
                "detail": survey.get('name', 'Без названия'),
                "time": "недавно"
            })

        if not actions:
            actions = self._get_demo_actions()

        return actions

    def _get_demo_actions(self):
        """Получение демо-действий"""
        return [
            {
                "action": "Новый пользователь зарегистрирован",
                "detail": "user@example.com",
                "time": "5 мин назад"
            },
            {
                "action": "Опрос опубликован",
                "detail": "Исследование рынка 2024",
                "time": "12 мин назад"
            },
            {
                "action": "Резервное копирование завершено",
                "detail": "Система",
                "time": "1 час назад"
            }
        ]

    def _create_action_card(self, action):
        """Создание HTML для карточки действия"""
        return f"""
        <div style="background: white; border-radius: 8px; padding: 15px; 
                    margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                    border-left: 4px solid #667eea;">
            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 5px;">
                {action['action']}
            </div>
            <div style="font-size: 14px; color: #7f8c8d; margin-bottom: 5px;">
                {action['detail']}
            </div>
            <div style="font-size: 12px; color: #95a5a6;">
                {action['time']}
            </div>
        </div>
        """