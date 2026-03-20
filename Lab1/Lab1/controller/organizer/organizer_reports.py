import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from controller.organizer.organizer_storage import OrganizerStorage


class ReportGenerator:

    def __init__(self, storage: OrganizerStorage):
        self.storage = storage

    def generate_survey_report_txt(self, survey, survey_data):
        """Генерация отчета по опросу в TXT формате"""
        report_lines = []

        report_lines.append("=" * 60)
        report_lines.append(f"ОТЧЕТ ПО ОПРОСУ")
        report_lines.append(f"Название: {survey.get('name', 'Без названия')}")
        report_lines.append(f"ID: {survey.get('id', 'N/A')}")
        report_lines.append(f"Статус: {survey.get('status', 'Неизвестно')}")
        report_lines.append(f"Дата создания: {survey.get('created_date', 'Неизвестно')}")
        report_lines.append("=" * 60)
        report_lines.append("")

        self._add_basic_metrics_to_report(report_lines, survey_data)
        self._add_demographics_to_report(report_lines, survey_data)
        self._add_trends_to_report(report_lines, survey_data)
        self._add_survey_info_to_report(report_lines, survey)

        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append(f"Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def _add_basic_metrics_to_report(self, report_lines, survey_data):
        """Добавление основных метрик в отчет"""
        report_lines.append("📊 ОСНОВНЫЕ МЕТРИКИ:")
        report_lines.append(f"  • Всего ответов: {survey_data['total_responses']}")
        report_lines.append(f"  • Процент завершения: {survey_data['completion_rate']:.1f}%")
        report_lines.append(f"  • Среднее время заполнения: {survey_data['average_time'] / 60:.1f} минут")
        report_lines.append("")

    def _add_demographics_to_report(self, report_lines, survey_data):
        """Добавление демографических данных в отчет"""
        report_lines.append("👥 ДЕМОГРАФИЧЕСКИЕ ДАННЫЕ:")

        if survey_data['demographics']['age']:
            report_lines.append("  Возрастное распределение:")
            for age, count in sorted(survey_data['demographics']['age'].items()):
                percentage = (count / survey_data['total_responses'] * 100) if survey_data['total_responses'] > 0 else 0
                report_lines.append(f"    • {age} лет: {count} чел. ({percentage:.1f}%)")

        if survey_data['demographics']['gender']:
            report_lines.append("  Гендерное распределение:")
            for gender, count in survey_data['demographics']['gender'].items():
                percentage = (count / survey_data['total_responses'] * 100) if survey_data['total_responses'] > 0 else 0
                report_lines.append(f"    • {gender}: {count} чел. ({percentage:.1f}%)")

        if survey_data['demographics']['city']:
            report_lines.append("  Географическое распределение:")
            for city, count in survey_data['demographics']['city'].items():
                percentage = (count / survey_data['total_responses'] * 100) if survey_data['total_responses'] > 0 else 0
                report_lines.append(f"    • {city}: {count} чел. ({percentage:.1f}%)")

    def _add_trends_to_report(self, report_lines, survey_data):
        """Добавление трендов в отчет"""
        report_lines.append("📈 ТРЕНДЫ ОТВЕТОВ:")

        if survey_data.get('daily_trends'):
            total_days = len(survey_data['daily_trends'])
            total_responses_trend = sum(survey_data['daily_trends'].values())
            avg_daily = total_responses_trend / total_days if total_days > 0 else 0

            report_lines.append(f"  • Всего дней с ответами: {total_days}")
            report_lines.append(f"  • Всего ответов за период: {total_responses_trend}")
            report_lines.append(f"  • Среднедневное количество ответов: {avg_daily:.1f}")

            last_7_days = sorted(survey_data['daily_trends'].items(), key=lambda x: x[0], reverse=True)[:7]
            report_lines.append("  • Последние 7 дней:")
            for date, count in last_7_days:
                report_lines.append(f"    • {date}: {count} ответов")
        else:
            report_lines.append("  • Нет данных о трендах")

    def _add_survey_info_to_report(self, report_lines, survey):
        """Добавление информации об опросе в отчет"""
        report_lines.append("")
        report_lines.append("📝 ИНФОРМАЦИЯ ОБ ОПРОСЕ:")
        report_lines.append(f"  • Количество вопросов: {len(survey.get('questions', []))}")
        report_lines.append(f"  • Тип опроса: {survey.get('type', 'Неизвестно')}")
        report_lines.append(f"  • Дата начала: {survey.get('start_date', 'Неизвестно')}")
        report_lines.append(f"  • Дата окончания: {survey.get('end_date', 'Неизвестно')}")


class ComprehensiveReportGenerator(ReportGenerator):

    def generate_comprehensive_txt_report(self):
        """Генерация сводного отчета в TXT формате"""
        self.storage.init_data_storage()

        report_lines = []
        self._add_report_header(report_lines, "СВОДНЫЙ ОТЧЕТ ПО ВСЕМ ОПРОСАМ")
        self._add_general_statistics(report_lines)
        self._add_surveys_statistics(report_lines)
        self._add_user_activity_analysis(report_lines)
        self._add_recommendations(report_lines)
        self._add_report_footer(report_lines)

        return "\n".join(report_lines)

    def _add_report_header(self, report_lines, title):
        """Добавление заголовка отчета"""
        report_lines.append("=" * 60)
        report_lines.append(title)
        report_lines.append(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")

    def _add_general_statistics(self, report_lines):
        """Добавление общей статистики в отчет"""
        total_surveys, total_responses, avg_completion, avg_time = self._calculate_dashboard_metrics()

        report_lines.append("📊 ОБЩАЯ СТАТИСТИКА:")
        report_lines.append(f"  • Всего опросов: {total_surveys}")
        report_lines.append(f"  • Всего ответов: {total_responses}")
        report_lines.append(f"  • Средний процент завершения: {avg_completion:.1f}%")
        report_lines.append(f"  • Среднее время заполнения: {avg_time:.1f} мин.")
        report_lines.append("")

    def _calculate_dashboard_metrics(self):
        """Расчет метрик дашборда"""
        total_surveys = len(st.session_state.get('real_surveys', []))
        total_responses = 0
        completion_rate_sum = 0
        avg_time_sum = 0

        for survey in st.session_state.get('real_surveys', []):
            survey_id = survey.get('id')
            if not survey_id:
                continue

            survey_data = self.storage.generate_real_survey_data(survey_id)
            total_responses += survey_data['total_responses']
            completion_rate_sum += survey_data['completion_rate']
            avg_time_sum += survey_data['average_time']

        avg_completion = completion_rate_sum / total_surveys if total_surveys > 0 else 0
        avg_time = avg_time_sum / total_surveys if total_surveys > 0 else 0

        return total_surveys, total_responses, avg_completion, avg_time

    def _add_surveys_statistics(self, report_lines):
        """Добавление статистики по опросам в отчет"""
        report_lines.append("📋 СТАТИСТИКА ПО ОПРОСАМ:")
        report_lines.append("")

        for i, survey in enumerate(st.session_state.get('real_surveys', []), 1):
            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            report_lines.append(f"{i}. {survey.get('name', 'Без названия')}")
            report_lines.append(f"   • ID: {survey.get('id', 'N/A')}")
            report_lines.append(f"   • Статус: {survey.get('status', 'Неизвестно')}")
            report_lines.append(f"   • Ответов: {survey_data['total_responses']}")
            report_lines.append(f"   • Завершение: {survey_data['completion_rate']:.1f}%")
            report_lines.append(f"   • Время: {survey_data['average_time'] / 60:.1f} мин.")
            report_lines.append(f"   • Вопросов: {len(survey.get('questions', []))}")
            report_lines.append("")

    def _add_user_activity_analysis(self, report_lines):
        """Добавление анализа активности пользователей в отчет"""
        report_lines.append("👥 АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЕЙ:")
        report_lines.append(f"  • Всего активных пользователей: {len(st.session_state.active_users_data)}")

        ages = [user['age'] for user in st.session_state.active_users_data]
        genders = [user['gender'] for user in st.session_state.active_users_data]
        cities = [user['city'] for user in st.session_state.active_users_data]

        report_lines.append(f"  • Средний возраст: {np.mean(ages):.1f} лет")
        report_lines.append(f"  • Медианный возраст: {np.median(ages):.1f} лет")

        gender_counts = pd.Series(genders).value_counts()
        report_lines.append("  • Распределение по полу:")
        for gender, count in gender_counts.items():
            percentage = (count / len(genders)) * 100
            report_lines.append(f"    • {gender}: {count} ({percentage:.1f}%)")

        city_counts = pd.Series(cities).value_counts().head(5)
        report_lines.append("  • Топ-5 городов:")
        for city, count in city_counts.items():
            percentage = (count / len(cities)) * 100
            report_lines.append(f"    • {city}: {count} ({percentage:.1f}%)")

    def _add_recommendations(self, report_lines):
        """Добавление рекомендаций в отчет"""
        report_lines.append("")
        report_lines.append("📈 ВЫВОДЫ И РЕКОМЕНДАЦИИ:")
        report_lines.append("  1. Рекомендуется увеличить количество активных опросов")
        report_lines.append("  2. Обратить внимание на опросы с низким процентом завершения")
        report_lines.append("  3. Рассмотреть возможность таргетирования по возрастным группам")
        report_lines.append("  4. Улучшить мобильную версию для увеличения вовлеченности")

    def _add_report_footer(self, report_lines):
        """Добавление подвала отчета"""
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("Конец отчета")
        report_lines.append("=" * 60)


class TrendsReportGenerator(ComprehensiveReportGenerator):

    def generate_trends_txt_report(self):
        """Генерация отчета по трендам в TXT формате"""
        self.storage.init_data_storage()

        report_lines = []
        self._add_report_header(report_lines, "ОТЧЕТ ПО ТРЕНДАМ ОТВЕТОВ")
        self._add_trends_analysis(report_lines)
        self._add_trends_by_surveys(report_lines)
        self._add_trends_recommendations(report_lines)
        self._add_report_footer(report_lines)

        return "\n".join(report_lines)

    def _add_trends_analysis(self, report_lines):
        """Добавление анализа трендов в отчет"""
        report_lines.append("📈 АНАЛИЗ ТРЕНДОВ ПО ДНЯМ:")
        report_lines.append("")

        all_daily_trends = self._get_all_daily_trends()
        if not all_daily_trends:
            report_lines.append("  • Нет данных о трендах за последние 30 дней")
            return

        sorted_dates = sorted(all_daily_trends.items(), key=lambda x: x[0])
        total_responses = sum(all_daily_trends.values())
        avg_daily = total_responses / len(all_daily_trends)

        report_lines.append(f"  • Всего ответов за период: {total_responses}")
        report_lines.append(f"  • Среднедневное количество ответов: {avg_daily:.1f}")
        report_lines.append(f"  • Максимальное за день: {max(all_daily_trends.values())}")
        report_lines.append(f"  • Минимальное за день: {min(all_daily_trends.values())}")
        report_lines.append("")

        self._add_last_14_days_analysis(report_lines, all_daily_trends)

    def _get_all_daily_trends(self):
        """Получение всех дневных трендов"""
        all_daily_trends = {}
        for survey in st.session_state.get('real_surveys', []):
            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            if not survey_data.get('daily_trends'):
                continue

            for date, count in survey_data['daily_trends'].items():
                all_daily_trends[date] = all_daily_trends.get(date, 0) + count

        return all_daily_trends

    def _add_last_14_days_analysis(self, report_lines, all_daily_trends):
        """Добавление анализа последних 14 дней"""
        last_14_days = sorted(all_daily_trends.items(), key=lambda x: x[0], reverse=True)[:14]
        report_lines.append("  • Динамика за последние 14 дней:")
        for date, count in last_14_days:
            report_lines.append(f"    • {date}: {count} ответов")

        if len(last_14_days) >= 2:
            self._add_change_analysis(report_lines, last_14_days)

    def _add_change_analysis(self, report_lines, last_14_days):
        """Добавление анализа изменений"""
        first_day = last_14_days[-1][1]
        last_day = last_14_days[0][1]
        change = ((last_day - first_day) / first_day * 100) if first_day > 0 else 0

        report_lines.append("")
        report_lines.append("  • Анализ изменений:")
        report_lines.append(f"    • Изменение за 14 дней: {change:+.1f}%")

        if change > 0:
            report_lines.append("    • Тренд: 📈 РОСТ")
        elif change < 0:
            report_lines.append("    • Тренд: 📉 СНИЖЕНИЕ")
        else:
            report_lines.append("    • Тренд: ↔️ СТАБИЛЬНО")

    def _add_trends_by_surveys(self, report_lines):
        """Добавление трендов по опросам"""
        report_lines.append("")
        report_lines.append("📊 ТРЕНДЫ ПО ОПРОСАМ:")
        report_lines.append("")

        for survey in st.session_state.get('real_surveys', []):
            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            if not survey_data.get('daily_trends'):
                continue

            trend_data = survey_data['daily_trends']
            total = sum(trend_data.values())
            avg = total / len(trend_data) if trend_data else 0

            report_lines.append(f"  • {survey.get('name', 'Без названия')}:")
            report_lines.append(f"    • Всего ответов: {total}")
            report_lines.append(f"    • Среднедневно: {avg:.1f}")

            if trend_data:
                peak_day = max(trend_data.items(), key=lambda x: x[1])
                report_lines.append(f"    • Пиковый день: {peak_day[0]} ({peak_day[1]} ответов)")
            report_lines.append("")

    def _add_trends_recommendations(self, report_lines):
        """Добавление рекомендаций по трендам"""
        report_lines.append("🎯 РЕКОМЕНДАЦИИ ПО ТРЕНДАМ:")
        report_lines.append("  1. Запускать новые опросы в дни с высокой активностью")
        report_lines.append("  2. Анализировать причины спадов в активности")
        report_lines.append("  3. Рассмотреть повторный запуск успешных опросов")
        report_lines.append("  4. Мониторить сезонные колебания активности")


class DemographicReportGenerator(ComprehensiveReportGenerator):
    """Класс для генерации демографических отчетов"""

    def generate_demographic_txt_report(self):
        """Генерация демографического отчета в TXT формате"""
        self.storage.init_data_storage()

        report_lines = []
        self._add_report_header(report_lines, "ДЕМОГРАФИЧЕСКИЙ АНАЛИЗ АУДИТОРИИ")
        self._add_general_demographics(report_lines)
        self._add_age_analysis(report_lines)
        self._add_gender_analysis(report_lines)
        self._add_geographic_analysis(report_lines)
        self._add_surveys_demographics(report_lines)
        self._add_demographic_recommendations(report_lines)
        self._add_report_footer(report_lines)

        return "\n".join(report_lines)

    def _add_general_demographics(self, report_lines):
        """Добавление общей демографической статистики"""
        report_lines.append("👥 ОБЩАЯ ДЕМОГРАФИЧЕСКАЯ СТАТИСТИКА:")
        report_lines.append(f"  • Всего активных пользователей: {len(st.session_state.active_users_data)}")
        report_lines.append("")

    def _add_age_analysis(self, report_lines):
        ages = [user['age'] for user in st.session_state.active_users_data]

        report_lines.append("📊 ВОЗРАСТНОЙ АНАЛИЗ:")
        report_lines.append(f"  • Средний возраст: {np.mean(ages):.1f} лет")
        report_lines.append(f"  • Медианный возраст: {np.median(ages):.1f} лет")
        report_lines.append(f"  • Минимальный возраст: {min(ages)} лет")
        report_lines.append(f"  • Максимальный возраст: {max(ages)} лет")
        report_lines.append("")

        self._add_age_groups_analysis(report_lines, ages)

    def _add_age_groups_analysis(self, report_lines, ages):
        """Добавление анализа возрастных групп"""
        age_groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46+': 0}
        for age in ages:
            if 18 <= age <= 25:
                age_groups['18-25'] += 1
            elif 26 <= age <= 35:
                age_groups['26-35'] += 1
            elif 36 <= age <= 45:
                age_groups['36-45'] += 1
            else:
                age_groups['46+'] += 1

        report_lines.append("  • Распределение по возрастным группам:")
        for group, count in age_groups.items():
            percentage = (count / len(ages)) * 100
            report_lines.append(f"    • {group}: {count} чел. ({percentage:.1f}%)")
        report_lines.append("")

    def _add_gender_analysis(self, report_lines):
        """Добавление гендерного анализа"""
        genders = [user['gender'] for user in st.session_state.active_users_data]
        gender_counts = pd.Series(genders).value_counts()

        report_lines.append("⚧ ГЕНДЕРНЫЙ АНАЛИЗ:")
        for gender, count in gender_counts.items():
            percentage = (count / len(genders)) * 100
            report_lines.append(f"  • {gender}: {count} чел. ({percentage:.1f}%)")
        report_lines.append("")

    def _add_geographic_analysis(self, report_lines):
        """Добавление географического анализа"""
        cities = [user['city'] for user in st.session_state.active_users_data]
        city_counts = pd.Series(cities).value_counts()

        report_lines.append("🗺️ ГЕОГРАФИЧЕСКИЙ АНАЛИЗ:")
        report_lines.append(f"  • Всего городов: {len(city_counts)}")
        report_lines.append("  • Топ-5 городов по активности:")

        for city, count in city_counts.head(5).items():
            percentage = (count / len(cities)) * 100
            report_lines.append(f"    • {city}: {count} чел. ({percentage:.1f}%)")
        report_lines.append("")

    def _add_surveys_demographics(self, report_lines):
        """Добавление демографических данных по опросам"""
        report_lines.append("📋 ДЕМОГРАФИЯ ПО ОПРОСАМ:")
        report_lines.append("")

        for survey in st.session_state.get('real_surveys', []):
            survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
            demographics = survey_data['demographics']

            report_lines.append(f"  • {survey.get('name', 'Без названия')}:")
            report_lines.append(f"    • Всего ответов: {survey_data['total_responses']}")

            if demographics['age']:
                total_age = sum(age * count for age, count in demographics['age'].items())
                total_count = sum(demographics['age'].values())
                avg_age = total_age / total_count if total_count > 0 else 0
                report_lines.append(f"    • Средний возраст ответивших: {avg_age:.1f} лет")

            if demographics['gender']:
                main_gender = max(demographics['gender'].items(), key=lambda x: x[1])[0]
                report_lines.append(f"    • Основная аудитория: {main_gender}")

            if demographics['city']:
                main_city = max(demographics['city'].items(), key=lambda x: x[1])[0]
                report_lines.append(f"    • Основной город: {main_city}")

            report_lines.append("")

    def _add_demographic_recommendations(self, report_lines):
        """Добавление демографических рекомендаций"""
        report_lines.append("🎯 ВЫВОДЫ И РЕКОМЕНДАЦИИ:")

        ages = [user['age'] for user in st.session_state.active_users_data]
        age_groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46+': 0}
        for age in ages:
            if 18 <= age <= 25:
                age_groups['18-25'] += 1
            elif 26 <= age <= 35:
                age_groups['26-35'] += 1
            elif 36 <= age <= 45:
                age_groups['36-45'] += 1
            else:
                age_groups['46+'] += 1

        report_lines.append("  1. Основная аудитория: ")
        if age_groups['26-35'] >= age_groups['18-25']:
            report_lines.append("     • Целевая группа 26-35 лет наиболее активна")
        else:
            report_lines.append("     • Целевая группа 18-25 лет наиболее активна")

        cities = [user['city'] for user in st.session_state.active_users_data]
        city_counts = pd.Series(cities).value_counts()
        top_city = city_counts.index[0] if len(city_counts) > 0 else "Не определен"

        report_lines.append("  2. Географическое распределение:")
        report_lines.append(f"     • Сфокусироваться на {top_city} и близлежащих регионах")

        report_lines.append("  3. Рекомендации по контенту:")
        report_lines.append("     • Адаптировать вопросы под основные возрастные группы")
        report_lines.append("     • Учитывать региональные особенности")
        report_lines.append("     • Разнообразить тематику для разных демографических групп")