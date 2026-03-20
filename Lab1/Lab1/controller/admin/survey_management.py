import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from controller.admin.storage import SurveyStorage


class SurveyManager:
    def __init__(self):
        self.storage = SurveyStorage()

    def show_page(self, services, views):
        """Управление опросами для администратора"""
        self.storage.init()

        st.markdown("## 📋 Управление опросами")

        real_surveys = st.session_state.get('real_surveys', [])
        self._render_surveys_stats(real_surveys)
        st.divider()

        filtered_surveys = self._filter_surveys(real_surveys)
        self._render_surveys_content(real_surveys, filtered_surveys)

    def show_details(self, survey):
        """Показать детальную информацию об опросен"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**ID:** {survey.get('id', 'N/A')}")
            st.markdown(f"**Название:** {survey.get('name', 'Без названия')}")
            st.markdown(f"**Статус:** {survey.get('status', 'Неизвестно')}")
            st.markdown(f"**Тип:** {survey.get('type', 'Неизвестно')}")

        with col2:
            st.markdown(f"**Создан:** {survey.get('created_date', 'Неизвестно')}")
            st.markdown(f"**Завершение:** {survey.get('end_date', 'Не указано')}")
            st.markdown(f"**Вопросов:** {len(survey.get('questions', []))}")
            st.markdown(f"**Ответов:** {survey.get('responses', 0)}")

        if survey.get('description'):
            st.markdown(f"**Описание:** {survey.get('description')}")

        if survey.get('organizer'):
            st.markdown(f"**Организатор:** {survey.get('organizer')}")

        self._render_survey_settings(survey)
        self._render_survey_questions(survey)

    def show_statistics(self, survey):
        """Показать статистику по опросу"""
        st.markdown(f"### 📊 Статистика: {survey.get('name', 'Опрос')}")

        responses = survey.get('responses', 0)
        completion_rate = np.random.randint(70, 98)
        avg_time = np.random.uniform(2.0, 10.0)

        col_stat1, col_stat2, col_stat3 = st.columns(3)

        with col_stat1:
            st.metric("Всего ответов", responses)

        with col_stat2:
            st.metric("Завершение", f"{completion_rate}%")

        with col_stat3:
            st.metric("Среднее время", f"{avg_time:.1f} мин")

        if responses > 0:
            self._render_responses_chart()

    def show_preview(self, survey):
        """Показать предпросмотр опроса для администратора"""
        st.markdown(f"### 👁️ Предпросмотр опроса: {survey.get('name', 'Без названия')}")

        if survey.get('description'):
            st.info(f"**Описание:** {survey.get('description')}")

        st.markdown("---")
        self._render_survey_preview_info(survey)
        st.markdown("---")
        self._render_survey_preview_questions(survey)
        st.markdown("---")
        self._render_survey_preview_actions(survey)

    def _render_surveys_stats(self, surveys):
        """Рендеринг статистики опросов"""
        active_count = sum(1 for s in surveys if s.get('status') in ['Активен', 'Опубликован'])
        draft_count = sum(1 for s in surveys if s.get('status') == 'Черновик')

        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Всего опросов", len(surveys))
        with col_stat2:
            st.metric("Активных", active_count)
        with col_stat3:
            st.metric("Черновиков", draft_count)

    def _filter_surveys(self, surveys):
        """Фильтрация опросов"""
        col_filters1, col_filters2, col_filters3, col_filters4 = st.columns([2, 1, 1, 1])

        with col_filters1:
            search_query = st.text_input("Поиск по названию или описанию",
                                         placeholder="Введите текст для поиска...")
            st.session_state.surveys_search = search_query

        with col_filters2:
            status_filter = st.selectbox("Статус",
                                         ["Все", "Активен", "Опубликован", "Черновик", "Завершен", "Архивный"])
            st.session_state.surveys_status = status_filter

        with col_filters3:
            type_filter = st.selectbox("Тип", ["Все", "Публичный", "Приватный", "По приглашению"])
            st.session_state.surveys_type = type_filter

        with col_filters4:
            st.markdown("")
            if st.button("🔄 Обновить", use_container_width=True):
                st.rerun()

        filtered_surveys = surveys.copy()

        if search_query:
            search_lower = search_query.lower()
            filtered_surveys = [
                s for s in filtered_surveys
                if search_lower in s.get('name', '').lower()
                   or search_lower in s.get('description', '').lower()
            ]

        if status_filter != "Все":
            filtered_surveys = [s for s in filtered_surveys if s.get('status') == status_filter]

        if type_filter != "Все":
            filtered_surveys = [s for s in filtered_surveys if s.get('type') == type_filter]

        return filtered_surveys

    def _render_surveys_content(self, all_surveys, filtered_surveys):
        """Рендеринг содержимого страницы опросов"""
        if not filtered_surveys:
            self._render_no_surveys_message(all_surveys)
            return

        st.markdown(f"### 📊 Найдено опросов: {len(filtered_surveys)}")

        surveys_table_data = self._prepare_surveys_table_data(filtered_surveys)
        surveys_df = pd.DataFrame(surveys_table_data)

        self._render_surveys_table(surveys_df, filtered_surveys)

    def _render_no_surveys_message(self, all_surveys):
        """Рендеринг сообщения об отсутствии опросов"""
        if all_surveys:
            st.info("Все опросы отфильтрованы. Попробуйте изменить параметры поиска.")
            return

        st.info("📭 Пока нет созданных опросов. Организаторы могут создавать опросы в соответствующем разделе.")

        st.markdown("### Как создать опрос:")
        st.markdown("""
        1. **Организатор** должен войти в систему
        2. Перейти в раздел **"📝 Создать опрос"**
        3. Заполнить информацию об опросе
        4. Добавить вопросы
        5. Сохранить или опубликовать опрос
        6. Созданные опросы появятся здесь
        """)

        self._render_demo_surveys()

    def _render_demo_surveys(self):
        """Рендеринг демо-опросов"""
        st.markdown("### Примеры опросов (демо):")

        demo_surveys = [
            {
                'id': 'SUR-001',
                'name': 'Оценка качества обучения',
                'description': 'Опрос для оценки качества образовательных программ',
                'status': 'Активен',
                'type': 'Публичный',
                'questions': 15,
                'responses': 1245,
                'created_date': '2024-02-15',
                'end_date': '2024-04-15',
                'organizer': 'Иванов И.И.'
            },
            {
                'id': 'SUR-002',
                'name': 'Исследование рынка 2024',
                'description': 'Маркетинговое исследование потребительских предпочтений',
                'status': 'Опубликован',
                'type': 'По приглашению',
                'questions': 20,
                'responses': 892,
                'created_date': '2024-03-01',
                'end_date': '2024-03-31',
                'organizer': 'Петров П.П.'
            }
        ]

        demo_df = pd.DataFrame(demo_surveys)
        st.dataframe(
            demo_df[['id', 'name', 'status', 'questions', 'responses', 'organizer']].rename(columns={
                'id': 'ID',
                'name': 'Название',
                'status': 'Статус',
                'questions': 'Вопросов',
                'responses': 'Ответов',
                'organizer': 'Организатор'
            }),
            use_container_width=True,
            hide_index=True
        )

    def _prepare_surveys_table_data(self, surveys):
        """Подготовка данных для таблицы опросов"""
        table_data = []
        for survey in surveys:
            table_data.append({
                'ID': survey.get('id', 'N/A'),
                'Название': survey.get('name', 'Без названия'),
                'Описание': survey.get('description', '')[:50] + '...' if survey.get('description', '') else '',
                'Статус': survey.get('status', 'Неизвестно'),
                'Тип': survey.get('type', 'Неизвестно'),
                'Вопросов': len(survey.get('questions', [])),
                'Ответов': survey.get('responses', 0),
                'Создан': survey.get('created_date', 'Неизвестно'),
                'Организатор': survey.get('organizer', 'Неизвестно'),
                'Действия': '👁️ ✏️ 📊 🗑️'
            })
        return table_data

    def _render_surveys_table(self, surveys_df, surveys):
        """Рендеринг таблицы опросов"""
        st.dataframe(
            surveys_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Статус": st.column_config.SelectboxColumn(
                    "Статус",
                    options=["Черновик", "Активен", "Опубликован", "Завершен", "Архивный"]
                )
            }
        )

        if not surveys_df.empty:
            self._render_survey_management(surveys_df, surveys)

    def _render_survey_management(self, surveys_df, surveys):
        """Рендеринг управления опросом"""
        st.markdown("### 🔧 Управление опросом")

        selected_survey_id = st.selectbox(
            "Выберите опрос для управления",
            surveys_df['ID'].tolist(),
            format_func=lambda x: f"{x} - {surveys_df[surveys_df['ID'] == x]['Название'].iloc[0]}"
        )

        if not selected_survey_id:
            return

        selected_survey = next((s for s in surveys if s['id'] == selected_survey_id), None)
        if not selected_survey:
            return

        self._render_survey_actions(selected_survey)
        self._render_survey_details(selected_survey)

        if st.session_state.get('selected_survey_for_preview'):
            st.markdown("---")
            self.show_preview(st.session_state.selected_survey_for_preview)

    def _render_survey_actions(self, survey):
        """Рендеринг действий с опросом"""
        col_actions1, col_actions2, col_actions3, col_actions4 = st.columns(4)

        with col_actions1:
            if st.button("👁️ Просмотр", use_container_width=True):
                st.session_state.selected_survey_for_preview = survey
                st.rerun()

        with col_actions2:
            if st.button("✏️ Редактировать", use_container_width=True):
                st.session_state.editing_survey = survey
                st.session_state.selected_menu = "📝 Создать опрос"
                st.rerun()

        with col_actions3:
            if st.button("📊 Статистика", use_container_width=True):
                self.show_statistics(survey)

        with col_actions4:
            if st.button("🗑️ Удалить", use_container_width=True):
                st.session_state.survey_to_delete = survey['id']
                st.session_state.survey_to_delete_name = survey.get('name', 'Опрос')

        self._render_delete_survey_confirmation(survey)

    def _render_delete_survey_confirmation(self, survey):
        """Рендеринг подтверждения удаления опроса"""
        if st.session_state.get('survey_to_delete') != survey['id']:
            return

        with st.expander("⚠️ Подтверждение удаления", expanded=True):
            st.warning(f"Вы уверены, что хотите удалить опрос '{st.session_state.survey_to_delete_name}'?")

            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Да, удалить", type="primary", use_container_width=True):
                    self.storage.delete(survey['id'])
                    st.success(f"Опрос '{st.session_state.survey_to_delete_name}' удален")
                    self._cleanup_survey_delete_state()
                    st.rerun()

            with col_confirm2:
                if st.button("❌ Отмена", type="secondary", use_container_width=True):
                    self._cleanup_survey_delete_state()
                    st.rerun()

    def _cleanup_survey_delete_state(self):
        """Очистка состояния удаления опроса"""
        if 'survey_to_delete' in st.session_state:
            del st.session_state.survey_to_delete
        if 'survey_to_delete_name' in st.session_state:
            del st.session_state.survey_to_delete_name

    def _render_survey_details(self, survey):
        """Рендеринг деталей опроса"""
        with st.expander("📋 Детальная информация об опросе", expanded=True):
            self.show_details(survey)

    def _render_survey_settings(self, survey):
        """Рендеринг настроек опроса"""
        st.markdown("#### ⚙️ Настройки опроса")
        col_set1, col_set2 = st.columns(2)

        with col_set1:
            st.markdown(f"**Анонимный:** {'✅ Да' if survey.get('anonymous', False) else '❌ Нет'}")
            st.markdown(f"**Прогресс:** {'✅ Показывать' if survey.get('show_progress', True) else '❌ Скрывать'}")

        with col_set2:
            st.markdown(f"**Возврат:** {'✅ Разрешен' if survey.get('allow_return', True) else '❌ Запрещен'}")
            st.markdown(f"**Аудитория:** {', '.join(survey.get('audience', ['Все']))}")

    def _render_survey_questions(self, survey):
        """Рендеринг вопросов опроса"""
        questions = survey.get('questions', [])
        if not questions:
            return

        st.markdown("#### ❓ Вопросы опроса")

        for i, question in enumerate(questions, 1):
            with st.expander(f"Вопрос {i}: {question.get('text', 'Без текста')}", expanded=False):
                col_q1, col_q2 = st.columns([3, 1])

                with col_q1:
                    q_type = question.get('type', 'text')
                    if q_type in ['multiple_choice', 'single_choice']:
                        options = question.get('options', [])
                        st.write("**Варианты ответов:**")
                        for j, option in enumerate(options, 1):
                            st.write(f"  {j}. {option}")
                    elif q_type == 'scale':
                        st.write(f"**Шкала:** от {question.get('min', 1)} до {question.get('max', 5)}")
                    else:
                        st.write("**Тип ответа:** Текстовый")

                with col_q2:
                    st.caption(f"**Тип:** {q_type}")

    def _render_responses_chart(self):
        """Рендеринг графика ответов"""
        st.markdown("#### 📈 Распределение ответов по дням")

        dates = pd.date_range(end=datetime.now(), periods=14, freq='D')
        daily_responses = np.random.randint(1, 20, size=len(dates))

        fig = px.bar(
            x=dates.strftime('%d.%m'),
            y=daily_responses,
            labels={'x': 'Дата', 'y': 'Ответы'},
            title='Количество ответов по дням'
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_survey_preview_info(self, survey):
        """Рендеринг информации в предпросмотре опроса"""
        col_info1, col_info2, col_info3 = st.columns(3)

        with col_info1:
            st.caption(f"👤 **Организатор:** {survey.get('organizer', 'Неизвестно')}")

        with col_info2:
            status = survey.get('status', 'Неизвестно')
            status_icon = "🟢" if status in ['Активен', 'Опубликован'] else "🟡" if status == 'Черновик' else "🔴"
            st.caption(f"{status_icon} **Статус:** {status}")

        with col_info3:
            st.caption(f"📅 **Создан:** {survey.get('created_date', 'Неизвестно')}")

    def _render_survey_preview_questions(self, survey):
        """Рендеринг вопросов в предпросмотре опроса"""
        questions = survey.get('questions', [])
        if not questions:
            st.warning("В этом опросе пока нет вопросов.")
            return

        st.markdown(f"#### ❓ Вопросы ({len(questions)})")
        preview_questions = questions[:5]

        for i, question in enumerate(preview_questions, 1):
            with st.expander(f"Вопрос {i}: {question.get('text', 'Без текста')}", expanded=False):
                self._render_question_preview(question, i)

        if len(questions) > 5:
            st.info(f"Еще {len(questions) - 5} вопросов...")

    def _render_question_preview(self, question, index):
        """Рендеринг предпросмотра вопроса"""
        q_type = question.get('type', 'text')

        if q_type in ['multiple_choice', 'single_choice']:
            options = question.get('options', [])
            st.write("**Варианты ответов:**")
            for j, option in enumerate(options, 1):
                st.write(f"  {j}. {option}")

        elif q_type == 'scale':
            min_val = question.get('min', 1)
            max_val = question.get('max', 5)
            st.write(f"**Шкала:** от {min_val} до {max_val}")
            st.slider("Пример ответа", min_val, max_val, (min_val + max_val) // 2,
                      key=f"preview_slider_{index}")

        else:
            st.text_area("Пример текстового ответа", placeholder="Введите ваш ответ здесь...",
                         key=f"preview_text_{index}")

    def _render_survey_preview_actions(self, survey):
        """Рендеринг действий в предпросмотре опроса"""
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("← Назад к списку", use_container_width=True):
                del st.session_state.selected_survey_for_preview
                st.rerun()

        with col_btn2:
            if st.button("✏️ Редактировать", use_container_width=True):
                st.session_state.editing_survey = survey
                st.session_state.selected_menu = "📝 Создать опрос"
                del st.session_state.selected_survey_for_preview
                st.rerun()

        with col_btn3:
            new_status = "Опубликован" if survey.get('status') != "Опубликован" else "Активен"
            button_text = 'Опубликовать' if survey.get('status') != 'Опубликован' else 'Снять с публикации'

            if st.button(f"🚀 {button_text}", use_container_width=True):
                self.storage.toggle_publication(survey['id'], new_status)
                st.rerun()