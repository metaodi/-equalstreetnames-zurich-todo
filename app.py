#!/usr/bin/env python
# coding: utf-8

import streamlit as st

import os
import json
import time
from pprint import pprint
import io
import zipfile

import requests
import folium
import geopandas
import pandas as pd
import xml.etree.ElementTree as ET
import osm2geojson
from streamlit_folium import folium_static
from ghapi.all import GhApi
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


@st.cache(ttl=900)
def load_data():
    # read data.pkl from GitHub Actions Artifacts
    github_token = os.environ['GITHUB_TOKEN']
    api = GhApi(owner='metaodi', repo='equalstreetnames-zurich-todo', token=github_token)
    artifacts = api.actions.list_artifacts_for_repo()['artifacts']
    download = api.actions.download_artifact(artifact_id=artifacts[0]['id'], archive_format="zip")

    with zipfile.ZipFile(io.BytesIO(download)) as zip_ref:
        zip_ref.extractall('.')

    df = pd.read_pickle("data.pkl")
    return df

def osm_link(r):
    return f"<a href='https://openstreetmap.org/{r['type']}/{r['id']}'>{r['type']}/{r['id']}</a>"

def wikidata_link(r, attr='wikidata'):
    if not r[attr]:
        return ''
    return f"<a href='https://www.wikidata.org/wiki/{r[attr]}'>{r[attr]}</a>"

filtered_df = load_data().copy()


filtered_df['osm_link'] = filtered_df.apply(osm_link, axis=1)
filtered_df['wikidata_link'] = filtered_df.apply(wikidata_link, axis=1)
filtered_df['named_after_link'] = filtered_df.apply(wikidata_link, args=('named_after'), axis=1)

# Basiskarte
m = base_map()

# Strassennamenverzeichnis-Daten hinzufügen
folium.features.GeoJson(
    filtered_df.to_json(),
    style_function=lambda x: {'fillColor': '#09bd63', 'color': '#09bd63'},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name', 'erlaeutertung', 'wikidata'],
        aliases=['name:', 'Erläuterung:', "Wikidata:"],
        permanent=True,
        sticky=False,
    )
).add_to(m)

# display content
st.header(f"Streets with potential person")
folium_static(m)

empty_name_ety = st.checkbox("Only display empty 'name:etymology:wikidata'", value=False)
empty_named_after = st.checkbox("Only display empty 'named_after'", value=False)
group_by_street = st.checkbox("Group by street", value=True)

if empty_named_after:
    filtered_df = filtered_df.drop(filtered_df[filtered_df['named_after'].notna()].index).reset_index(drop=True)

if group_by_street:
    filtered_df = filtered_df.groupby(['name', 'erlaeutertung', 'wikidata_link', 'named_after_link'], as_index=False).count()
    st.write(filtered_df[['name', 'erlaeutertung', 'wikidata_link', 'named_after_link']].to_html(escape=False), unsafe_allow_html=True)
else:
    st.write(filtered_df[['name', 'erlaeutertung', 'wikidata_link', 'named_after_link', 'osm_link']].to_html(escape=False), unsafe_allow_html=True)

st.markdown('&copy; 2022 Stefan Oderbolz | [Github Repository](https://github.com/metaodi/equalstreetnames-zurich-todo)')
