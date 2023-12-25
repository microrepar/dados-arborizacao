import json
import math
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from scipy.interpolate import interp1d
from st_pages import add_page_title
from streamlit_folium import st_folium

from src.adapters import Controller
from src.external.app_pages.auth_manager.authentication import streamlit_auth


def get_zoom_max_by_geometry_height(geometry_height):

    alturas_conhecidas = [
       0.07800771139449836, 0.0668139, 0.046270852250899, 8.67e-05, 
       0.0107444, 0.015478, 0.004357956833899, 0.003926012918501698,
       0.07966,
    ]
    zooms_conhecidos = [
        11, 12, 12, 14,
        14, 14, 16, 16,
        11,
    ]

    # Função de interpolação linear
    interp_func = interp1d(alturas_conhecidas, zooms_conhecidos, kind='linear', fill_value='extrapolate')

    # Exemplos de alturas para estimar o zoom_start
    # Novo valor de altura para estimar o zoom_start
    zoom_start_estimado = int(interp_func(geometry_height))

    return zoom_start_estimado


def on_click_get_location(*args):
    st.session_state.flag_folium_map = not st.session_state.flag_folium_map
    if len(args) == 2:
        st.session_state.flag_btn_centralizar = False
        st.session_state.latitude = args[0]
        st.session_state.longitude = args[1]
    else:
        st.session_state.flag_btn_centralizar = True
        st.session_state.pop('latitude')
        st.session_state.pop('longitude')
        st.session_state.selected_tree = None
        
if 'flag_btn_centralizar' not in st.session_state:
    st.session_state.flag_btn_centralizar = False    

if 'latitude' not in st.session_state:
    st.session_state.latitude = None

if 'longitude' not in st.session_state:
    st.session_state.longitude = None

if 'flag_folium_map' not in st.session_state:
    st.session_state.flag_folium_map = False

if 'selected_tree' not in st.session_state:
    st.session_state.selected_tree = None

HERE = Path(__name__).parent

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(layout="wide")

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
    st.sidebar.divider()

    add_page_title(layout='wide')
    
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

        df_bairros = pd.read_parquet('.resources/abairramento.parquet')
        df_bairros = df_bairros.set_index('nome')
        selected_bairro = st.selectbox('Selecione o bairro', df_bairros.index, index=None)


        # Função para estilizar o GeoJSON
        def style_function(feature):            
            # Verificar se o bairro atual é o bairro selecionado
            if feature['properties']['NOME'] == selected_bairro:
                return {
                    'fillColor': 'orange',  # Cor quando selecionado
                    'color': 'blue',
                    'weight': 4,
                    'fillOpacity': 0.3
                }
            else:
                return {
                    'opacity': 0.4,
                    'fillOpacity': 0.2
                }
        

        tooltip = folium.GeoJsonTooltip(
            fields=["DISTRITO", "NOME"],
            aliases=["Distrito: ", "Bairro: "],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 3px solid;
                border-color: black;
                border-radius: 4px;
                box-shadow: 5px;                
            """,
            max_width=600,
        )

        latitude = st.session_state.latitude
        longitude = st.session_state.longitude

        if latitude and longitude:            

            m = folium.Map(location=[latitude, longitude],  zoom_start=18)

            url = '.resources/abairramento.geojson'
            folium.GeoJson(url, name="abairramento", tooltip=tooltip).add_to(m)

            cluster = MarkerCluster()

            for arvore in entities: 

                tooltip = f"{arvore.nome_comum}"

                if st.session_state.selected_tree and st.session_state.selected_tree.id != arvore.id:
                    flag_icon_color = True
                elif st.session_state.selected_tree is None:
                    flag_icon_color = True
                else:
                    flag_icon_color = False

                folium.Marker(
                    location=[arvore.latitude , arvore.longitude],                    
                    icon=folium.Icon(
                        color='green' if  flag_icon_color else 'orange', 
                        icon='fa-tree', 
                        prefix='fa'),
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

            if st.session_state.flag_folium_map:
                out = st_folium(m, height=250, use_container_width=True , return_on_hover=False, key='folium_map_key_1', )
            else:
                out = st_folium(m, height=250, use_container_width=True , return_on_hover=False, key='folium_map_key_2')
        
        else:
            df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)

            if selected_bairro:
                latitude_media = df_bairros.loc[selected_bairro, 'latitude_media']
                longitude_media = df_bairros.loc[selected_bairro, 'longitude_media']
                # geometry_width = df_bairros.loc[selected_bairro, 'geometry_width']
                geometry_height = df_bairros.loc[selected_bairro, 'geometry_height']

                zoom_start = get_zoom_max_by_geometry_height(geometry_height)

                # print('>>>>>>geometry>>>>>>>>>', abs(geometry_height))
                # print('>>>>>>zoom_start>>>>>>>>>', zoom_start)

                m = folium.Map(location=[latitude_media, longitude_media], zoom_start=zoom_start)

                with open('.resources/abairramento.geojson') as f:
                    geojson_data = json.load(f)
                folium.GeoJson(geojson_data, name="abairramento", tooltip=tooltip, style_function=style_function).add_to(m)

            else:
                m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()],  zoom_start=9)

                url = '.resources/abairramento.geojson'
                folium.GeoJson(url, name="abairramento", tooltip=tooltip).add_to(m)

            cluster = MarkerCluster()

            for arvore in entities: 

                tooltip = f"{arvore.nome_comum}"

                if st.session_state.selected_tree and st.session_state.selected_tree.id != arvore.id:
                    flag_icon_color = True
                elif st.session_state.selected_tree is None:
                    flag_icon_color = True
                else:
                    flag_icon_color = False

                folium.Marker(
                    location=[arvore.latitude , arvore.longitude],
                    icon=folium.Icon(
                        color='green' if flag_icon_color else 'orange', 
                        icon='fa-tree',
                        prefix='fa'),
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
            if st.session_state.flag_folium_map:
                out = st_folium(m, height=250, use_container_width=True , return_on_hover=False, key='folium_map_key_1')
            else:
                out = st_folium(m, height=250, use_container_width=True , return_on_hover=False, key='folium_map_key_2')
        
        placeholder_btn_ctrl_mapa = st.empty()

        if out["last_object_clicked_popup"] \
                or st.session_state.selected_tree:
            value_popup = out["last_object_clicked_popup"]            

            try:
                tree_id = int(value_popup.split('\n')[0].split(':')[-1])
            except:
                tree_id = None

            selected_tree = {e.id: e for e in entities}.get(tree_id) or st.session_state.selected_tree                
            st.session_state.selected_tree = selected_tree        
        
            st.markdown(f'### Árvore Selecionada - id: {selected_tree.id}')
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
            
            with placeholder_btn_ctrl_mapa:

                if st.session_state.flag_btn_centralizar:
                    col1, col2 = st.columns(2)
                    col2.button('🗑️ Limpar',
                        on_click=on_click_get_location,
                        use_container_width=True)
                    col1.button('🎯Centralizar Mapa',
                            args=[latitude, longitude],
                            on_click=on_click_get_location,
                            use_container_width=True)
                else:
                    col1, col2 = st.columns(2)
                    col2.button('🗑️ Limpar',
                        on_click=on_click_get_location,
                        use_container_width=True)
                    col1.button('🎯Centralizar Mapa',
                            args=[latitude, longitude],
                            on_click=on_click_get_location,
                            use_container_width=True)
       
        else:
            st.info('Selecione uma árvore no mapa para ver as sua informações detalhadas', icon='ℹ️')