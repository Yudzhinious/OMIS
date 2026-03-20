import streamlit as st
from datetime import datetime, timedelta


class SurveyStorage:

    def init(self):
        """Инициализация хранилища опросов"""
        if 'real_surveys' not in st.session_state:
            st.session_state.real_surveys = []

        if 'next_survey_id' not in st.session_state:
            st.session_state.next_survey_id = 1

        if 'published_surveys' not in st.session_state:
            st.session_state.published_surveys = []

    def add(self, survey_data, organizer_name):
        """Добавить реальный опрос в систему"""
        self.init()

        survey_id = f"SUR-{st.session_state.next_survey_id:03d}"
        st.session_state.next_survey_id += 1

        full_survey = {
            'id': survey_id,
            'name': survey_data.get('name', 'Без названия'),
            'description': survey_data.get('description', ''),
            'questions': survey_data.get('questions', []),
            'type': survey_data.get('type', 'Публичный'),
            'audience': survey_data.get('audience', ['Все']),
            'start_date': survey_data.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            'end_date': survey_data.get('end_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
            'anonymous': survey_data.get('anonymous', False),
            'show_progress': survey_data.get('show_progress', True),
            'allow_return': survey_data.get('allow_return', True),
            'status': survey_data.get('status', 'Черновик'),
            'organizer': organizer_name,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'responses': 0
        }

        st.session_state.real_surveys.append(full_survey)

        if full_survey['status'] == 'Опубликован':
            st.session_state.published_surveys.append(full_survey)

        return survey_id

    def toggle_publication(self, survey_id, new_status):
        """Переключить статус публикации опроса"""
        if 'real_surveys' not in st.session_state:
            return

        for i, survey in enumerate(st.session_state.real_surveys):
            if survey['id'] == survey_id:
                st.session_state.real_surveys[i]['status'] = new_status

                if new_status == 'Опубликован':
                    if survey not in st.session_state.published_surveys:
                        st.session_state.published_surveys.append(survey)
                elif survey in st.session_state.published_surveys:
                    st.session_state.published_surveys.remove(survey)

                st.success(f"Статус опроса изменен на '{new_status}'")
                break

    def delete(self, survey_id):
        """Удалить опрос"""
        if 'real_surveys' in st.session_state:
            st.session_state.real_surveys = [
                s for s in st.session_state.real_surveys
                if s['id'] != survey_id
            ]

        if 'published_surveys' in st.session_state:
            st.session_state.published_surveys = [
                s for s in st.session_state.published_surveys
                if s['id'] != survey_id
            ]

        if 'saved_surveys' in st.session_state:
            st.session_state.saved_surveys = [
                s for s in st.session_state.saved_surveys
                if s.get('id') != survey_id
            ]