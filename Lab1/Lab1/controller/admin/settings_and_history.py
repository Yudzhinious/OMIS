import streamlit as st
import pandas as pd


class SettingsManager:

    def show_page(self, services, views):
        """Страница настроек системы"""
        st.markdown("## ⚙️ Настройки системы")

        if 'system_settings' in views:
            views['system_settings'].showSettings()

        tab_set1, tab_set2, tab_set3, tab_set4 = st.tabs(["Основные", "Уведомления", "Интеграции", "Внешний вид"])

        with tab_set1:
            self._render_basic_settings(views)

    def _render_basic_settings(self, views):
        """Рендеринг основных настроек"""
        st.markdown("### Основные настройки")

        col_set1, col_set2 = st.columns(2)

        with col_set1:
            system_name = st.text_input("Название системы", value="SurveyPro")
            domain = st.text_input("Домен", value="surveypro.example.com")
            timezone = st.selectbox("Часовой пояс", ["Москва (UTC+3)", "Лондон (UTC+0)", "Нью-Йорк (UTC-5)"])
            max_file_size = st.number_input("Макс. размер файла (МБ)", min_value=1, max_value=100, value=10)

        with col_set2:
            maintenance_mode = st.checkbox("Включить режим обслуживания", value=False)
            enable_captcha = st.checkbox("Включить капчу", value=True)
            require_email_confirmation = st.checkbox("Требовать подтверждение email", value=True)
            auto_backup = st.checkbox("Автоматическое резервное копирование", value=True)
            backup_frequency = st.number_input("Частота резервного копирования (часов)",
                                               min_value=1, max_value=24, value=6)

        if st.button("💾 Сохранить настройки"):
            new_settings = {
                "system_name": system_name,
                "domain": domain,
                "timezone": timezone,
                "max_file_size": max_file_size,
                "maintenance_mode": maintenance_mode,
                "enable_captcha": enable_captcha,
                "require_email_confirmation": require_email_confirmation,
                "auto_backup": auto_backup,
                "backup_frequency": backup_frequency
            }

            if 'system_settings' in views:
                views['system_settings'].updateSettings(new_settings)
                saved_settings = views['system_settings'].saveSettingsToConfig()

            st.success("Настройки сохранены!")

            if 'notification_view' in views:
                views['notification_view'].showSuccess("Настройки системы сохранены")

            if 'system_settings' in views:
                with st.expander("📋 Просмотр сохраненных настроек"):
                    st.json(saved_settings)


class HistoryManager:

    def show_page(self, services, views):
        """Страница истории для администратора"""
        st.markdown("## 📜 История опросов")

        real_surveys = st.session_state.get('real_surveys', [])

        if not real_surveys:
            st.info("📭 История опросов пуста. Создайте первый опрос!")
            return

        sorted_surveys = sorted(real_surveys,
                                key=lambda x: x.get('created_date', ''),
                                reverse=True)

        history_data = []
        for survey in sorted_surveys[:10]:
            history_data.append({
                "ID": survey.get('id', 'N/A'),
                "Название": survey.get('name', 'Без названия'),
                "Дата создания": survey.get('created_date', 'Неизвестно'),
                "Статус": survey.get('status', 'Неизвестно'),
                "Организатор": survey.get('organizer', 'Неизвестно'),
                "Ответов": survey.get('responses', 0)
            })

        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)

        selected_survey = st.selectbox(
            "Выберите опрос для просмотра",
            [f"{s['ID']} - {s['Название']}" for s in history_data]
        )

        if st.button("👁️ Просмотреть опрос"):
            survey_id = selected_survey.split(' - ')[0]
            survey = next((s for s in sorted_surveys if s['id'] == survey_id), None)
            if survey:
                st.session_state.selected_survey_for_preview = survey
                st.rerun()