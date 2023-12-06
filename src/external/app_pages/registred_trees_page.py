import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from st_pages import add_page_title
from streamlit_folium import st_folium
from pathlib import Path
from src.adapters import Controller
from src.external.app_pages.auth_manager.authentication import streamlit_auth


HERE = Path(__name__).parent

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(layout="wide")

add_page_title()

placeholder_messages = st.empty()

# ----- LOGIN MAIN ------
name, authentication_status, username, authenticator, credentials, user_dict = streamlit_auth(placeholder_messages)

if 'btn_signup_page' not in st.session_state:
    if username == 'admin':
        st.session_state.btn_signup_page = True
    else:
        st.session_state.btn_signup_page = False

if 'btn_reset_password_page' not in st.session_state:
    if username == 'admin':
        st.session_state.btn_reset_password_page = False
    else:
        st.session_state.btn_reset_password_page = True

# Check login
if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:    
    # ---- LOGOUT SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    st.sidebar.divider()
    
    #############################################################
    ### ALL USERS PLACEHOLDER###
    #############################################################
    placeholder_messages = st.empty()
    placeholder_get_all_tree = st.empty()
    #############################################################

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/tree'}
    resp       = controller(request=request)
    #############################################################
    entities = resp.get('entities')
    messages = resp.get('messages')    

    if 'error' in messages:
        placeholder_messages.error('\n  - '.join(messages['error']), icon='🚨')
    if 'info' in messages:
        placeholder_messages.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placeholder_messages.info('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placeholder_messages.info('\n  - '.join(messages['success']), icon='✅')
    #############################################################

    # placeholder_get_all_tree.write(resp)

    if 'error' not in messages and entities:

        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)

        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()],  zoom_start=10)

        url = '.resources/regioes_plan.geojson'
        folium.GeoJson(url, name="regioes_plan").add_to(m)

        cluster = MarkerCluster()

        for arvore in entities: 

            tooltip = f"{arvore.nome_comum}"

            folium.Marker(
                location=[arvore.latitude , arvore.longitude],
                icon=folium.Icon(color = 'green', icon = 'fa-tree', prefix = 'fa'),
                popup=folium.Popup(f'''
                                   <b>Id</b>: {arvore.id}<br>
                                   <b>Nome Comum</b>: {arvore.nome_comum}<br>
                                   <b>Espécie</b>: {arvore.especie}<br>
                                   <b>Fitossanidade</b>: {arvore.fitossanidade}<br>
                                   ''',
                                   max_width=300,
                                   sticky=False),
                tooltip=tooltip

            ).add_to(cluster)

        cluster.add_to(m)

        out = st_folium(m, height=400, use_container_width=True , return_on_hover=False)

        if out["last_object_clicked_popup"]:
            value_popup = out["last_object_clicked_popup"]            
            tree_id = int(value_popup.split('\n')[0].split(':')[-1])
            st.markdown(f'### Detalhes da Árvore Selecionada | id: {tree_id}')

            selected_tree = {e.id: e for e in entities}.get(tree_id)
            
            col1, col2 = st.columns(2)
            nome_especie = col1.text_input('**Espécie**',
                                        value=selected_tree.especie,
                                        disabled=True)
            nome_comum = col2.text_input('**Nome Comum**',
                                        value=selected_tree.nome_comum,
                                        disabled=True)        
            col1, col2, col3 = st.columns(3)
            origem_especie = col1.text_input('**Origem**', 
                                        value=selected_tree.origem,
                                        disabled=True)
            fitossanidade = col2.text_input('**Fitossanidade**', 
                                        value=selected_tree.fitossanidade,
                                        disabled=True)
            created_by = col3.text_input('**Registrado por**', 
                                        value=selected_tree.created_by,
                                        disabled=True)
            localizacao = st.text_input('**Localização**', 
                                        value=selected_tree.localizacao, 
                                        disabled=True)        
            col1, col2 = st.columns(2)
            latitude = col1.text_input('**Latitude**', 
                                    value=selected_tree.latitude, 
                                    disabled=True)
            longitude = col2.text_input('**Longitude**', 
                                        value=selected_tree.longitude
                                        , disabled=True)
            observacao = st.text_area('**Observação:**', 
                                        value=selected_tree.obs
                                        , disabled=True)
        
        else:
            st.info('Selecione uma árvore no mapa para ver as sua informações detalhadas', icon='ℹ️')