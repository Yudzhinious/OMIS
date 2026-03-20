import streamlit as st
from datetime import datetime, timedelta
from controller.admin.storage import SurveyStorage

class SurveyCreator:
    def __init__(self):
        self.storage = SurveyStorage()

    def show_page(self, services, views):
        """Страница создания опроса"""
        st.markdown("## 📝 Создание нового опроса")

        user_name = self._get_user_name()
        self._render_survey_form(user_name)
        self._render_survey_questions_section()
        self._render_survey_actions(user_name)

    def _get_user_name(self):
        """Получение имени пользователя"""
        if not st.session_state.current_user:
            return "Неизвестный пользователь"

        if hasattr(st.session_state.current_user, 'login'):
            return st.session_state.current_user.login
        elif hasattr(st.session_state.current_user, 'name'):
            return st.session_state.current_user.name

        return "Неизвестный пользователь"

    def _render_survey_form(self, user_name):
        """Рендеринг формы опроса"""
        with st.form("create_survey_form"):
            st.markdown("### Основная информация")

            survey_name = st.text_input(
                "Название опроса *",
                placeholder="Введите название опроса",
                help="Название должно быть понятным и отражать суть опроса"
            )

            survey_description = st.text_area(
                "Описание опроса",
                placeholder="Опишите цель и задачи опроса",
                help="Это описание увидят участники опроса"
            )

            col_type, col_audience = st.columns(2)
            with col_type:
                survey_type = st.selectbox(
                    "Тип опроса *",
                    ["Публичный", "Приватный", "По приглашению"],
                    help="Публичный - доступен всем, Приватный - по ссылке, По приглашению - только для выбранных пользователей"
                )

            with col_audience:
                target_audience = st.multiselect(
                    "Целевая аудитория",
                    ["Все", "Студенты", "Сотрудники", "Клиенты", "Партнеры", "Другое"],
                    default=["Все"],
                    help="Кто является целевой аудиторией опроса"
                )

            st.markdown("### Настройки опроса")

            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Дата начала *", datetime.now())

            with col_date2:
                end_date = st.date_input("Дата окончания *", datetime.now() + timedelta(days=30))

            col_settings1, col_settings2, col_settings3 = st.columns(3)
            with col_settings1:
                anonymous = st.checkbox("Анонимный опрос", value=False,
                                        help="Ответы будут анонимными, имена участников не сохранятся")

            with col_settings2:
                show_progress = st.checkbox("Показывать прогресс", value=True,
                                            help="Участники будут видеть прогресс прохождения опроса")

            with col_settings3:
                allow_return = st.checkbox("Разрешить возврат", value=True,
                                           help="Участники смогут возвращаться к предыдущим вопросам")

            submitted = st.form_submit_button("📋 Сохранить основную информацию", use_container_width=True)

            if submitted:
                self._handle_survey_form_submission(survey_name, survey_description, survey_type,
                                                    target_audience, start_date, end_date, anonymous,
                                                    show_progress, allow_return, user_name)

    def _handle_survey_form_submission(self, name, description, type_, audience, start_date, end_date,
                                       anonymous, show_progress, allow_return, organizer):
        """Обработка отправки формы опроса"""
        if not name:
            st.error("Название опроса обязательно!")
            return

        if end_date <= start_date:
            st.error("Дата окончания должна быть позже даты начала!")
            return

        st.session_state.survey_basic_info = {
            'name': name,
            'description': description,
            'type': type_,
            'audience': audience,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'anonymous': anonymous,
            'show_progress': show_progress,
            'allow_return': allow_return,
            'organizer': organizer
        }

        st.success("Основная информация сохранена!")

    def _render_survey_questions_section(self):
        """Рендеринг секции вопросов опроса"""
        st.markdown("### ❓ Вопросы опроса")

        if 'survey_questions' not in st.session_state:
            st.session_state.survey_questions = []

        questions = st.session_state.survey_questions
        self._render_add_question_form()
        self._render_existing_questions(questions)

    def _render_add_question_form(self):
        """Рендеринг формы добавления вопроса"""
        with st.form("add_question_form"):
            st.markdown("#### Добавить новый вопрос")

            col_q1, col_q2 = st.columns([3, 1])
            with col_q1:
                question_text = st.text_input(
                    "Текст вопроса *",
                    key="new_question_text",
                    placeholder="Введите текст вопроса",
                    help="Формулировка вопроса должна быть четкой и понятной"
                )

            with col_q2:
                question_type = st.selectbox(
                    "Тип вопроса *",
                    ["single_choice", "multiple_choice", "text", "scale"],
                    format_func=lambda x: {
                        "single_choice": "Один вариант",
                        "multiple_choice": "Несколько вариантов",
                        "text": "Текстовый ответ",
                        "scale": "Шкала"
                    }[x],
                    key="new_question_type",
                    help="Выберите тип ответа на вопрос"
                )

            self._render_question_type_fields(question_type)

            add_question_submitted = st.form_submit_button("➕ Добавить вопрос")

            if add_question_submitted:
                self._handle_add_question_submission(question_text, question_type)

    def _render_question_type_fields(self, question_type):
        """Рендеринг полей в зависимости от типа вопроса"""
        if question_type in ["single_choice", "multiple_choice"]:
            options = st.text_area(
                "Варианты ответов * (каждый с новой строки)",
                placeholder="Вариант 1\nВариант 2\nВариант 3\n...",
                key="new_question_options",
                help="Каждый вариант ответа должен быть на новой строке"
            )
            required_options = st.checkbox("Обязательный вопрос", value=True,
                                           help="Участник должен ответить на этот вопрос")
            st.session_state.new_question_data = {'options': options, 'required': required_options}

        elif question_type == "scale":
            col_scale1, col_scale2 = st.columns(2)

            with col_scale1:
                min_scale = st.number_input("Минимальное значение", value=1,
                                            min_value=1, max_value=10,
                                            help="Минимальное значение шкалы")

            with col_scale2:
                max_scale = st.number_input("Максимальное значение", value=5,
                                            min_value=2, max_value=10,
                                            help="Максимальное значение шкалы")

            scale_label_left = st.text_input("Подпись слева", placeholder="Совсем не согласен")
            scale_label_right = st.text_input("Подпись справа", placeholder="Полностью согласен")

            st.session_state.new_question_data = {
                'min': min_scale, 'max': max_scale,
                'label_left': scale_label_left, 'label_right': scale_label_right
            }

    def _handle_add_question_submission(self, question_text, question_type):
        """Обработка добавления вопроса"""
        if not question_text:
            st.error("Введите текст вопроса!")
            return

        questions = st.session_state.survey_questions
        new_question = {
            'id': f"q_{len(questions) + 1:03d}",
            'text': question_text,
            'type': question_type,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        if question_type in ["single_choice", "multiple_choice"]:
            options = st.session_state.get('new_question_data', {}).get('options', '')
            option_list = [opt.strip() for opt in options.split('\n') if opt.strip()]

            if not option_list:
                st.error("Добавьте хотя бы один вариант ответа!")
                return

            new_question['options'] = option_list
            new_question['required'] = st.session_state.new_question_data.get('required', True)

        elif question_type == "scale":
            new_question.update(st.session_state.get('new_question_data', {}))

        questions.append(new_question)
        st.session_state.survey_questions = questions
        st.success(f"Вопрос добавлен: {question_text}")
        st.rerun()

    def _render_existing_questions(self, questions):
        """Рендеринг существующих вопросов"""
        if not questions:
            return

        st.markdown(f"#### Добавленные вопросы ({len(questions)})")

        for i, q in enumerate(questions, 1):
            with st.expander(f"Вопрос {i}: {q['text'][:50]}...", expanded=False):
                col_qd1, col_qd2 = st.columns([3, 1])

                with col_qd1:
                    self._render_question_details(q)

                with col_qd2:
                    self._render_question_actions(i, q, questions)

    def _render_question_details(self, question):
        """Рендеринг деталей вопроса"""
        q_type_display = {
            "single_choice": "Один вариант",
            "multiple_choice": "Несколько вариантов",
            "text": "Текстовый ответ",
            "scale": "Шкала"
        }.get(question['type'], question['type'])

        st.write(f"**Тип:** {q_type_display}")

        if 'options' in question:
            st.write("**Варианты ответов:**")
            for j, option in enumerate(question['options'], 1):
                st.write(f"  {j}. {option}")
        elif 'min' in question and 'max' in question:
            st.write(f"**Шкала:** от {question['min']} до {question['max']}")
            if 'label_left' in question:
                st.write(f"**Слева:** {question['label_left']}")
            if 'label_right' in question:
                st.write(f"**Справа:** {question['label_right']}")

        if question.get('required', False):
            st.write("**Обязательный:** Да")

    def _render_question_actions(self, index, question, questions):
        """Рендеринг действий с вопросом"""
        col_edit, col_del = st.columns(2)

        with col_edit:
            if st.button("✏️", key=f"edit_q_{index}"):
                st.info("Редактирование будет реализовано в следующей версии")

        with col_del:
            if st.button("🗑️", key=f"del_q_{index}"):
                questions.pop(index - 1)
                st.session_state.survey_questions = questions
                st.rerun()

    def _render_survey_actions(self, user_name):
        """Рендеринг действий с опросом"""
        st.markdown("---")

        col_actions1, col_actions2, col_actions3 = st.columns(3)

        with col_actions1:
            self._render_preview_button()

        with col_actions2:
            self._render_save_draft_button(user_name)

        with col_actions3:
            self._render_publish_button(user_name)

        self._render_survey_preview()

    def _render_preview_button(self):
        """Рендеринг кнопки предпросмотра"""
        has_basic_info = 'survey_basic_info' in st.session_state
        has_questions = bool(st.session_state.get('survey_questions', []))

        if st.button("👁️ Предпросмотр", use_container_width=True,
                     disabled=not (has_basic_info and has_questions)):
            if has_basic_info and has_questions:
                preview_data = {
                    **st.session_state.survey_basic_info,
                    'questions': st.session_state.survey_questions
                }
                st.session_state.survey_preview = preview_data
                st.rerun()
            else:
                st.error("Заполните основную информацию и добавьте хотя бы один вопрос")

    def _render_save_draft_button(self, user_name):
        """Рендеринг кнопки сохранения черновика"""
        has_basic_info = 'survey_basic_info' in st.session_state
        has_questions = bool(st.session_state.get('survey_questions', []))

        if st.button("💾 Сохранить как черновик", use_container_width=True,
                     disabled=not (has_basic_info and has_questions)):
            if has_basic_info and has_questions:
                self._save_survey_as_draft(user_name)

    def _save_survey_as_draft(self, user_name):
        """Сохранение опроса как черновика"""
        survey_data = {
            **st.session_state.survey_basic_info,
            'questions': st.session_state.survey_questions,
            'status': 'Черновик'
        }

        survey_id = self.storage.add(survey_data, user_name)
        st.success(f"Опрос сохранен как черновик! ID: {survey_id}")

        self._cleanup_survey_creation_state()

    def _render_publish_button(self, user_name):
        """Рендеринг кнопки публикации"""
        has_basic_info = 'survey_basic_info' in st.session_state
        has_questions = bool(st.session_state.get('survey_questions', []))

        if st.button("🚀 Опубликовать", use_container_width=True, type="primary",
                     disabled=not (has_basic_info and has_questions)):
            if has_basic_info and has_questions:
                self._publish_survey(user_name)

    def _publish_survey(self, user_name):
        """Публикация опроса"""
        survey_data = {
            **st.session_state.survey_basic_info,
            'questions': st.session_state.survey_questions,
            'status': 'Опубликован'
        }

        survey_id = self.storage.add(survey_data, user_name)
        st.success(f"Опрос опубликован! ID: {survey_id}")

        self._cleanup_survey_creation_state()

    def _cleanup_survey_creation_state(self):
        """Очистка состояния создания опроса"""
        if 'survey_basic_info' in st.session_state:
            del st.session_state.survey_basic_info
        if 'survey_questions' in st.session_state:
            st.session_state.survey_questions = []
        if 'survey_preview' in st.session_state:
            del st.session_state.survey_preview

        st.rerun()

    def _render_survey_preview(self):
        """Рендеринг предпросмотра опроса"""
        if not st.session_state.get('survey_preview'):
            return

        st.markdown("---")
        from controller.admin.survey_management import SurveyManager
        manager = SurveyManager()
        manager.show_preview(st.session_state.survey_preview)