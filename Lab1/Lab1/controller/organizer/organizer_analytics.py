import random
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from controller.organizer.organizer_storage import OrganizerStorage
from controller.organizer.organizer_reports import (
    ComprehensiveReportGenerator,
    TrendsReportGenerator,
    DemographicReportGenerator
)


class AnalyticsRenderer:

    def __init__(self, storage: OrganizerStorage):
        self.storage = storage
        self.report_generators = {
            'comprehensive': ComprehensiveReportGenerator(storage),
            'trends': TrendsReportGenerator(storage),
            'demographic': DemographicReportGenerator(storage)
        }

    def show_organizer_analytics(self):
        """Отображение аналитики организатора"""
        self.storage.init_data_storage()

        st.markdown("## 📊 Аналитика")
        self._render_analytics_filters()
        self._render_analytics_metrics()
        self._render_analytics_charts()
        self._render_analytics_table()
        self._render_quick_report_generation()

    def _render_analytics_filters(self):
        """Рендеринг фильтров аналитики"""
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            time_period = st.selectbox("Период",
                                       ["Последние 7 дней", "Последние 30 дней", "Последние 90 дней", "Всё время"])

        with col_f2:
            real_surveys = st.session_state.get('real_surveys', [])
            survey_names = ["Все опросы"] + [s.get('name', f'Опрос {i + 1}') for i, s in enumerate(real_surveys)]
            survey_filter = st.selectbox("Опрос", survey_names)

        with col_f3:
            metric_type = st.selectbox("Метрика",
                                       ["Ответы", "Завершение", "Время", "Удовлетворенность"])

    def _render_analytics_metrics(self):
        """Рендеринг метрик аналитики"""
        total_responses, avg_completion, avg_time, avg_satisfaction = self._calculate_analytics_metrics()

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.metric("Всего ответов", f"{total_responses}", f"+{random.randint(10, 100)} за неделю")

        with col_m2:
            st.metric("Средний рейтинг", f"{avg_satisfaction:.1f}/5", f"+{random.uniform(0.1, 0.5):.1f}")

        with col_m3:
            st.metric("Время заполнения", f"{avg_time:.1f} мин", f"-{random.uniform(0.1, 0.5):.1f}")

        with col_m4:
            st.metric("Завершение", f"{avg_completion:.0f}%", f"+{random.randint(1, 5)}%")

    def _calculate_analytics_metrics(self):
        """Расчет метрик аналитики"""
        total_responses = 0
        completion_rates = []
        completion_times = []
        satisfaction_scores = []

        for survey in st.session_state.get('real_surveys', []):
            survey_id = survey.get('id')
            if not survey_id:
                continue

            survey_data = self.storage.generate_real_survey_data(survey_id)
            total_responses += survey_data['total_responses']
            completion_rates.append(survey_data['completion_rate'])
            completion_times.append(survey_data['average_time'])
            satisfaction_scores.append(random.randint(35, 50) / 10)

        avg_completion = np.mean(completion_rates) if completion_rates else 0
        avg_time = np.mean(completion_times) / 60 if completion_times else 0
        avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0

        return total_responses, avg_completion, avg_time, avg_satisfaction

    def _render_analytics_charts(self):
        """Рендеринг графиков аналитики"""
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            self._render_response_distribution_chart()

        with col_g2:
            self._render_satisfaction_chart()

    def _render_response_distribution_chart(self):
        """Рендеринг графика распределения ответов"""
        st.markdown("#### Распределение ответов по опросам")

        response_data = self._prepare_response_distribution_data()
        if not response_data:
            st.info("Нет данных для отображения")
            return

        response_df = pd.DataFrame(response_data)
        fig1 = px.bar(response_df, x='Опрос', y='Ответы', color='Опрос')
        st.plotly_chart(fig1, use_container_width=True)

    def _prepare_response_distribution_data(self):
        """Подготовка данных распределения ответов"""
        response_data = []
        for survey in st.session_state.get('real_surveys', []):
            survey_id = survey.get('id')
            if not survey_id:
                continue

            survey_data = self.storage.generate_real_survey_data(survey_id)
            response_data.append({
                'Опрос': survey.get('name', 'Без названия'),
                'Ответы': survey_data['total_responses']
            })

        return response_data

    def _render_satisfaction_chart(self):
        """Рендеринг графика удовлетворенности"""
        st.markdown("#### Удовлетворенность по опросам")

        satisfaction_data = self._prepare_satisfaction_data()
        if not satisfaction_data:
            st.info("Нет данных для отображения")
            return

        satisfaction_df = pd.DataFrame(satisfaction_data)
        fig2 = px.line(satisfaction_df, x='Опрос', y='Удовлетворенность', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    def _prepare_satisfaction_data(self):
        """Подготовка данных удовлетворенности"""
        satisfaction_data = []
        for survey in st.session_state.get('real_surveys', []):
            survey_id = survey.get('id')
            if not survey_id:
                continue

            survey_data = self.storage.generate_real_survey_data(survey_id)
            satisfaction_score = min(5.0, max(1.0, survey_data['completion_rate'] / 20))
            satisfaction_data.append({
                'Опрос': survey.get('name', 'Без названия'),
                'Удовлетворенность': satisfaction_score
            })

        return satisfaction_data

    def _render_analytics_table(self):
        """Рендеринг таблицы аналитики"""
        st.markdown("#### Детальная статистика по опросам")

        stats_data = self._prepare_detailed_stats_data()
        if not stats_data:
            st.info("Нет данных для отображения")
            return

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)

    def _prepare_detailed_stats_data(self):
        """Подготовка детальной статистики"""
        stats_data = []
        for survey in st.session_state.get('real_surveys', []):
            survey_id = survey.get('id')
            if not survey_id:
                continue

            survey_data = self.storage.generate_real_survey_data(survey_id)
            stats_data.append({
                'Название опроса': survey.get('name', 'Без названия'),
                'Статус': survey.get('status', 'Неизвестно'),
                'Ответы': survey_data['total_responses'],
                'Завершение': f"{survey_data['completion_rate']:.0f}%",
                'Средний балл': f"{survey_data['completion_rate'] / 20:.1f}/5",
                'Среднее время': f"{survey_data['average_time'] / 60:.1f} мин"
            })

        return stats_data

    def _render_quick_report_generation(self):
        """Рендеринг быстрой генерации отчетов"""
        st.markdown("---")
        st.markdown("### 🚀 Быстрая генерация отчетов в TXT")

        col_auto1, col_auto2, col_auto3 = st.columns(3)

        with col_auto1:
            self._render_comprehensive_report_button()

        with col_auto2:
            self._render_trends_report_button()

        with col_auto3:
            self._render_demographic_report_button()

    def _render_comprehensive_report_button(self):
        """Рендеринг кнопки сводного отчета"""
        if st.button("📊 Создать сводный отчет", use_container_width=True):
            txt_content = self.report_generators['comprehensive'].generate_comprehensive_txt_report()
            if txt_content:
                self._render_download_button(txt_content, "Сводный_отчет", "📥 Скачать отчет в TXT")

    def _render_trends_report_button(self):
        """Рендеринг кнопки отчета по трендам"""
        if st.button("📈 Тренды ответов", use_container_width=True):
            txt_content = self.report_generators['trends'].generate_trends_txt_report()
            if txt_content:
                self._render_download_button(txt_content, "Тренды_ответов", "📥 Скачать отчет в TXT")

    def _render_demographic_report_button(self):
        """Рендеринг кнопки демографического отчета"""
        if st.button("👥 Демографический анализ", use_container_width=True):
            txt_content = self.report_generators['demographic'].generate_demographic_txt_report()
            if txt_content:
                self._render_download_button(txt_content, "Демографический_анализ", "📥 Скачать отчет в TXT")

    def _render_download_button(self, content, file_prefix, button_label):
        """Рендеринг кнопки скачивания"""
        st.download_button(
            label=button_label,
            data=content,
            file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )