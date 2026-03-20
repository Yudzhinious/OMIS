import streamlit as st
from datetime import datetime
from controller.participant.participant_state import ParticipantState


class ParticipantSurvey:

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
        """Страница прохождения опроса для участника"""
        self.participant_state.init_session_state()

        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 30px;'>Пройти опрос</h1>",
            unsafe_allow_html=True
        )

        selected_survey = self._get_selected_survey()
        if not selected_survey:
            return

        self._display_survey_info(selected_survey)

    def _get_selected_survey(self):
        """Получение выбранного опроса"""
        real_surveys = st.session_state.get('real_surveys', [])
        published_surveys = [s for s in real_surveys
                             if s.get('status') in ['Опубликован', 'Активный', 'Опубликованный']]

        if not published_surveys:
            st.info("📭 В данный момент нет доступных опросов.")
            return None

        if 'selected_survey_for_take' in st.session_state:
            return st.session_state.selected_survey_for_take

        return self._select_survey_from_list(published_surveys)

    def _select_survey_from_list(self, published_surveys):
        """Выбор опроса из списка"""
        survey_options = {}
        for survey in published_surveys:
            survey_id = survey.get('id', '')
            survey_data = self.organizer_storage.generate_real_survey_data(
                survey_id) if survey_id and self.organizer_storage else {'total_responses': 0}

            survey_options[
                f"{survey.get('name', 'Без названия')} "
                f"({len(survey.get('questions', []))} вопросов, "
                f"{survey_data['total_responses']} ответов)"
            ] = survey

        selected_survey_name = st.selectbox(
            "Выберите опрос для прохождения",
            options=list(survey_options.keys()),
            index=0 if survey_options else None
        )

        return survey_options.get(selected_survey_name) if selected_survey_name else None

    def _display_survey_info(self, selected_survey):
        """Отображение информации об опросе"""
        survey_id = selected_survey.get('id', '')
        survey_data = self.organizer_storage.generate_real_survey_data(
            survey_id) if survey_id and self.organizer_storage else {'total_responses': 0}

        completed_ids = [s.get('id') for s in st.session_state.completed_surveys]
        is_completed = survey_id in completed_ids

        if is_completed:
            completed_info = next(s for s in st.session_state.completed_surveys
                                  if s.get('id') == survey_id)
            st.info(f"📋 Вы уже проходили этот опрос {completed_info['date']}. "
                    f"Оценка: {completed_info['score']}")

        self._render_survey_header(selected_survey, survey_data)
        self._render_survey_buttons(selected_survey, survey_id)

        if ('current_survey' in st.session_state and
                st.session_state.current_survey.get('id') == selected_survey.get('id')):
            self.display_real_survey(st.session_state.current_survey)

    def display_real_survey(self, survey):
        """Отображение реального опроса с вопросами"""
        if 'show_survey_result' in st.session_state and st.session_state.show_survey_result:
            self._show_survey_result()
            return

        self._display_survey_progress(survey)
        self._display_current_question(survey)

    def _render_survey_header(self, selected_survey, survey_data):
        """Рендеринг заголовка опроса"""
        html = f"""
        <div style="background: white; border-radius: 10px; padding: 25px; 
                    margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-top: 0;">
                {selected_survey.get('name', 'Без названия')}
            </h3>
            <div style="margin: 15px 0;">
                <p style="color: #7f8c8d;">
                    {selected_survey.get('description', 'Описание отсутствует')}
                </p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); 
                        gap: 15px; margin: 20px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #667eea;">
                        {len(selected_survey.get('questions', []))}
                    </div>
                    <div style="font-size: 12px; color: #7f8c8d;">вопросов</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #27ae60;">
                        {survey_data['total_responses']}
                    </div>
                    <div style="font-size: 12px; color: #7f8c8d;">уже ответили</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #ff7e5f;">+10</div>
                    <div style="font-size: 12px; color: #7f8c8d;">баллов</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _render_survey_buttons(self, selected_survey, survey_id):
        """Рендеринг кнопок опроса"""
        col_start1, col_start2 = st.columns([1, 1])

        with col_start1:
            if st.button("🚀 Начать опрос", use_container_width=True, type="primary"):
                st.session_state.current_survey = selected_survey
                st.session_state.survey_step = 0
                st.session_state.survey_answers = {}
                st.session_state.survey_start_time = datetime.now()
                st.session_state.show_survey_result = False

                if 'selected_survey_for_take' in st.session_state:
                    del st.session_state.selected_survey_for_take
                st.rerun()

        with col_start2:
            if st.button("← Назад к списку", use_container_width=True, type="secondary"):
                if 'selected_survey_for_take' in st.session_state:
                    del st.session_state.selected_survey_for_take
                st.rerun()

    def _show_survey_result(self):
        """Показ результатов опроса"""
        completed_survey = st.session_state.get('completed_survey', {})

        st.success("🎉 Опрос завершен!")

        html = f"""
        <div style="background: white; border-radius: 10px; padding: 25px; 
                    margin: 20px 0; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #27ae60;">🏆 Отличная работа!</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); 
                        gap: 20px; margin: 30px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #ff7e5f;">+10</div>
                    <div style="font-size: 14px; color: #7f8c8d;">баллов заработано</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #667eea;">
                        {completed_survey.get('raw_score', 0)}/100
                    </div>
                    <div style="font-size: 14px; color: #7f8c8d;">ваша оценка</div>
                </div>
            </div>
            <p style="color: #7f8c8d;">Опрос сохранен в вашей истории</p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        self._show_result_buttons()

    def _show_result_buttons(self):
        """Показ кнопок после завершения опроса"""
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("📋 Перейти к истории", use_container_width=True):
                self._cleanup_survey_state()
                st.session_state.selected_menu = "📜 История"
                st.rerun()

        with col_btn2:
            if st.button("Вернуться к списку опросов", use_container_width=True, type="secondary"):
                self._cleanup_survey_state()
                st.rerun()

    def _cleanup_survey_state(self):
        """Очистка состояния опроса"""
        keys_to_remove = ['current_survey', 'survey_step', 'survey_answers',
                          'survey_start_time', 'show_survey_result', 'completed_survey']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]

    def _display_survey_progress(self, survey):
        """Отображение прогресса опроса"""
        questions = survey.get('questions', [])
        total_questions = len(questions)

        if total_questions == 0:
            st.error("В этом опросе нет вопросов")
            if st.button("← Вернуться"):
                if 'current_survey' in st.session_state:
                    del st.session_state.current_survey
                st.rerun()
            return

        progress = ((st.session_state.survey_step + 1) / total_questions) * 100 if total_questions > 0 else 0

        html = f"""
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-size: 14px; color: #7f8c8d;">Прогресс</span>
                <span style="font-size: 14px; color: #667eea; font-weight: bold;">
                    {st.session_state.survey_step + 1} из {total_questions}
                </span>
            </div>
            <div style="height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden;">
                <div style="width: {progress}%; height: 100%; 
                            background: linear-gradient(90deg, #667eea, #764ba2); 
                            transition: width 0.3s;"></div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _display_current_question(self, survey):
        """Отображение текущего вопроса"""
        questions = survey.get('questions', [])
        total_questions = len(questions)

        if st.session_state.survey_step < total_questions:
            current_question = questions[st.session_state.survey_step]
            self._render_question(current_question, survey, total_questions)

    def _render_question(self, current_question, survey, total_questions):
        """Рендеринг вопроса"""
        html = f"""
        <div style="background: white; border-radius: 10px; padding: 30px; 
                    margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-top: 0;">
                Вопрос {st.session_state.survey_step + 1}
            </h3>
            <p style="font-size: 18px; margin: 20px 0; font-weight: 500;">
                {current_question.get('text', 'Вопрос без текста')}
            </p>
            <p style="font-size: 14px; color: #7f8c8d;">
                Тип вопроса: {current_question.get('type', 'Не указан')}
            </p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        selected_answer = self._display_answer_options(current_question, survey)
        self._render_navigation_buttons(current_question, survey, total_questions, selected_answer)

    def _display_answer_options(self, current_question, survey):
        """Отображение вариантов ответов"""
        q_type = current_question.get('type', 'text')
        selected_answer = None

        if q_type == 'single_choice':
            options = current_question.get('options', [])
            if options:
                selected_answer = st.radio(
                    "Выберите один вариант:",
                    options,
                    key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}"
                )
            else:
                st.warning("Вопрос без вариантов ответа")
                selected_answer = st.text_input(
                    "Ваш ответ:",
                    key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}"
                )

        elif q_type == 'multiple_choice':
            options = current_question.get('options', [])
            if options:
                selected_options = st.multiselect(
                    "Выберите один или несколько вариантов:",
                    options,
                    key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}"
                )
                selected_answer = selected_options
            else:
                st.warning("Вопрос без вариантов ответа")
                selected_answer = st.text_input(
                    "Ваш ответ:",
                    key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}"
                )

        elif q_type == 'scale':
            min_val = current_question.get('min', 1)
            max_val = current_question.get('max', 5)
            selected_answer = st.slider(
                "Оцените по шкале:",
                min_val, max_val, (min_val + max_val) // 2,
                key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}"
            )

        else:
            selected_answer = st.text_area(
                "Ваш ответ:",
                key=f"q_{st.session_state.survey_step}_{survey.get('id', '')}",
                height=100
            )

        return selected_answer

    def _render_navigation_buttons(self, current_question, survey, total_questions, selected_answer):
        """Рендеринг кнопок навигации"""
        col_prev, col_space, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.session_state.survey_step > 0:
                if st.button("⬅️ Предыдущий", use_container_width=True, type="secondary"):
                    st.session_state.survey_step -= 1
                    st.rerun()

        with col_next:
            if st.session_state.survey_step < total_questions - 1:
                if st.button("Далее ➡️", use_container_width=True, disabled=selected_answer is None):
                    self._save_answer_and_continue(current_question, selected_answer)
            else:
                if st.button("✅ Завершить опрос", use_container_width=True,
                             type="primary", disabled=selected_answer is None):
                    self._complete_survey(current_question, selected_answer, survey)

        if st.button("❌ Отменить опрос", use_container_width=True, type="secondary"):
            if 'current_survey' in st.session_state:
                del st.session_state.current_survey
            st.rerun()

    def _save_answer_and_continue(self, current_question, selected_answer):
        """Сохранение ответа и переход к следующему вопросу"""
        st.session_state.survey_answers[st.session_state.survey_step] = {
            'question': current_question.get('text', ''),
            'question_type': current_question.get('type', 'text'),
            'answer': selected_answer,
            'question_data': current_question
        }
        st.session_state.survey_step += 1
        st.rerun()

    def _complete_survey(self, current_question, selected_answer, survey):
        """Завершение опроса и сохранение результатов"""
        st.session_state.survey_answers[st.session_state.survey_step] = {
            'question': current_question.get('text', ''),
            'question_type': current_question.get('type', 'text'),
            'answer': selected_answer,
            'question_data': current_question
        }

        time_spent = max(1, (datetime.now() - st.session_state.survey_start_time).seconds // 60)
        final_score = self._calculate_final_score(survey)

        self._save_survey_response(survey, time_spent, final_score)
        self._finish_survey(survey, time_spent, final_score)

    def _calculate_final_score(self, survey):
        """Расчет итоговой оценки"""
        total_score = 0
        total_questions = len(survey.get('questions', []))
        max_score = total_questions * 10

        for i, answer_data in st.session_state.survey_answers.items():
            if answer_data['question_type'] == 'scale':
                max_val = answer_data['question_data'].get('max', 5)
                score = (answer_data['answer'] / max_val) * 10
            elif answer_data['question_type'] in ['single_choice', 'multiple_choice']:
                score = 7
            else:
                score = 5 if answer_data['answer'] and len(answer_data['answer']) > 10 else 3
            total_score += score

        return int((total_score / max_score) * 100) if max_score > 0 else 50

    def _save_survey_response(self, survey, time_spent, final_score):
        """Сохранение ответа на опрос"""
        formatted_answers = {}
        for i, answer_data in st.session_state.survey_answers.items():
            q_key = f"q_{i + 1}"
            if isinstance(answer_data['answer'], list):
                formatted_answers[q_key] = ", ".join(answer_data['answer'])
            else:
                formatted_answers[q_key] = str(answer_data['answer'])

        user_data = st.session_state.current_user

        try:
            if self.organizer_storage:
                self.organizer_storage.add_survey_response(
                    survey.get('id', ''),
                    user_data,
                    formatted_answers,
                    time_spent * 60
                )
        except Exception as e:
            st.warning(f"Ответ сохранен локально. Ошибка при сохранении в систему: {str(e)}")

    def _finish_survey(self, survey, time_spent, final_score):
        """Завершение опроса"""
        completed = self.participant_state.save_completed_survey(
            survey,
            st.session_state.survey_answers,
            time_spent,
            final_score
        )

        st.session_state.completed_survey = completed
        st.session_state.show_survey_result = True
        st.rerun()