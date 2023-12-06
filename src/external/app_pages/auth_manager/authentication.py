"""Authentication
"""
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from yaml.loader import SafeLoader

from src.adapters import Controller


def streamlit_auth(placeholder_msg):
    
    if 'user_dict' not in st.session_state:
        st.session_state.user_dict = {}

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
    
    st.session_state.user_dict = user_dict

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

    return name, authentication_status, username, authenticator, credentials, user_dict