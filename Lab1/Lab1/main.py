import streamlit as st
import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from view.config import init_app, init_session_state, get_role_info
from view.auth.auth_pages import show_auth_page
from view.sidebar import show_sidebar
from model.core_handlers import show_content

st.set_page_config(
    page_title="SurveyPro - Платформа интерактивных опросов",
    page_icon="📊",
    layout="wide"
)

services, views = init_app()
init_session_state()
role_text, user_initial = get_role_info()

if not st.session_state.is_authenticated:
    show_auth_page(services, views)
else:
    st.markdown(f"""
    <div class="top-banner">
        <div class="top-banner-content">
            <span class="top-banner-icon">📊</span>
            <span class="top-banner-title">SurveyPro {role_text}</span>
            <div class="user-circle">{user_initial}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: block !important;
        }

        .stApp {
            background: white !important;
        }

        .top-banner {
            z-index: 999999 !important;
        }

        .main .block-container {
            margin-left: 250px !important;
            max-width: calc(100% - 250px) !important;
        }

        button[title="Close sidebar"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            transform: translateX(0) !important;
            transition: none !important;
        }

        [data-testid="stSidebar"]:hover {
            transform: translateX(0) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    selected_menu = show_sidebar(services, views, role_text, user_initial)
    show_content(selected_menu, services, views)