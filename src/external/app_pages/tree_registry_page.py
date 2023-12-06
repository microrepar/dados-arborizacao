import time

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

from src.adapters import Controller

st.session_state.username = st.session_state.username

def tree_registry_page(username, user_dict):
    placeholder_messages = st.empty()

    #############################################################

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/tree/get_especies'}
    resp       = controller(request=request)
    #############################################################
    entities = resp.get('entities')
    objects  = resp.get('objects')
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

    especie_list = objects
    if especie_list:
        msg_placeholder = ('Selecione uma espécie ou adicione '
                           'uma marcando a caixa abaixo')
    else:
        msg_placeholder = ('Atenção! Não há espécies cadastradas, '
                           'adicione uma marcando a caixa abaixo')

    st.divider()
    col1, col2 = st.columns(2)
    user_name = col1.text_input('**Responsável pelo Registro**', 
                                value=getattr(user_dict.get(username), 'name', username),
                                disabled=True)
    st.divider()
    
    with st.container():
        st.markdown("### Cadastro de Árvores")
        placeholder_especie_field = st.empty()
        col1, *col = st.columns(3)
        if col1.checkbox('Incluir espécie', value=not bool(especie_list)):
            nome_especie = placeholder_especie_field.text_input('**Adicione a espécie**:red[*]', 
                                            placeholder='Adicione aqui a espécie')
        else:            
            nome_especie = placeholder_especie_field.selectbox('**Selecione a espécie**:red[*]', 
                                           especie_list, 
                                           index=None, 
                                           placeholder=msg_placeholder)
        
        nome_comum = st.text_input('**Nome Comum**:red[*]')
        col1, col2 = st.columns(2)
        origem_especie = col1.text_input('**Origem**:red[*]')
        fitossanidade = col2.selectbox('**Fitossanidade**:red[*]', 
                                           ['Excelente', 'Boa', 'Regular', 'Ruim', 'Moribunda', 'Morta'], 
                                           index=None, 
                                           placeholder='Selecione uma opção')
        col1, col2 = st.columns(2)
        altura = col1.number_input('**Altura**:red[*]', value=None, step=.2, format='%.2f')
        dap = col2.number_input('**DAP (Diâmetro à Altura do Peito)**:red[*]', value=None, step=.2, format='%.2f')
        
        st.divider()
        localizacao = st.text_input('**Localização**:red[*]')
        
        placeholder_cols_lat_long = st.empty()

        loc = {}
        lat_ = long_ = None
        col1, _ = st.columns(2)
        geolocation = col1.checkbox("Marcar geolocalização")
        if geolocation:
            loc = get_geolocation()
            while True:
                try:
                    lat_ = loc.get('coords', {}).get('latitude')
                    long_ = loc.get('coords', {}).get('longitude')
                    break
                except:
                    time.sleep(.2)

        col1, col2 = placeholder_cols_lat_long.columns(2)
        latitude = col1.text_input('**Latitude**', value=lat_, disabled=True)
        longitude = col2.text_input('**Longitude**', value=long_, disabled=True)

        if geolocation:
            if entities:
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

                tooltip = f"Nova árvore: {nome_comum}"
                folium.Marker(
                    location=[latitude , longitude],
                    popup=tooltip,
                    tooltip=tooltip,
                    icon=folium.Icon(color = 'blue', icon = 'fa-tree', prefix = 'fa')
                ).add_to(cluster)

                cluster.add_to(m)
                st_folium(m, height=300, use_container_width=True , returned_objects=[])
            else:
                m = folium.Map(location=[latitude, longitude],  zoom_start=25)
                
                url = '.resources/regioes_plan.geojson'
                folium.GeoJson(url, name="regioes_plan").add_to(m)

                tooltip = f"Árvore {nome_comum}"
                folium.Marker(
                    location=[latitude , longitude],
                    popup=tooltip,
                    tooltip=tooltip,
                    icon=folium.Icon(color = 'blue', icon = 'fa-tree', prefix = 'fa')
                ).add_to(m)
                st_folium(m, height=300, use_container_width=True , returned_objects=[])
        
        st.divider()
        
        observacao = st.text_area('**Observação:**')
        
        # Every form must have a submit button.
        submitted = st.button("💾 SALVAR", type="primary", use_container_width=True)


    
    if submitted:
        #############################################################
        ### REGISTRY TREE ###
        #############################################################
        # st.markdown('## REGISTRY TREE')

        controller = Controller()
        request = {
            'resource': '/tree/registry',                        
            'tree_created_by'    : user_name,
            'tree_especie'       : nome_especie,
            'tree_nome_comum'    : nome_comum,
            'tree_origem'        : origem_especie,
            'tree_altura'        : altura,
            'tree_dap'           : dap,
            'tree_fitossanidade' : fitossanidade,
            'tree_localizacao'   : localizacao,
            'tree_latitude'      : latitude,
            'tree_longitude'     : longitude,
            'tree_obs'           : observacao,
        }

        resp = controller(request=request)
        messages = resp.get('messages')
        entities = resp.get('entities')

        if 'error' in messages:
            placeholder_messages.error('\n  - '.join(messages['error']), icon='🚨')
            st.error('\n  - '.join(messages['error']), icon='🚨')
        if 'info' in messages:
            placeholder_messages.info('\n  - '.join(messages['info']), icon='⚠️')
            st.info('\n  - '.join(messages['info']), icon='⚠️')
        if 'warning' in messages:
            placeholder_messages.info('\n  - '.join(messages['warning']), icon='ℹ️')
            st.info('\n  - '.join(messages['warning']), icon='ℹ️')
        if 'success' in messages:
            placeholder_messages.info('\n  - '.join(messages['success']), icon='✅')
            st.info('\n  - '.join(messages['success']), icon='✅')
        #############################################################
            