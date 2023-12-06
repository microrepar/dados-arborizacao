import datetime
import time

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from st_pages import add_page_title
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

from src.adapters import Controller
from src.external.app_pages.auth_manager.authentication import streamlit_auth


def on_click_get_location():
    st.session_state.flag_btn_centralizar = True
    st.session_state.flag_folium_map = not st.session_state.flag_folium_map
    st.session_state.pop('latitude')
    st.session_state.pop('longitude')


if 'latitude' not in st.session_state:
    st.session_state.latitude = None

if 'longitude' not in st.session_state:
    st.session_state.longitude = None

if 'flag_btn_centralizar' not in st.session_state:
    st.session_state.flag_btn_centralizar = False

if 'flag_folium_map' not in st.session_state:
    st.session_state.flag_folium_map = False


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(layout="wide")

add_page_title()

placeholder_messages = st.empty()

# ----- LOGIN MAIN ------
name, authentication_status, username, authenticator, credentials, user_dict = streamlit_auth(placeholder_messages)
st.session_state.username = st.session_state.username

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

    #############################################################
    ### ALL TREE PLACEHOLDER###
    #############################################################
    placeholder_messages = st.empty()
    placeholder_get_all_tree = st.empty()
    #############################################################

    #############################################################
    ### GET ALL TREE AND ###
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

    # placeholder_get_all_tree.write(entities)

    if 'error' not in messages and entities:
        
        placeholder_folium_map = st.empty()


        st.button('🎯Centralizar Mapa',
                  on_click=on_click_get_location)
        
        if st.session_state.flag_btn_centralizar:
            loc = get_geolocation()
            while True:
                try:
                    st.session_state.latitude = loc.get('coords', {}).get('latitude')
                    st.session_state.longitude = loc.get('coords', {}).get('longitude')                    
                    break
                except: 
                    time.sleep(.2)
            
        latitude = st.session_state.latitude
        longitude = st.session_state.longitude

        if latitude and longitude:
            st.session_state.flag_btn_centralizar = False
            st.session_state.latitude = None
            st.session_state.longitude = None            

            m = folium.Map(location=[latitude, longitude],  zoom_start=18)

            url = '.resources/regioes_plan.geojson'
            folium.GeoJson(url, name="regioes_plan").add_to(m)

            cluster = MarkerCluster()

            for arvore in entities: 

                tooltip = f"{arvore.nome_comum}"

                folium.Marker(
                    location=[arvore.latitude , arvore.longitude],
                    icon=folium.Icon(color = 'green', icon = 'fa-tree', prefix = 'fa'),
                    popup=folium.Popup(f'''
                                    <b>Ident</b>: {arvore.id}<br>
                                    <b>Nome Comum</b>: {arvore.nome_comum}<br>
                                    <b>Espécie</b>: {arvore.especie}<br>
                                    <b>Fitossanidade</b>: {arvore.fitossanidade}<br>
                                    ''',
                                    max_width=300,
                                    sticky=False),
                    tooltip=tooltip

                ).add_to(cluster)
            
            folium.CircleMarker(
                location=[latitude , longitude],
                radius=5,
                tooltip="Você está aqui.",
                color="#3186cc",
                # color="red",
                fill=True,
                fill_color="#3186cc",
            ).add_to(cluster)

            cluster.add_to(m)

            if st.session_state.flag_folium_map:
                with placeholder_folium_map:
                    out = st_folium(m, height=200, 
                                    use_container_width=True, 
                                    returned_objects=[],
                                    key='folium_map_1')
            else:    
                with placeholder_folium_map:
                    out = st_folium(m, height=200, 
                                    use_container_width=True, 
                                    returned_objects=[],
                                    key='folium_map_2')
        
        else:
            df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
            m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()],  zoom_start=11)

            url = '.resources/regioes_plan.geojson'
            folium.GeoJson(url, name="regioes_plan").add_to(m)
            
            cluster = MarkerCluster()

            for arvore in entities: 

                tooltip = f"{arvore.nome_comum}"

                folium.Marker(
                    location=[arvore.latitude , arvore.longitude],
                    icon=folium.Icon(color = 'green', icon = 'fa-tree', prefix = 'fa'),
                    popup=folium.Popup(f'''
                                    <b>Identificação</b>: {arvore.id}<br>
                                    <b>Nome Comum</b>: {arvore.nome_comum}<br>
                                    <b>Espécie</b>: {arvore.especie}<br>
                                    <b>Fitossanidade</b>: {arvore.fitossanidade}<br>
                                    ''',
                                    max_width=300,
                                    sticky=False),
                    tooltip=tooltip

                ).add_to(cluster)

            cluster.add_to(m)
        
            with placeholder_folium_map:
                out = st_folium(m, height=200, use_container_width=True, returned_objects=[])


        st.divider()
        st.markdown('### REGISTRO DE PODA')
        col, *_ = st.columns(2)
        tree_id = col.number_input('Identificação', placeholder='Identificação da árvore', step=1, format='%d', value=None)

        selected_tree = {e.id: e for e in entities}.get(tree_id)
        if tree_id is None:
            st.info('Selecione a árvore no mapa e insirá no campo identificação, '
                    'o mesmo número que foi informado do rótulo da seleção, para '
                    'abrir o formulário de registro de poda.', icon='ℹ️')
        elif selected_tree:
            poda_list = ['Poda de Formação', 'Poda de Limpeza', 'Poda de Redução', 'Poda de Rebaixamento', 'Poda de Desbaste', 'Poda de Emergência'] 
            with st.form('registrar_poda'):
                st.markdown('**Registrar Poda:**')
                col1, col2, col3 = st.columns(3)
                nome_especie = col1.text_input('**Espécie**',
                                            value=selected_tree.especie,
                                            disabled=True)
                nome_comum = col2.text_input('**Nome Comum**',
                                             value=selected_tree.nome_comum,
                                            disabled=True)        
                origem_especie = col3.text_input('**Origem**', 
                                            value=selected_tree.origem,
                                            disabled=True)
                col1, col2 = st.columns(2)
                localizacao = st.text_input('**Localização**', 
                                            value=selected_tree.localizacao, 
                                            disabled=True)        
                latitude = col1.text_input('**Latitude**', 
                                           value=selected_tree.latitude, 
                                           disabled=True)
                longitude = col2.text_input('**Longitude**', 
                                            value=selected_tree.longitude
                                            , disabled=True)
                st.selectbox('Tipo de poda:', poda_list, index=None,
                            placeholder='Escolha uma opção')
                col1, col2 = st.columns(2)
                data_poda = col1.date_input('Data da poda:', datetime.datetime.now().date(), format='DD/MM/YYYY')
                responsavel_poda = col2.text_input('Responsável pela poda:')
                submited = st.form_submit_button('Registrar')

            if submited:           

                #############################################################
                ### GET ALL TREE AND ###
                #############################################################
                controller = Controller()
                request    = {
                    'resource': '/pruning/registry'
                }
                resp       = controller(request=request)
                #############################################################
                entities = resp.get('entities')
                messages = resp.get('messages')    

                if 'error' in messages:
                    st.error('\n  - '.join(messages['error']), icon='🚨')
                if 'info' in messages:
                    st.info('\n  - '.join(messages['info']), icon='⚠️')
                if 'warning' in messages:
                    st.info('\n  - '.join(messages['warning']), icon='ℹ️')
                if 'success' in messages:
                    st.info('\n  - '.join(messages['success']), icon='✅')
                #############################################################
            
        else:
            st.error(f'Não há nenhuma árvore com o id={tree_id}.', icon='🚨')