import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime
from controller.participant.participant_state import ParticipantState


class ParticipantHistory:

    def __init__(self):
        self.participant_state = ParticipantState()
        self.organizer_storage = None
        self._init_storage()

    def _init_storage(self):
        """Инициализация хранилища"""
        try:
            from controller.organizer.organizer_pages import OrganizerStorage
            self.organizer_storage = OrganizerStorage()
        except ImportError:
            st.warning("Хранилище организатора недоступно")

    def show(self):
        """Страница истории опросов для участника"""
        self.participant_state.init_session_state()

        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 30px;'>История пройденных опросов</h1>",
            unsafe_allow_html=True
        )

        self._display_history_filters()
        self._display_survey_history()
        self._display_overall_stats()

    def _display_history_filters(self):
        """Отображение фильтров истории"""
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            search_query = st.text_input("Поиск по названию", placeholder="Введите название опроса")
            st.session_state.history_search = search_query

        with col_filter2:
            status_filter = st.selectbox(
                "Статус",
                ["Все", "Завершен", "В процессе", "Прерван"]
            )
            st.session_state.history_status = status_filter

    def _display_survey_history(self):
        """Отображение истории опросов"""
        history_data = self._prepare_history_data()
        filtered_history = self._filter_history_data(history_data)

        if filtered_history:
            for i, survey in enumerate(filtered_history):
                self._display_history_survey_card(survey, i)
        else:
            self._display_no_history_message()

    def _prepare_history_data(self):
        """Подготовка данных истории"""
        history_data = st.session_state.completed_surveys

        if not history_data:
            history_data = self._generate_demo_history_data()

        return history_data

    def _generate_demo_history_data(self):
        """Генерация демо-данных истории"""
        demo_history = []
        real_surveys = st.session_state.get('real_surveys', [])

        for survey in real_surveys:
            survey_id = survey.get('id', '')
            if survey_id and self.organizer_storage:
                survey_data = self.organizer_storage.generate_real_survey_data(survey_id)
                if survey_data['total_responses'] > 0:
                    demo_history.append({
                        "id": survey_id,
                        "title": survey.get('name', 'Без названия'),
                        "date": datetime.now().strftime("%d.%m.%Y"),
                        "status": "Завершен",
                        "score": f"{random.randint(70, 95)}/100",
                        "time": f"{random.randint(5, 20)} мин",
                        "questions": len(survey.get('questions', [])),
                        "points": 10,
                        "raw_score": random.randint(70, 95),
                        "time_spent": random.randint(5, 20)
                    })

        return demo_history

    def _filter_history_data(self, history_data):
        """Фильтрация данных истории"""
        filtered_history = history_data

        if st.session_state.get('history_status', 'Все') != "Все":
            filtered_history = [h for h in filtered_history
                                if h.get("status") == st.session_state.history_status]

        if st.session_state.get('history_search'):
            search_query = st.session_state.history_search.lower()
            filtered_history = [h for h in filtered_history
                                if search_query in h.get("title", "").lower()]

        return filtered_history

    def _display_history_survey_card(self, survey, index):
        """Отображение карточки опроса в истории"""
        status_color = self._get_status_color(survey.get("status", "Завершен"))
        score_color = self._get_score_color(survey.get('raw_score', 0))

        html = f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; 
                        align-items: flex-start; margin-bottom: 15px;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 5px 0; color: #2c3e50;">
                        {survey.get('title', 'Без названия')}
                    </h4>
                    <div style="display: flex; gap: 15px; font-size: 13px; color: #7f8c8d;">
                        <span>📅 {survey.get('date', 'Дата неизвестна')}</span>
                        <span>⏱️ {survey.get('time', 'Время неизвестно')}</span>
                        <span>📝 {survey.get('questions', 0)} вопросов</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="background: {status_color}; color: white; 
                                padding: 5px 12px; border-radius: 20px; 
                                font-size: 12px; font-weight: bold; margin-bottom: 5px;">
                        {survey.get('status', 'Завершен')}
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: {score_color};">
                        {survey.get('score', '0/100')}
                    </div>
                    <div style="font-size: 12px; color: #7f8c8d;">
                        +{survey.get('points', 0)} баллов
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        self._display_history_actions(survey, index)

    def _get_status_color(self, status):
        """Получение цвета статуса"""
        if status == "Завершен":
            return "#27ae60"
        elif status == "В процессе":
            return "#667eea"
        else:
            return "#e74c3c"

    def _get_score_color(self, score_value):
        """Получение цвета оценки"""
        if score_value >= 90:
            return "#27ae60"
        elif score_value >= 70:
            return "#f39c12"
        else:
            return "#e74c3c"

    def _display_history_actions(self, survey, index):
        """Отображение действий в истории"""
        col_hist1, col_hist2, col_hist3 = st.columns(3)

        with col_hist1:
            if st.button("👁️ Просмотр ответов",
                         key=f"view_{index}_{survey.get('id', index)}",
                         use_container_width=True):
                st.session_state.selected_survey_for_view = survey

        with col_hist2:
            pass

        with col_hist3:
            if st.button("📊 Статистика",
                         key=f"stats_{index}_{survey.get('id', index)}",
                         use_container_width=True):
                self._show_survey_statistics(survey)

        st.markdown("<br>", unsafe_allow_html=True)
        self._show_survey_answers(survey)

    def _show_survey_statistics(self, survey):
        """Показ статистики по опросу"""
        st.info(f"Статистика по опросу: {survey.get('title', 'Без названия')}")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Оценка", survey.get('score', '0/100'))
        with col2:
            st.metric("Время", survey.get('time', '0 мин'))
        with col3:
            st.metric("Баллы", f"+{survey.get('points', 0)}")

    def _show_survey_answers(self, survey):
        """Показ ответов на опрос"""
        if ('selected_survey_for_view' in st.session_state and
                st.session_state.selected_survey_for_view.get('id') == survey.get('id')):
            with st.expander("📋 Ответы на вопросы", expanded=True):
                answers = survey.get('answers', {})
                if answers:
                    for j, answer_data in sorted(answers.items()):
                        try:
                            question_num = int(j) + 1
                        except:
                            question_num = j

                        st.markdown(f"**Вопрос {question_num}:** {answer_data.get('question', 'Без вопроса')}")
                        answer = answer_data.get('answer', 'Нет ответа')
                        if isinstance(answer, list):
                            answer = ", ".join(answer)
                        st.markdown(f"**Ответ:** {answer}")
                        st.divider()
                else:
                    st.info("Ответы не сохранены")

    def _display_no_history_message(self):
        """Отображение сообщения об отсутствии истории"""
        st.info("📭 Опросы не найдены по выбранным фильтрам")

        if not st.session_state.completed_surveys:
            html = """
            <div style="text-align: center; padding: 40px; background: #f8f9fa; 
                        border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #7f8c8d;">У вас еще нет пройденных опросов</h3>
                <p style="color: #95a5a6;">Начните проходить опросы на вкладке "Доступные опросы"</p>
                <div style="margin-top: 20px;">
                    <span style="font-size: 48px;">📋</span>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

    def _display_overall_stats(self):
        """Отображение общей статистики"""
        st.markdown("---")
        st.markdown("### 📈 Общая статистика")

        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)

        total_surveys = len(st.session_state.completed_surveys)
        avg_score = st.session_state.user_stats['avg_score']
        total_points = st.session_state.user_points
        total_time = st.session_state.user_stats['total_time']

        with col_stats1:
            history_data = self._prepare_history_data()
            session_change = total_surveys - len(history_data)
            delta = f"+{session_change} за сессию" if session_change > 0 else None
            st.metric("Всего пройдено", f"{total_surveys} опросов", delta)

        with col_stats2:
            if total_surveys > 0:
                delta = f"{'+' if avg_score > 70 else ''}{avg_score - 70:.1f}" if avg_score != 0 else "0"
                st.metric("Средний балл", f"{avg_score:.1f}/100", delta)
            else:
                st.metric("Средний балл", "0/100", "Нет данных")

        with col_stats3:
            history_data = self._prepare_history_data()
            session_points = total_points - sum(h.get('points', 0) for h in history_data if 'id' in h)
            delta = f"+{session_points} за сессию" if session_points > 0 else None
            st.metric("Заработано баллов", f"{total_points}", delta)

        with col_stats4:
            history_data = self._prepare_history_data()
            session_time = total_time - sum(h.get('time_spent', 0) for h in history_data if 'id' in h)
            delta = f"+{session_time} мин за сессию" if session_time > 0 else None
            st.metric("Общее время", f"{total_time} мин", delta)


class ParticipantAnalytics:

    def __init__(self):
        self.participant_state = ParticipantState()

    def show(self):
        self.participant_state.init_session_state()

        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 30px;'>Аналитика и отчеты</h1>",
            unsafe_allow_html=True
        )

        self._display_report_filters()
        self._display_available_reports()
        self._display_personal_analytics()

    def _display_report_filters(self):
        """Отображение фильтров отчетов"""
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            st.session_state.report_type_filter = st.selectbox(
                "Тип отчета",
                ["Все типы", "Сводный", "Аналитический", "Детальный", "Статистический"]
            )

        with col_filter2:
            st.session_state.search_report = st.text_input(
                "Поиск по названию",
                placeholder="Введите название отчета..."
            )

    def _display_available_reports(self):
        """Отображение доступных отчетов"""
        st.markdown("### 📊 Доступные отчеты")

        filtered_reports = self._get_filtered_reports()

        if filtered_reports:
            for report in filtered_reports:
                self._display_report_details(report)
        else:
            st.info("📭 Отчеты не найдены по выбранным фильтрам")

    def _get_filtered_reports(self):
        """Получение отфильтрованных отчетов"""
        filtered_reports = st.session_state.available_reports

        if st.session_state.report_type_filter != "Все типы":
            filtered_reports = [r for r in filtered_reports
                                if r['type'] == st.session_state.report_type_filter]

        if st.session_state.search_report:
            search_term = st.session_state.search_report.lower()
            filtered_reports = [r for r in filtered_reports
                                if search_term in r['title'].lower()]

        return filtered_reports

    def _display_report_details(self, report):
        """Отображение деталей отчета"""
        with st.expander(f"{report['title']} ({report['type']})", expanded=False):
            st.markdown(f"""
            **Описание:** {report['description']}

            **Дата публикации:** {report['date']}

            **Доступ:** {report['access']}
            """)

            self._display_report_content(report)
            self._display_report_actions(report)

    def _display_report_content(self, report):
        """Отображение содержимого отчета"""
        if "удовлетворенности" in report['title'].lower():
            self._display_satisfaction_report()
        elif "демографический" in report['title'].lower():
            self._display_demographic_report()
        elif "общий отчет" in report['title'].lower():
            self._display_general_report()

    def _display_satisfaction_report(self):
        """Отображение отчета об удовлетворенности"""
        st.markdown("#### 📈 Статистика удовлетворенности")

        satisfaction_data = pd.DataFrame({
            'Оценка': ['Очень доволен', 'Доволен', 'Нейтрален', 'Не доволен', 'Очень не доволен'],
            'Процент': [35, 40, 15, 7, 3]
        })

        fig = px.bar(satisfaction_data, x='Оценка', y='Процент',
                     color='Процент', title='Распределение оценок удовлетворенности')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🔑 Ключевые выводы:")
        insights = [
            "📊 75% участников довольны или очень довольны услугами",
            "📈 Удовлетворенность выросла на 15% по сравнению с прошлым кварталом",
            "⭐ Наибольшую оценку получила скорость обслуживания (4.7/5)",
            "🔧 Основные области для улучшения: поддержка клиентов и документация"
        ]
        for insight in insights:
            st.markdown(f"- {insight}")

    def _display_demographic_report(self):
        """Отображение демографического отчета"""
        st.markdown("#### 👥 Демографическое распределение")

        col_demo1, col_demo2 = st.columns(2)

        with col_demo1:
            age_data = pd.DataFrame({
                'Возраст': ['18-25', '26-35', '36-45', '46-55', '56+'],
                'Процент': [25, 35, 20, 15, 5]
            })
            fig1 = px.pie(age_data, values='Процент', names='Возраст',
                          title='Возрастное распределение')
            st.plotly_chart(fig1, use_container_width=True)

        with col_demo2:
            geo_data = pd.DataFrame({
                'Регион': ['Москва', 'СПб', 'Центральный', 'Сибирский', 'Другие'],
                'Процент': [30, 15, 25, 20, 10]
            })
            fig2 = px.bar(geo_data, x='Регион', y='Процент',
                          title='Географическое распределение')
            st.plotly_chart(fig2, use_container_width=True)

    def _display_general_report(self):
        """Отображение общего отчета"""
        st.markdown("#### 📋 Сводная статистика")

        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("Всего опросов", "15")
        with col_sum2:
            st.metric("Всего участников", "2,543")
        with col_sum3:
            st.metric("Средняя оценка", "4.3/5")

        results_data = pd.DataFrame({
            'Опрос': ['Удовлетворенность', 'Качество услуг', 'Обучение', 'Поддержка'],
            'Участников': [1247, 856, 342, 589],
            'Средний балл': [4.5, 4.2, 4.7, 4.0],
            'Завершение': ['89%', '92%', '85%', '88%']
        })
        st.dataframe(results_data, use_container_width=True)

    def _display_report_actions(self, report):
        """Отображение действий с отчетом"""
        col_report1, col_report2 = st.columns(2)

        with col_report1:
            if st.button("📥 Скачать отчет", key=f"download_{report['id']}", use_container_width=True):
                st.success(f"Отчет '{report['title']}' готов к скачиванию")

        with col_report2:
            if st.button("📈 Подробная статистика", key=f"details_{report['id']}", use_container_width=True):
                st.info(f"Детальная статистика по отчету: {report['title']}")

    def _display_personal_analytics(self):
        """Отображение персональной аналитики"""
        st.markdown("---")
        st.markdown("### 📊 Ваша персональная аналитика")

        if st.session_state.completed_surveys:
            self._display_progress_chart()
            self._display_personal_stats()
            self._display_recommendations()
        else:
            st.info("📭 У вас еще нет пройденных опросов. Начните с прохождения доступных опросов!")

    def _display_progress_chart(self):
        """Отображение графика прогресса"""
        progress_data = pd.DataFrame(st.session_state.completed_surveys)

        if len(progress_data) > 1:
            dates, scores = self._extract_progress_data()

            if dates and scores:
                progress_df = pd.DataFrame({'Дата': dates, 'Оценка': scores})

                fig = px.line(progress_df, x='Дата', y='Оценка',
                              markers=True, title='Ваш прогресс по опросам',
                              labels={'Оценка': 'Оценка (из 100)'})
                st.plotly_chart(fig, use_container_width=True)

    def _extract_progress_data(self):
        """Извлечение данных для графика прогресса"""
        dates = []
        scores = []

        for survey in st.session_state.completed_surveys:
            try:
                date_str = survey['date'].split()[0]
                dates.append(date_str)
                scores.append(survey.get('raw_score', 0))
            except:
                continue

        return dates, scores

    def _display_personal_stats(self):
        """Отображение персональной статистики"""
        st.markdown("#### 📈 Ваша статистика по типам опросов")

        col_stat1, col_stat2, col_stat3 = st.columns(3)

        with col_stat1:
            completed_count = len(st.session_state.completed_surveys)
            st.metric("Пройдено опросов", completed_count)

        with col_stat2:
            avg_score = st.session_state.user_stats['avg_score']
            st.metric("Средняя оценка", f"{avg_score:.1f}/100")

        with col_stat3:
            total_time = st.session_state.user_stats['total_time']
            st.metric("Общее время", f"{total_time} мин")

    def _display_recommendations(self):
        """Отображение рекомендаций"""
        st.markdown("#### 💡 Рекомендации для вас")

        recommendations = []

        if len(st.session_state.completed_surveys) < 3:
            recommendations.append("Пройдите еще несколько опросов для получения более точной статистики")

        for rec in recommendations:
            st.markdown(f"- {rec}")