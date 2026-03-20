import streamlit as st
import random
from datetime import datetime, timedelta

class OrganizerStorage:

    def init_data_storage(self):
        """Инициализация всех хранилищ данных"""
        self._init_reports_storage()
        self._init_survey_responses_storage()
        self._init_user_demographics_storage()
        self._init_active_users_data()
        self._init_survey_responses_for_existing_surveys()

    def _init_reports_storage(self):
        """Инициализация хранилища отчетов"""
        if 'reports' not in st.session_state:
            st.session_state.reports = []

        if 'next_report_id' not in st.session_state:
            st.session_state.next_report_id = 1

    def _init_survey_responses_storage(self):
        """Инициализация хранилища ответов на опросы"""
        if 'survey_responses' not in st.session_state:
            st.session_state.survey_responses = {}

    def _init_user_demographics_storage(self):
        """Инициализация хранилища статистики пользователей"""
        if 'user_demographics' not in st.session_state:
            st.session_state.user_demographics = []

    def _init_active_users_data(self):
        """Инициализация данных активных пользователей"""
        if 'active_users_data' not in st.session_state:
            st.session_state.active_users_data = self._create_demo_active_users()

    def _create_demo_active_users(self):
        """Создание демо-данных активных пользователей"""
        return [
            {'user_id': 'user_1', 'age': 25, 'gender': 'Мужчина', 'city': 'Москва', 'registration_date': '2024-01-15'},
            {'user_id': 'user_2', 'age': 32, 'gender': 'Женщина', 'city': 'Санкт-Петербург',
             'registration_date': '2024-01-20'},
            {'user_id': 'user_3', 'age': 28, 'gender': 'Мужчина', 'city': 'Новосибирск',
             'registration_date': '2024-02-10'},
            {'user_id': 'user_4', 'age': 45, 'gender': 'Женщина', 'city': 'Екатеринбург',
             'registration_date': '2024-02-15'},
            {'user_id': 'user_5', 'age': 22, 'gender': 'Мужчина', 'city': 'Казань', 'registration_date': '2024-03-01'},
            {'user_id': 'user_6', 'age': 38, 'gender': 'Женщина', 'city': 'Москва', 'registration_date': '2024-03-05'},
            {'user_id': 'user_7', 'age': 29, 'gender': 'Мужчина', 'city': 'Санкт-Петербург',
             'registration_date': '2024-03-10'},
            {'user_id': 'user_8', 'age': 41, 'gender': 'Женщина', 'city': 'Новосибирск',
             'registration_date': '2024-03-15'},
            {'user_id': 'user_9', 'age': 26, 'gender': 'Мужчина', 'city': 'Москва', 'registration_date': '2024-03-20'},
            {'user_id': 'user_10', 'age': 34, 'gender': 'Женщина', 'city': 'Екатеринбург',
             'registration_date': '2024-03-25'}
        ]

    def _init_survey_responses_for_existing_surveys(self):
        """Инициализация данных опросов"""
        if 'real_surveys' not in st.session_state:
            return

        for survey in st.session_state.real_surveys:
            survey_id = survey.get('id')
            if not survey_id:
                continue

            if survey_id not in st.session_state.survey_responses:
                st.session_state.survey_responses[survey_id] = {
                    'total_responses': 0,
                    'completion_rate': 0,
                    'average_time': 0,
                    'responses': [],
                    'demographics': {'age': {}, 'gender': {}, 'city': {}}
                }

    def generate_real_survey_data(self, survey_id):
        """Генерация реальных данных для опроса"""
        if survey_id not in st.session_state.survey_responses:
            self._init_survey_response_data(survey_id)

        survey_data = st.session_state.survey_responses[survey_id]
        self._generate_demo_responses_if_empty(survey_id, survey_data)

        return survey_data

    def _init_survey_response_data(self, survey_id):
        """Инициализация данных ответов для опроса"""
        st.session_state.survey_responses[survey_id] = {
            'total_responses': 0,
            'completion_rate': 0,
            'average_time': 0,
            'responses': [],
            'demographics': {'age': {}, 'gender': {}, 'city': {}},
            'daily_trends': {}
        }

    def _generate_demo_responses_if_empty(self, survey_id, survey_data):
        """Генерация демо-ответов если нет реальных"""
        if survey_data['responses']:
            return

        if not st.session_state.active_users_data:
            return

        self._generate_random_responses(survey_id, survey_data)

    def _generate_random_responses(self, survey_id, survey_data):
        """Генерация случайных ответов"""
        num_responses = random.randint(
            int(len(st.session_state.active_users_data) * 0.3),
            int(len(st.session_state.active_users_data) * 0.8)
        )

        selected_users = random.sample(
            st.session_state.active_users_data,
            min(num_responses, len(st.session_state.active_users_data))
        )

        for user in selected_users:
            self._add_demo_response(survey_id, survey_data, user)

        self._update_survey_stats(survey_data)
        self._generate_daily_trends(survey_data)

    def _add_demo_response(self, survey_id, survey_data, user):
        """Добавление демо-ответа"""
        response = {
            'user_id': user['user_id'],
            'survey_id': survey_id,
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 30)),
            'completion_time': random.randint(60, 600),
            'answers': {},
            'demographics': {
                'age': user['age'],
                'gender': user['gender'],
                'city': user['city']
            }
        }

        self._update_demographics(survey_data, response['demographics'])
        survey_data['responses'].append(response)

    def _update_demographics(self, survey_data, demographics):
        """Обновление демографических данных"""
        age = demographics['age']
        gender = demographics['gender']
        city = demographics['city']

        survey_data['demographics']['age'][age] = survey_data['demographics']['age'].get(age, 0) + 1
        survey_data['demographics']['gender'][gender] = survey_data['demographics']['gender'].get(gender, 0) + 1
        survey_data['demographics']['city'][city] = survey_data['demographics']['city'].get(city, 0) + 1

    def _update_survey_stats(self, survey_data):
        """Обновление статистики опроса"""
        survey_data['total_responses'] = len(survey_data['responses'])
        survey_data['completion_rate'] = random.randint(85, 98)

        if survey_data['responses']:
            avg_time = sum(r['completion_time'] for r in survey_data['responses']) / len(survey_data['responses'])
            survey_data['average_time'] = avg_time

    def _generate_daily_trends(self, survey_data):
        """Генерация дневных трендов"""
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            survey_data['daily_trends'][date] = random.randint(0, len(survey_data['responses']) // 3)

    def add_survey_response(self, survey_id, user_data, answers, completion_time):
        """Добавить ответ на опрос в реальные данные"""
        self.init_data_storage()

        if survey_id not in st.session_state.survey_responses:
            self._init_survey_response_data(survey_id)

        survey_data = st.session_state.survey_responses[survey_id]
        response = self._create_response_object(survey_id, user_data, answers, completion_time)

        self._add_response_to_survey_data(survey_data, response)
        self._update_response_analytics(survey_data, response)

        return response

    def _create_response_object(self, survey_id, user_data, answers, completion_time):
        """Создание объекта ответа"""
        return {
            'user_id': user_data.get('user_id', f'user_{len(st.session_state.active_users_data) + 1}'),
            'survey_id': survey_id,
            'timestamp': datetime.now(),
            'completion_time': completion_time,
            'answers': answers,
            'demographics': {
                'age': user_data.get('age', random.randint(18, 65)),
                'gender': user_data.get('gender', random.choice(['Мужчина', 'Женщина'])),
                'city': user_data.get('city', self._get_random_city())
            }
        }

    def _get_random_city(self):
        """Получение случайного города"""
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
        return random.choice(cities)

    def _add_response_to_survey_data(self, survey_data, response):
        """Добавление ответа в данные опроса"""
        survey_data['responses'].append(response)
        survey_data['total_responses'] = len(survey_data['responses'])

    def _update_response_analytics(self, survey_data, response):
        """Обновление аналитики ответов"""
        self._update_demographics(survey_data, response['demographics'])
        self._update_daily_trends(survey_data)
        self._recalculate_survey_stats(survey_data)
        self._add_user_if_new(response)

    def _update_daily_trends(self, survey_data):
        """Обновление дневных трендов"""
        today = datetime.now().strftime('%Y-%m-%d')
        survey_data['daily_trends'][today] = survey_data['daily_trends'].get(today, 0) + 1

    def _recalculate_survey_stats(self, survey_data):
        """Пересчет статистики опроса"""
        if not survey_data['responses']:
            return

        total_responses = survey_data['total_responses']
        survey_data['completion_rate'] = min(100,
                                             (total_responses / max(1, total_responses + random.randint(0, 5))) * 100)

        total_time = sum(r['completion_time'] for r in survey_data['responses'])
        survey_data['average_time'] = total_time / len(survey_data['responses'])

    def _add_user_if_new(self, response):
        """Добавление пользователя если он новый"""
        user_id = response['user_id']
        demographics = response['demographics']

        user_exists = any(u['user_id'] == user_id for u in st.session_state.active_users_data)
        if user_exists or not user_id.startswith('user_'):
            return

        st.session_state.active_users_data.append({
            'user_id': user_id,
            'age': demographics['age'],
            'gender': demographics['gender'],
            'city': demographics['city'],
            'registration_date': datetime.now().strftime('%Y-%m-%d')
        })