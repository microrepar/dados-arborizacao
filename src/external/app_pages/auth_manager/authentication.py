"""Authentication
"""
import warnings
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from yaml.loader import SafeLoader
from st_pages import Page, Section, add_page_title, show_pages
from src.adapters import Controller

warnings.filterwarnings('ignore', category=FutureWarning)


def streamlit_auth(placeholder_msg):
    
    config_file = Path(__file__).parent / 'config.yaml'
    with config_file.open('rb') as file:
        config = yaml.load(file, Loader=SafeLoader)

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user'}
    resp       = controller(request=request)
    #############################################################
    messages = resp['messages']
    entities = resp['entities']
    #############################################################

    credentials = {'usernames': {}}
    user_dict = {}
    if 'error' not in messages:
        for user in entities:
            credentials['usernames'].setdefault(user.username, {})
            credentials['usernames'][user.username]['name'] = user.name
            credentials['usernames'][user.username]['email'] = user.email
            credentials['usernames'][user.username]['password'] = user.password
            user_dict[user.username] = user
    else:
        placeholder_msg.warning('\n\n'.join(messages['error']))
    
    
    config['credentials'] = credentials
    st.session_state.credentials = credentials

    authenticator = stauth.Authenticate(
        config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
        config['cookie']['name'],           # cookie:           str
        config['cookie']['key'],            # cookie:           str
        config['cookie']['expiry_days'],    # cookie:           str
        config['preauthorized'],            # preauthorized:    List[str]
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
       show_pages(
            [   
                Page("streamlit_app.py", "REGISTRO DE ÁRVORE", "🌳"),
                Page("src/external/app_pages/registred_trees_page.py", "Árvores Registradas", "🌳"),
                Page("src/external/app_pages/pruning_registry_page.py", "Registro de Poda", "✂️"),
                Page("src/external/app_pages/auth_manager/auth_manager_page.py", "Authentication Manager", "🔑"),
            ]
        )

    return name, authentication_status, username, authenticator, credentials, user_dict