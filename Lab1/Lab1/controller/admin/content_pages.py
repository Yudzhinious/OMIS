from controller.admin.storage import SurveyStorage
from controller.admin.user_management import UserManager
from controller.admin.admin_dashboard import AdminDashboard
from controller.admin.survey_management import SurveyManager
from controller.admin.survey_creation import SurveyCreator
from controller.admin.settings_and_history import SettingsManager, HistoryManager

survey_storage = SurveyStorage()
user_manager = UserManager()
admin_dashboard = AdminDashboard()
survey_manager = SurveyManager()
survey_creator = SurveyCreator()
settings_manager = SettingsManager()
history_manager = HistoryManager()

init_surveys_storage = survey_storage.init
add_real_survey = survey_storage.add
toggle_survey_publication = survey_storage.toggle_publication
delete_survey = survey_storage.delete

show_users_page_management = user_manager.show_page
create_demo_users = user_manager.create_demo
update_user_status = user_manager.update_status
update_user = user_manager.update
delete_user = user_manager.delete_user

show_admin_dashboard = admin_dashboard.show

show_admin_surveys_page = survey_manager.show_page
show_survey_details = survey_manager.show_details
show_survey_statistics = survey_manager.show_statistics
show_survey_preview_admin = survey_manager.show_preview

show_create_survey_page_content = survey_creator.show_page

show_settings_page_content = settings_manager.show_page
show_admin_history_page = history_manager.show_page
