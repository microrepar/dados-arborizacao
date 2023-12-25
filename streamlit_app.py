"""Application's entry point
Project name: Dados Arborizacao
Author: Codata
Description: Formulário para coleta de dados de arborização.
"""
import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages

from src.external.app_pages.auth_manager.authentication import streamlit_auth
from src.external.app_pages.tree_registry_page import tree_registry_page

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(layout="wide")


placeholder_msg = st.empty()

# ------------------------- Authentication -------------------------
name, authentication_status, username, authenticator, credentials, user_dict = streamlit_auth(placeholder_msg)

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
        
    add_page_title(layout="wide")
    tree_registry_page(username, user_dict)

