import json

from pathlib import Path
import branca
import folium
import requests
import streamlit as st
from streamlit_folium import st_folium



def get_mapa(latitude, longetude, zoom_start=10):

    m = folium.Map(location=[latitude, longetude],  zoom_start=zoom_start)
    folium.CircleMarker(
        location=[latitude , longetude],
        radius=5,
        popup="CENTRO MOGI DAS CRUZES",
        # color="#3186cc",
        color="red",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)

    st_data = st_folium(m, use_container_width=True)
