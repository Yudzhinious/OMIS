import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import io
import random
from datetime import datetime, timedelta
from controller.organizer.organizer_storage import OrganizerStorage


class ReportManager:

    def __init__(self, storage: OrganizerStorage):
        self.storage = storage

    def show_organizer_reports(self):
        """Управление отчетами организатора"""
        self.storage.init_data_storage()

        st.markdown("## Управление отчетами")
        self._render_quick_reports()
        self._render_custom_report_form()
        self._render_reports_history()

    def _render_quick_reports(self):
        """Рендеринг быстрых отчетов"""
        st.markdown("### Быстрые отчеты")
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)

        with col_r1:
            if st.button("📊 Ежедневный отчет", use_container_width=True):
                self.generate_daily_report()

    def _render_custom_report_form(self):
        """Рендеринг формы кастомного отчета"""
        st.markdown("### Создать кастомный отчет")

        with st.form("custom_report_form", clear_on_submit=True):
            report_name = st.text_input("Название отчета*", placeholder="Введите название отчета")

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                report_type = st.selectbox("Тип отчета*",
                                           ["Статистический", "Аналитический", "Сравнительный", "Детальный"])

            with col_c2:
                format_type = st.selectbox("Формат вывода*", ["TXT", "Excel", "CSV", "JSON"])

            surveys = self._get_survey_names_for_multiselect()
            selected_surveys = st.multiselect("Выберите опросы*", surveys, default=[])

            metrics = st.multiselect("Выберите метрики*",
                                     ["Количество ответов", "Процент завершения", "Средний балл", "Время заполнения",
                                      "Демографические данные", "Распределение ответов", "Тренды во времени"],
                                     default=["Количество ответов", "Процент завершения", "Средний балл"])

            date_range = st.date_input("Период*",
                                       [datetime.now() - timedelta(days=30), datetime.now()])

            include_charts = st.checkbox("Включить графики", value=True)

            col_submit1, col_submit2 = st.columns(2)
            with col_submit1:
                submit_button = st.form_submit_button("📊 Создать отчет", use_container_width=True)

            with col_submit2:
                preview_button = st.form_submit_button("👁️ Предпросмотр", use_container_width=True)

            if submit_button or preview_button:
                self._handle_custom_report_submission(
                    report_name, report_type, format_type, selected_surveys,
                    metrics, date_range, include_charts, submit_button
                )

    def _get_survey_names_for_multiselect(self):
        """Получение названий опросов для multiselect"""
        return [
            survey.get('name', f'Опрос {i + 1}')
            for i, survey in enumerate(st.session_state.get('real_surveys', []))
        ]

    def _handle_custom_report_submission(self, name, type_, format_, surveys, metrics,
                                         date_range, include_charts, is_submit):
        """Обработка отправки кастомного отчета"""
        if not name or not surveys or not metrics:
            st.error("⚠️ Заполните обязательные поля (отмечены *)")
            return

        report_data = {
            'name': name,
            'type': type_,
            'format': format_,
            'surveys': surveys,
            'metrics': metrics,
            'date_range': [d.strftime('%Y-%m-%d') for d in date_range],
            'include_charts': include_charts,
            'created_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'status': 'Готов'
        }

        if not is_submit:
            return

        report_id = st.session_state.next_report_id
        report_data['id'] = report_id
        report_data['size'] = f"{np.random.randint(1, 5)}.{np.random.randint(0, 9)} КБ"
        report_data = self._generate_custom_report_content(report_data)

        st.session_state.reports.append(report_data)
        st.session_state.next_report_id += 1

        st.success(f"✅ Отчет '{name}' успешно создан!")
        self._show_report_download_options(report_data)

    def _generate_custom_report_content(self, report_data):
        """Генерация контента кастомного отчета"""
        selected_survey_names = report_data['surveys']
        survey_data_list = []

        for survey in st.session_state.get('real_surveys', []):
            if survey.get('name') not in selected_survey_names:
                continue

            survey_stats = self.storage.generate_real_survey_data(survey.get('id', ''))
            survey_data_list.append({
                'name': survey.get('name'),
                'responses': survey_stats['total_responses'],
                'completion_rate': survey_stats['completion_rate'],
                'average_time': survey_stats['average_time'] / 60,
                'demographics': survey_stats['demographics']
            })

        report_content = {}
        self._add_metrics_to_report_content(report_content, survey_data_list, report_data['metrics'])

        report_data['content'] = report_content
        report_data['generated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        return report_data

    def _add_metrics_to_report_content(self, report_content, survey_data_list, metrics):
        """Добавление метрик в контент отчета"""
        if "Количество ответов" in metrics:
            report_content['total_responses'] = sum(s['responses'] for s in survey_data_list)
            report_content['responses_per_survey'] = {s['name']: s['responses'] for s in survey_data_list}

        if "Процент завершения" in metrics:
            report_content['completion_rates'] = {s['name']: s['completion_rate'] for s in survey_data_list}

        if "Средний балл" in metrics:
            report_content['average_scores'] = {
                s['name']: min(5.0, s['completion_rate'] / 20)
                for s in survey_data_list
            }

        if "Время заполнения" in metrics:
            report_content['completion_times'] = {
                s['name']: f"{s['average_time']:.1f} мин"
                for s in survey_data_list
            }

        if "Демографические данные" in metrics and survey_data_list:
            self._add_demographics_to_report_content(report_content, survey_data_list)

    def _add_demographics_to_report_content(self, report_content, survey_data_list):
        """Добавление демографических данных в контент отчета"""
        all_ages = {}
        all_genders = {}
        all_cities = {}

        for survey in survey_data_list:
            for age, count in survey['demographics']['age'].items():
                all_ages[age] = all_ages.get(age, 0) + count
            for gender, count in survey['demographics']['gender'].items():
                all_genders[gender] = all_genders.get(gender, 0) + count
            for city, count in survey['demographics']['city'].items():
                all_cities[city] = all_cities.get(city, 0) + count

        report_content['demographics'] = {
            'age_groups': all_ages,
            'genders': all_genders,
            'locations': all_cities
        }

    def _show_report_download_options(self, report_data):
        """Показ опций скачивания отчета"""
        st.markdown("##### 📥 Скачать отчет в формате:")

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            if st.button("TXT", use_container_width=True):
                self._download_report(report_data, "TXT")

        with col_dl2:
            if st.button("Excel", use_container_width=True):
                self._download_report(report_data, "Excel")

        with col_dl3:
            if st.button("CSV", use_container_width=True):
                self._download_report(report_data, "CSV")

    def _download_report(self, report_data, format_type=None):
        """Функция скачивания отчета"""
        format_type = format_type or report_data.get('format', 'TXT')

        if format_type == "TXT":
            self._download_txt_report(report_data)
        elif format_type == "Excel":
            self._download_excel_report(report_data)
        elif format_type == "CSV":
            self._download_csv_report(report_data)

    def _download_txt_report(self, report_data):
        """Скачивание отчета в TXT формате"""
        txt_content = f"Отчет: {report_data['name']}\n"
        txt_content += f"Тип: {report_data['type']}\n"
        txt_content += f"Дата создания: {report_data['created_date']}\n"
        txt_content += f"Период: {report_data['date_range'][0]} - {report_data['date_range'][1]}\n"
        txt_content += "-" * 50 + "\n\n"

        if 'content' in report_data:
            content = report_data['content']

            if 'total_responses' in content:
                txt_content += f"Всего ответов: {content['total_responses']}\n\n"

            if 'completion_rates' in content:
                txt_content += "Процент завершения по опросам:\n"
                for survey, rate in content['completion_rates'].items():
                    txt_content += f"  • {survey}: {rate:.1f}%\n"
                txt_content += "\n"

        st.download_button(
            label=f"⬇️ Скачать TXT файл",
            data=txt_content,
            file_name=f"{report_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    def _download_excel_report(self, report_data):
        """Скачивание отчета в Excel формате"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            info_df = pd.DataFrame([
                ["Название отчета", report_data['name']],
                ["Тип отчета", report_data['type']],
                ["Дата создания", report_data['created_date']],
                ["Период", f"{report_data['date_range'][0]} - {report_data['date_range'][1]}"],
                ["Опросы", ", ".join(report_data['surveys'])],
                ["Метрики", ", ".join(report_data['metrics'])]
            ], columns=["Параметр", "Значение"])
            info_df.to_excel(writer, sheet_name='Информация', index=False)

            if 'content' in report_data and 'average_scores' in report_data['content']:
                scores_df = pd.DataFrame(
                    list(report_data['content']['average_scores'].items()),
                    columns=['Опрос', 'Средний балл']
                )
                scores_df.to_excel(writer, sheet_name='Баллы', index=False)

        output.seek(0)

        st.download_button(
            label=f"⬇️ Скачать Excel файл",
            data=output,
            file_name=f"{report_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def _download_csv_report(self, report_data):
        """Скачивание отчета в CSV формате"""
        if 'content' not in report_data or 'average_scores' not in report_data['content']:
            return

        content = report_data['content']
        scores_df = pd.DataFrame(
            list(content['average_scores'].items()),
            columns=['Опрос', 'Средний балл']
        )

        csv_data = scores_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="⬇️ Скачать CSV файл",
            data=csv_data,
            file_name=f"{report_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    def _render_reports_history(self):
        """Рендеринг истории отчетов"""
        st.markdown("---")
        st.markdown("### 📚 История отчетов")

        if not st.session_state.reports:
            st.info("📭 Отчеты еще не созданы. Создайте свой первый отчет выше.")
            return

        reports_df = pd.DataFrame(st.session_state.reports)
        self._render_reports_filters(reports_df)

    def _render_reports_filters(self, reports_df):
        """Рендеринг фильтров отчетов"""
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            report_search = st.text_input("Поиск по названию", placeholder="Введите название отчета...")

        with col_filter2:
            type_filter = st.selectbox("Фильтр по типу",
                                       ["Все типы", "Статистический", "Аналитический", "Сравнительный", "Детальный"])

        filtered_reports = self._filter_reports_df(reports_df, report_search, type_filter)
        self._render_filtered_reports(filtered_reports)

    def _filter_reports_df(self, df, search_query, type_filter):
        """Фильтрация DataFrame отчетов"""
        filtered_df = df

        if search_query:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_query, case=False, na=False)
            ]

        if type_filter != "Все типы":
            filtered_df = filtered_df[filtered_df['type'] == type_filter]

        return filtered_df

    def _render_filtered_reports(self, filtered_df):
        """Рендеринг отфильтрованных отчетов"""
        if filtered_df.empty:
            st.info("📭 Отчеты не найдены по выбранным фильтрам")
            return

        display_cols = ['name', 'type', 'created_date', 'status', 'size', 'actions']
        filtered_df['actions'] = '📥 👁️ 📊 🗑️'

        st.dataframe(
            filtered_df[display_cols].rename(columns={
                'name': 'Название',
                'type': 'Тип',
                'created_date': 'Дата создания',
                'status': 'Статус',
                'size': 'Размер',
                'actions': 'Действия'
            }),
            use_container_width=True,
            hide_index=True
        )

        self._render_report_actions(filtered_df)

    def _render_report_actions(self, filtered_df):
        """Рендеринг действий с отчетами"""
        if filtered_df.empty:
            return

        selected_report_idx = st.selectbox(
            "Выберите отчет для управления:",
            range(len(filtered_df)),
            format_func=lambda x: filtered_df.iloc[x]['name']
        )

        if selected_report_idx is None:
            return

        selected_report = filtered_df.iloc[selected_report_idx].to_dict()
        self._render_report_action_buttons(selected_report)

    def _render_report_action_buttons(self, report):
        """Рендеринг кнопок действий с отчетом"""
        col_act1, col_act2, col_act3, col_act4 = st.columns(4)

        with col_act1:
            if st.button("📥 Скачать", key="download_btn", use_container_width=True):
                self._download_report(report)

        with col_act3:
            if st.button("📊 Анализ", key="analyze_btn", use_container_width=True):
                self._show_report_analysis(report)

        with col_act4:
            if st.button("🗑️ Удалить", key="delete_btn", use_container_width=True):
                self._delete_report(report['id'])

    def _show_report_analysis(self, report_data):
        """Показ детального анализа отчета"""
        st.markdown(f"### 📊 Детальный анализ: {report_data['name']}")

        if 'content' not in report_data:
            st.info("Нет данных для анализа")
            return

        content = report_data['content']
        self._render_report_visualizations(content)
        self._render_report_insights(content)

    def _render_report_visualizations(self, content):
        """Рендеринг визуализаций отчета"""
        col_vis1, col_vis2 = st.columns(2)

        with col_vis1:
            if 'average_scores' in content:
                scores_df = pd.DataFrame(
                    list(content['average_scores'].items()),
                    columns=['Опрос', 'Балл']
                )
                fig = px.bar(scores_df, x='Опрос', y='Балл',
                             title='Средние баллы по опросам',
                             color='Балл')
                st.plotly_chart(fig, use_container_width=True)

        with col_vis2:
            if 'demographics' in content and 'age_groups' in content['demographics']:
                age_df = pd.DataFrame(
                    list(content['demographics']['age_groups'].items()),
                    columns=['Возраст', 'Количество']
                )
                fig = px.pie(age_df, values='Количество', names='Возраст',
                             title='Возрастное распределение')
                st.plotly_chart(fig, use_container_width=True)

    def _render_report_insights(self, content):
        """Рендеринг инсайтов отчета"""
        st.markdown("#### 📝 Статистические выводы")

        insights = []
        if 'total_responses' in content:
            insights.append(f"📊 Всего собрано {content.get('total_responses', 0):,} ответов")

        if 'completion_rates' in content:
            avg_completion = np.mean(list(content['completion_rates'].values()))
            insights.append(f"📈 Средний процент завершения опросов: {avg_completion:.1f}%")

        if 'average_scores' in content:
            best_survey = max(content['average_scores'].items(), key=lambda x: x[1])[0]
            insights.append(f"⭐ Наивысший балл получен в опросе '{best_survey}'")

        if 'demographics' in content and 'age_groups' in content['demographics']:
            total_age = sum(age * count for age, count in content['demographics']['age_groups'].items())
            total_count = sum(content['demographics']['age_groups'].values())
            avg_age = total_age / total_count if total_count > 0 else 0
            insights.append(f"👥 Основная аудитория: {avg_age:.1f} лет")

        for insight in insights:
            st.markdown(f"- {insight}")

    def _delete_report(self, report_id):
        """Удаление отчета"""
        for i, report in enumerate(st.session_state.reports):
            if report['id'] != report_id:
                continue

            report_name = report['name']
            st.session_state.reports.pop(i)
            st.success(f"✅ Отчет '{report_name}' удален")
            st.rerun()
            return

        st.error("Отчет не найден")

    def generate_daily_report(self):
        """Генерация ежедневного отчета"""
        report_data = {
            'id': st.session_state.next_report_id,
            'name': f'Ежедневный отчет {datetime.now().strftime("%d.%m.%Y")}',
            'type': 'Автоматический',
            'format': 'TXT',
            'surveys': ['Все активные опросы'],
            'metrics': ['Количество ответов', 'Процент завершения', 'Средний балл', 'Время заполнения'],
            'date_range': [datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')],
            'include_charts': True,
            'created_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'status': 'Готов',
            'size': f"{np.random.randint(1, 3)}.{np.random.randint(0, 9)} КБ"
        }

        report_data = self._generate_custom_report_content(report_data)
        st.session_state.reports.append(report_data)
        st.session_state.next_report_id += 1

        st.success(f"✅ Ежедневный отчет создан")
        return report_data


class SurveyParticipant:
    """Класс для прохождения опросов участниками"""

    def __init__(self, storage: OrganizerStorage):
        self.storage = storage

    def take_survey_participant(self, survey_id):
        """Функция для прохождения опроса участником"""
        self.storage.init_data_storage()

        survey = self._get_survey_by_id(survey_id)
        if not survey:
            st.error("Опрос не найден")
            return False

        self._render_survey_header(survey)
        self._render_survey_progress(survey)

        answers = {}
        user_data = self._get_user_data()
        questions = survey.get('questions', [])

        for i, question in enumerate(questions, 1):
            self._render_question(question, i, answers, survey_id)

            if survey.get('show_progress', True) and i < len(questions):
                progress = i / len(questions)
                st.progress(progress, text=f"Вопрос {i + 1} из {len(questions)}")

        return self._render_submit_button(survey_id, user_data, answers)

    def _render_survey_header(self, survey):
        """Рендеринг заголовка опроса"""
        st.markdown(f"## 📝 Опрос: {survey.get('name', 'Без названия')}")

        if survey.get('description'):
            st.info(survey.get('description'))

    def _render_survey_progress(self, survey):
        """Рендеринг прогресса опроса"""
        questions = survey.get('questions', [])
        total_questions = len(questions)

        if not survey.get('show_progress', True) or total_questions <= 0:
            return

        st.progress(0, text=f"Вопрос 1 из {total_questions}")

    def _get_user_data(self):
        """Получение данных пользователя"""
        current_user = st.session_state.get('current_user', {})
        return {
            'user_id': getattr(current_user, 'id', f'user_{random.randint(1000, 9999)}'),
            'age': random.randint(18, 65),
            'gender': random.choice(['Мужчина', 'Женщина']),
            'city': random.choice(['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань'])
        }

    def _render_question(self, question, index, answers, survey_id):
        """Рендеринг вопроса"""
        st.markdown(f"### ❓ Вопрос {index}")
        st.markdown(f"**{question.get('text', '')}**")

        q_type = question.get('type', 'text')
        answer_key = f"q_{index}"

        if q_type == 'single_choice':
            self._render_single_choice_question(question, answer_key, answers, survey_id, index)
        elif q_type == 'multiple_choice':
            self._render_multiple_choice_question(question, answer_key, answers, survey_id, index)
        elif q_type == 'scale':
            self._render_scale_question(question, answer_key, answers, survey_id, index)
        else:
            self._render_text_question(answer_key, answers, survey_id, index)

    def _render_single_choice_question(self, question, answer_key, answers, survey_id, index):
        """Рендеринг вопроса с одним вариантом ответа"""
        options = question.get('options', [])
        answers[answer_key] = st.radio(
            "Выберите один вариант:",
            options,
            key=f"single_{survey_id}_{index}"
        )

    def _render_multiple_choice_question(self, question, answer_key, answers, survey_id, index):
        """Рендеринг вопроса с несколькими вариантами ответа"""
        options = question.get('options', [])
        selected = st.multiselect(
            "Выберите один или несколько вариантов:",
            options,
            key=f"multi_{survey_id}_{index}"
        )
        answers[answer_key] = selected

    def _render_scale_question(self, question, answer_key, answers, survey_id, index):
        """Рендеринг вопроса со шкалой"""
        min_val = question.get('min', 1)
        max_val = question.get('max', 5)
        answers[answer_key] = st.slider(
            "Оцените по шкале:",
            min_val, max_val, (min_val + max_val) // 2,
            key=f"scale_{survey_id}_{index}"
        )

    def _render_text_question(self, answer_key, answers, survey_id, index):
        """Рендеринг текстового вопроса"""
        answers[answer_key] = st.text_area(
            "Ваш ответ:",
            key=f"text_{survey_id}_{index}"
        )

    def _render_submit_button(self, survey_id, user_data, answers):
        """Рендеринг кнопки отправки"""
        if not st.button("📤 Отправить ответы", type="primary", use_container_width=True):
            return False

        completion_time = random.randint(60, 600)
        response = self.storage.add_survey_response(survey_id, user_data, answers, completion_time)

        st.success("✅ Ваши ответы успешно отправлены! Спасибо за участие!")
        st.balloons()

        survey_data = self.storage.generate_real_survey_data(survey_id)
        self._show_survey_stats(survey_data, completion_time)

        return True

    def _show_survey_stats(self, survey_data, completion_time):
        """Показ статистики опроса"""
        minutes = completion_time // 60
        seconds = completion_time % 60
        time_str = f"{minutes} мин. {seconds} сек." if minutes > 0 else f"{seconds} сек."

        st.info(f"**Статистика опроса:**\n"
                f"• Всего ответов: {survey_data['total_responses']}\n"
                f"• Ваше время: {time_str}")

    def show_participant_survey(self):
        """Страница прохождения опросов для участника"""
        self.storage.init_data_storage()

        st.markdown("## 📝 Доступные опросы")

        published_surveys = self._get_published_surveys()
        if not published_surveys:
            st.info("📭 В данный момент нет доступных опросов. Загляните позже!")
            return

        self._render_survey_selection(published_surveys)
        self._render_selected_survey()

    def _get_published_surveys(self):
        """Получение опубликованных опросов"""
        return [
            s for s in st.session_state.get('real_surveys', [])
            if s.get('status') in ['Опубликован', 'Активный']
        ]

    def _render_survey_selection(self, published_surveys):
        """Рендеринг выбора опроса"""
        survey_options = {
            f"{s.get('name', 'Без названия')} ({s.get('id', 'N/A')})": s
            for s in published_surveys
        }

        selected_survey_name = st.selectbox(
            "Выберите опрос для прохождения:",
            list(survey_options.keys())
        )

        if not selected_survey_name:
            return

        selected_survey = survey_options[selected_survey_name]
        self._render_survey_info(selected_survey)

    def _render_survey_info(self, survey):
        """Рендеринг информации об опросе"""
        st.markdown(f"### {survey.get('name', 'Без названия')}")

        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.caption(f"📅 Создан: {survey.get('created_date', 'Неизвестно')}")
            st.caption(f"📊 Вопросов: {len(survey.get('questions', []))}")

        with col_info2:
            estimated_time = len(survey.get('questions', [])) * 2
            st.caption(f"⏱️ Примерное время: {estimated_time} мин.")

            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            st.caption(f"👥 Уже ответили: {survey_data['total_responses']} чел.")

        if survey.get('description'):
            st.info(f"**Описание:** {survey.get('description')}")

        if st.button("🚀 Начать опрос", type="primary", use_container_width=True):
            st.session_state.current_survey_id = survey.get('id')
            st.rerun()

    def _render_selected_survey(self):
        """Рендеринг выбранного опроса"""
        if not st.session_state.get('current_survey_id'):
            return

        survey_id = st.session_state.current_survey_id
        completed = self.take_survey_participant(survey_id)

        if completed:
            del st.session_state.current_survey_id
            st.rerun()

        if st.button("← Вернуться к списку опросов", type="secondary"):
            del st.session_state.current_survey_id
            st.rerun()

    def _get_survey_by_id(self, survey_id):
        """Получение опроса по ID"""
        for survey in st.session_state.get('real_surveys', []):
            if survey.get('id') == survey_id:
                return survey
        return None