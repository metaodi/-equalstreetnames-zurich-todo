#!/usr/bin/env python
# coding: utf-8

import streamlit as st

import os
import json
import time
from pprint import pprint

import requests
import folium
import geopandas
import pandas as pd
import xml.etree.ElementTree as ET
import osm2geojson
from streamlit_folium import folium_static
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


st.set_page_config(page_title="EqualStreetNames Zurich - TODO", layout="wide", menu_items=None)
st.title('EqualStreetNames Zurich - TODO')

def base_map(location=[47.38, 8.53], zoom=13):
    m = folium.Map(location=location, zoom_start=zoom, tiles=None)
    folium.raster_layers.WmsTileLayer(
        url='https://www.ogd.stadt-zuerich.ch/wms/geoportal/Basiskarte_Zuerich_Raster_Grau',
        layers='Basiskarte Zürich Raster Grau',
        name='Zürich - Basiskarte',
        fmt='image/png',
        overlay=False,
        control=False,
        autoZindex=False,
    ).add_to(m)
    return m

@st.cache(ttl=3600)
def load_data():
    #df = pd.read_csv("https://raw.githubusercontent.com/metaodi/equalstreetnames-zurich-todo/main/data.csv")
    df = pd.read_pickle("data.pkl")
    return df

def osm_link(r):
    return f"<a href='https://openstreetmap.org/{r['type']}/{r['id']}'>{r['type']}/{r['id']}</a>"

def wikidata_link(r):
    return f"<a href='https://www.wikidata.org/wiki/{r['wikidata']}'>{r['wikidata']}</a>"

def named_after_link(r):
    if not r['named_after']:
        return ''
    return f"<a href='https://www.wikidata.org/wiki/{r['named_after']}'>{r['named_after']}</a>"

filtered_df = load_data().copy()
filtered_df['osm_link'] = filtered_df.apply(osm_link, axis=1)
filtered_df['wikidata_link'] = filtered_df.apply(wikidata_link, axis=1)
filtered_df['named_after_link'] = filtered_df.apply(named_after_link, axis=1)

# Basiskarte
m = base_map()

# Strassennamenverzeichnis-Daten hinzufügen
folium.features.GeoJson(
    filtered_df.to_json(),
    style_function=lambda x: {'fillColor': '#09bd63', 'color': '#09bd63'},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name', 'erlaeutertung', 'wikidata'],
        aliases=['name:', 'Erläuterung:', "Wikidata:"],                      
    )
).add_to(m)

# display content
st.header(f"Streets with potential person")
folium_static(m)
st.write(filtered_df[['name', 'erlaeutertung', 'wikidata_link', 'named_after_link', 'osm_link']].to_html(escape=False), unsafe_allow_html=True)

st.markdown('&copy; 2022 Stefan Oderbolz | [Github Repository](https://github.com/metaodi/equalstreetnames-zurich-todo)')
