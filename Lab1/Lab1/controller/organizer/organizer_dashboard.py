import streamlit as st
from controller.organizer.organizer_storage import OrganizerStorage


class DashboardRenderer:
    def __init__(self, storage: OrganizerStorage):
        self.storage = storage

    def show_organizer_dashboard(self):
        """Отображение дашборда организатора"""
        self.storage.init_data_storage()
        self._render_dashboard_header()
        self._render_dashboard_metrics()
        self._render_dashboard_content()

    def _render_dashboard_header(self):
        """Рендеринг заголовка дашборда"""
        html = """
        <div style="display: flex; justify-content: space-between; 
                    align-items: center; margin-bottom: 30px;">
            <h1 style="margin: 0;">Панель управления</h1>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _render_dashboard_metrics(self):
        """Рендеринг метрик дашборда"""
        total_surveys, total_responses, avg_completion, avg_time = self._calculate_dashboard_metrics()

        col1, col2, col3, col4 = st.columns(4)
        metrics_data = [
            (total_surveys, "Созданных опросов"),
            (total_responses, "Всего ответов"),
            (f"{avg_completion:.0f}%", "Средний процент завершения"),
            (f"{avg_time / 60:.1f}", "Среднее время (мин)")
        ]

        for i, (value, label) in enumerate(metrics_data):
            with [col1, col2, col3, col4][i]:
                st.markdown(self._create_metric_card(value, label), unsafe_allow_html=True)

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

    def _create_metric_card(self, value, label):
        """Создание HTML для карточки метрики"""
        return f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="font-size: 32px; font-weight: bold; color: #667eea;">{value}</div>
            <div style="font-size: 14px; color: #7f8c8d;">{label}</div>
        </div>
        """

    def _render_dashboard_content(self):
        """Рендеринг содержимого дашборда"""
        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_center, col_right = st.columns([3, 3, 1])

        with col_left:
            self._render_recent_surveys()

        with col_right:
            self._render_create_survey_button()

        with col_center:
            self._render_recent_reports()

    def _render_recent_surveys(self):
        """Рендеринг последних опросов"""
        st.markdown("### Последние опросы")

        real_surveys = st.session_state.get('real_surveys', [])[-2:]
        for survey in real_surveys:
            self._render_survey_card(survey)

    def _render_survey_card(self, survey):
        """Рендеринг карточки опроса"""
        survey_data = self.storage.generate_real_survey_data(survey.get('id', ''))
        status = survey.get('status', 'Черновик')
        status_color = self._get_status_color(status)

        html = f"""
        <div style="background: white; border-radius: 10px; padding: 20px; 
                    margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    border-left: 4px solid {status_color};">
            <div style="display: flex; justify-content: space-between; 
                        align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <h4 style="margin: 0 0 5px 0; color: #2c3e50;">
                        {survey.get('name', 'Без названия')}
                    </h4>
                    <p style="margin: 0; color: #7f8c8d; font-size: 14px;">
                        {survey.get('created_date', 'Неизвестно')}
                    </p>
                </div>
                <div style="background: {status_color}; color: white; 
                            padding: 5px 12px; border-radius: 20px; 
                            font-size: 12px; font-weight: bold;">
                    {status}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; 
                        color: #7f8c8d; font-size: 13px;">
                <div>📊 {survey_data['total_responses']} ответов</div>
                <div>📝 {len(survey.get('questions', []))} вопросов</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def _get_status_color(self, status):
        """Получение цвета статуса"""
        if status in ['Активный', 'Опубликован']:
            return "#27ae60"
        elif status == 'Завершен':
            return "#667eea"
        else:
            return "#95a5a6"

    def _render_create_survey_button(self):
        """Рендеринг кнопки создания опроса"""
        if st.button("+ Создать опрос", use_container_width=True):
            st.session_state.selected_menu = "📝 Создать опрос"
            st.rerun()

    def _render_recent_reports(self):
        """Рендеринг последних отчетов"""
        st.markdown("")
        st.markdown("### 📈 Последние отчеты")

        if not st.session_state.reports:
            st.info("Отчеты еще не созданы")
            return

        recent_reports = st.session_state.reports[-3:]
        for report in recent_reports:
            self._render_report_card(report)

    def _render_report_card(self, report):
        """Рендеринг карточки отчета"""
        html = f"""
        <div style="background: white; border-radius: 8px; padding: 15px; 
                    margin-bottom: 10px; box-shadow: 0 1px 5px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{report['name']}</strong><br>
                    <span style="font-size: 12px; color: #7f8c8d;">
                        Создан: {report['created_date']}
                    </span>
                </div>
                <span style="font-size: 12px; background: #e8f4fc; 
                            padding: 3px 8px; border-radius: 12px;">
                    {report['type']}
                </span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)