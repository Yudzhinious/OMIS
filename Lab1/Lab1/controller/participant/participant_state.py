import streamlit as st
from datetime import datetime
import random


class ParticipantState:

    def __init__(self):
        self.storage = None
        self.init_storage()

    def init_storage(self):
        """Инициализация хранилища"""
        try:
            from controller.organizer.organizer_pages import OrganizerStorage
            self.storage = OrganizerStorage()
            self.storage.init_data_storage()
        except ImportError:
            st.warning("Организаторское хранилище недоступно")

    def init_session_state(self):
        """Инициализация состояния сессии"""
        if 'completed_surveys' not in st.session_state:
            st.session_state.completed_surveys = []

        if 'user_points' not in st.session_state:
            st.session_state.user_points = 0

        if 'user_stats' not in st.session_state:
            st.session_state.user_stats = {
                'total_surveys': 0, 'total_points': 0, 'avg_score': 0,
                'total_time': 0, 'last_completed': None
            }

        self.init_session_reports()
        self.init_current_user()

    def init_session_reports(self):
        """Инициализация отчетов в session_state"""
        if 'available_reports' not in st.session_state:
            st.session_state.available_reports = [
                {
                    'id': 1, 'title': 'Общий отчет по опросам Q1 2024',
                    'description': 'Сводная статистика по всем опросов за первый квартал',
                    'type': 'Сводный', 'date': '15.03.2024', 'access': 'public'
                },
                {
                    'id': 2, 'title': 'Анализ удовлетворенности клиентов',
                    'description': 'Детальный анализ ответов по опросу удовлетворенности',
                    'type': 'Аналитический', 'date': '10.03.2024', 'access': 'public'
                },
                {
                    'id': 3, 'title': 'Демографические данные участников',
                    'description': 'Распределение участников по возрасту, полу и географии',
                    'type': 'Детальный', 'date': '05.03.2024', 'access': 'public'
                }
            ]

    def init_current_user(self):
        """Инициализация текущего пользователя"""
        if 'current_user' not in st.session_state:
            cities = ['Москва', 'Санкт-Петербург', 'Новосибирск',
                      'Екатеринбург', 'Казань']
            st.session_state.current_user = {
                'id': f'participant_{random.randint(1000, 9999)}',
                'name': 'Участник', 'age': random.randint(18, 65),
                'gender': random.choice(['Мужчина', 'Женщина']),
                'city': random.choice(cities)
            }

    def save_completed_survey(self, survey_data, answers, time_spent, score=None):
        """Сохранение пройденного опроса"""
        completed_survey = self._create_completed_survey_object(
            survey_data, answers, time_spent, score
        )

        st.session_state.completed_surveys.append(completed_survey)
        self._update_user_stats(completed_survey, score)

        return completed_survey

    def _create_completed_survey_object(self, survey_data, answers, time_spent, score):
        """Создание объекта пройденного опроса"""
        return {
            'id': survey_data.get('id', 'unknown'),
            'title': survey_data.get('name', 'Без названия'),
            'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'status': 'Завершен',
            'score': f"{score}/100" if score else "Нет оценки",
            'time': f"{time_spent} мин",
            'questions': len(survey_data.get('questions', [])),
            'points': 10,
            'answers': answers.copy(),
            'raw_score': score,
            'time_spent': time_spent,
            'survey_data': survey_data
        }

    def _update_user_stats(self, completed_survey, score):
        """Обновление статистики пользователя"""
        st.session_state.user_points += 10
        st.session_state.user_stats['total_surveys'] = len(
            st.session_state.completed_surveys
        )
        st.session_state.user_stats['total_points'] = st.session_state.user_points
        st.session_state.user_stats['last_completed'] = datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )

        if score is not None:
            scores = [s['raw_score'] for s in st.session_state.completed_surveys
                      if s['raw_score'] is not None]
            if scores:
                st.session_state.user_stats['avg_score'] = sum(scores) / len(scores)

        st.session_state.user_stats['total_time'] = sum(
            s.get('time_spent', 0) for s in st.session_state.completed_surveys
        )