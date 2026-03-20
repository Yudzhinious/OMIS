import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
from controller.organizer.organizer_storage import OrganizerStorage


class SurveyManager:

    def __init__(self, storage: OrganizerStorage):
        self.storage = storage

    def show_organizer_surveys(self):
        """Управление опросами для организатора"""
        self.storage.init_data_storage()

        st.markdown("## 📋 Мои опросы")
        self._render_surveys_actions()
        self._render_surveys_filters()
        self._render_surveys_list()

    def _render_surveys_actions(self):
        """Рендеринг действий с опросами"""
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("📝 Создать новый", use_container_width=True):
                st.session_state.selected_menu = "📝 Создать опрос"
                st.rerun()

        with col_btn2:
            if st.button("📥 Импортировать", use_container_width=True):
                st.info("Функция импорта будет реализована")

        with col_btn3:
            if st.button("🔄 Обновить", use_container_width=True):
                st.rerun()

        with col_btn4:
            self._render_export_all_button()

    def _render_export_all_button(self):
        """Рендеринг кнопки экспорта всех опросов"""
        surveys_data = st.session_state.get('real_surveys', [])
        if not surveys_data:
            if st.button("📊 Экспорт всех", use_container_width=True):
                st.info("Нет опросов для экспорта")
            return

        if st.button("📊 Экспорт всех", use_container_width=True):
            json_data = json.dumps(surveys_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Скачать JSON",
                data=json_data,
                file_name=f"Все_опросы_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    def _render_surveys_filters(self):
        """Рендеринг фильтров опросов"""
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            status_filter = st.selectbox("Статус",
                                         ["Все", "Активный", "Опубликован", "Черновик", "Завершен", "Архивный"])

        with col_f2:
            date_filter = st.date_input("Период", [datetime.now() - timedelta(days=30), datetime.now()])

        with col_f3:
            search_query = st.text_input("Поиск", placeholder="Поиск по названию...")

    def _render_surveys_list(self):
        """Рендеринг списка опросов"""
        real_surveys = st.session_state.get('real_surveys', [])

        if not real_surveys:
            st.info("📭 У вас пока нет созданных опросов. Нажмите 'Создать новый' чтобы начать.")
            return

        surveys_list = self._prepare_surveys_list(real_surveys)
        surveys_df = pd.DataFrame(surveys_list)
        filtered_df = self._filter_surveys_df(surveys_df)

        if filtered_df.empty:
            st.info("📭 Опросы не найдены по выбранным фильтрам")
            return

        self._render_surveys_dataframe(filtered_df)
        self._render_survey_management(filtered_df, real_surveys)

    def _prepare_surveys_list(self, surveys):
        """Подготовка списка опросов"""
        surveys_list = []
        for survey in surveys:
            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            surveys_list.append({
                'Название': survey.get('name', 'Без названия'),
                'Статус': survey.get('status', 'Черновик'),
                'Дата создания': survey.get('created_date', 'Неизвестно'),
                'Дата окончания': survey.get('end_date', '-'),
                'Ответов': survey_data['total_responses'],
                'Завершение': f"{survey_data['completion_rate']:.0f}%",
                'Действия': '📊 ✏️ 🗑️'
            })
        return surveys_list

    def _filter_surveys_df(self, df):
        """Фильтрация DataFrame опросов"""
        # В реальном коде здесь будет логика фильтрации
        return df

    def _render_surveys_dataframe(self, df):
        """Рендеринг DataFrame опросов"""
        st.dataframe(df, use_container_width=True, hide_index=True)

    def _render_survey_management(self, filtered_df, real_surveys):
        """Рендеринг управления опросом"""
        st.markdown("### 🔧 Управление опросом")

        survey_names = filtered_df['Название'].tolist()
        if not survey_names:
            return

        selected_survey = st.selectbox("Выберите опрос:", survey_names)
        if not selected_survey:
            return

        original_survey = next((s for s in real_surveys if s.get('name') == selected_survey), None)
        if not original_survey:
            return

        self._render_survey_actions_buttons(original_survey, selected_survey)

    def _render_survey_actions_buttons(self, survey, survey_name):
        """Рендеринг кнопок действий с опросом"""
        col_action1, col_action2, col_action3 = st.columns(3)

        with col_action1:
            if st.button("📊 Статистика", use_container_width=True):
                self.show_survey_statistics_organizer(survey['id'])

        with col_action2:
            if st.button("✏️ Редактировать", use_container_width=True):
                st.session_state.editing_survey = survey
                st.session_state.selected_menu = "📝 Создать опрос"
                st.rerun()

        with col_action3:
            self._render_delete_survey_button(survey, survey_name)

    def _render_delete_survey_button(self, survey, survey_name):
        """Рендеринг кнопки удаления опроса"""
        if st.button("🗑️ Удалить", use_container_width=True):
            confirm_key = f"del_confirm_{survey['id']}"
            if st.checkbox(f"Вы уверены, что хотите удалить опрос '{survey_name}'?", key=confirm_key):
                st.session_state.real_surveys = [
                    s for s in st.session_state.real_surveys
                    if s['id'] != survey['id']
                ]
                st.success(f"Опрос '{survey_name}' удален")
                st.rerun()

    def show_survey_statistics_organizer(self, survey_id):
        """Показать статистику опроса для организатора"""
        self.storage.init_data_storage()

        survey = self._get_survey_by_id(survey_id)
        if not survey:
            st.error("Опрос не найден")
            return

        survey_data = self.storage.generate_real_survey_data(survey_id)

        st.markdown(f"### 📊 Статистика: {survey.get('name', 'Опрос')}")
        self._render_survey_basic_metrics(survey_data)
        self._render_survey_demographics(survey_data)
        self._render_survey_trends(survey_data)
        self._render_survey_report_button(survey, survey_data)

    def _get_survey_by_id(self, survey_id):
        """Получение опроса по ID"""
        for survey in st.session_state.get('real_surveys', []):
            if survey.get('id') == survey_id:
                return survey
        return None

    def _render_survey_basic_metrics(self, survey_data):
        """Рендеринг основных метрик опроса"""
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего ответов", survey_data['total_responses'])

        with col2:
            st.metric("Процент завершения", f"{survey_data['completion_rate']:.1f}%")

        with col3:
            st.metric("Среднее время", f"{survey_data['average_time'] / 60:.1f} мин")

    def _render_survey_demographics(self, survey_data):
        """Рендеринг демографических данных опроса"""
        st.markdown("#### 👥 Демографические данные")

        if survey_data['demographics']['age']:
            self._render_age_distribution(survey_data)

        if survey_data['demographics']['gender']:
            self._render_gender_distribution(survey_data)

    def _render_age_distribution(self, survey_data):
        """Рендеринг распределения по возрасту"""
        st.markdown("**Возрастное распределение:**")
        age_df = pd.DataFrame(
            list(survey_data['demographics']['age'].items()),
            columns=['Возраст', 'Количество']
        )
        age_df = age_df.sort_values('Возраст')
        fig_age = px.bar(age_df, x='Возраст', y='Количество', title='Распределение по возрасту')
        st.plotly_chart(fig_age, use_container_width=True)

    def _render_gender_distribution(self, survey_data):
        """Рендеринг распределения по полу"""
        st.markdown("**Гендерное распределение:**")
        gender_df = pd.DataFrame(
            list(survey_data['demographics']['gender'].items()),
            columns=['Пол', 'Количество']
        )
        fig_gender = px.pie(gender_df, values='Количество', names='Пол', title='Распределение по полу')
        st.plotly_chart(fig_gender, use_container_width=True)

    def _render_survey_trends(self, survey_data):
        """Рендеринг трендов опроса"""
        st.markdown("#### 📈 Тренды ответов")

        if not survey_data.get('daily_trends'):
            return

        trends_df = pd.DataFrame(
            list(survey_data['daily_trends'].items()),
            columns=['Дата', 'Ответов']
        )
        trends_df['Дата'] = pd.to_datetime(trends_df['Дата'])
        trends_df = trends_df.sort_values('Дата')

        fig_trends = px.line(
            trends_df, x='Дата', y='Ответов',
            title='Динамика ответов по дням',
            markers=True
        )
        st.plotly_chart(fig_trends, use_container_width=True)

    def _render_survey_report_button(self, survey, survey_data):
        """Рендеринг кнопки отчета по опросу"""
        if not st.button("📥 Скачать отчет по опросу в TXT"):
            return

        from organizer_reports import ReportGenerator
        report_generator = ReportGenerator(self.storage)
        txt_content = report_generator.generate_survey_report_txt(survey, survey_data)
        st.download_button(
            label="📥 Скачать отчет",
            data=txt_content,
            file_name=f"Отчет_{survey.get('name', 'Опрос').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )