#!/usr/bin/env python
# coding: utf-8

import streamlit as st

import os
import json
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

@st.cache
def get_layers_from_wfs(wfs_base_url):
    r = requests.get(wfs_base_url, params={
        'service': 'WFS',
        'version': '1.0.0',
        'request': 'GetCapabilities'
    })
    # XML parsen und die Layer-Informationen extrahieren
    root = ET.fromstring(r.content)
    namespaces = {
        'wfs': 'http://www.opengis.net/wfs'
    }
    layers = {}
    for feature_type in root.findall('wfs:FeatureTypeList/wfs:FeatureType', namespaces):
        layers[feature_type.find('wfs:Name', namespaces).text] = {
            'srs': feature_type.find('wfs:SRS', namespaces).text,
        }
    return layers

@st.cache
def overpass_query(q, endpoint='http://overpass.osm.ch/api/interpreter'):
    r = requests.get(endpoint, params={'data': q})
    r.raise_for_status()
    osm_gj = osm2geojson.json2geojson(r.json())
    for f in osm_gj['features']:
        props = {}
        for p, v in f['properties'].items():
            if isinstance(v, dict):
                for ip, iv in v.items():
                    props[ip] = iv
            else:
                props[p] = v
        f['properties'] = props
    return osm_gj

@st.cache
def wikidata_item(item, endpoint='https://www.wikidata.org/w/api.php'):
    res = requests.get(endpoint, params={
        'action': 'wbgetentities',
        'ids': item,
        'format': 'json',
    })
    return res.json()['entities'][item]

@st.cache
def load_data(wfs_url, layer):
    r = requests.get(wfs_url, params={
        'service': 'WFS',
        'version': '1.0.0',
        'request': 'GetFeature',
        'typename': str_verz_layer,
        'outputFormat': 'GeoJSON'
    })
    str_verz_geo = r.json()
    return str_verz_geo

def osm_link(r):
    return f"<a href='https://openstreetmap.org/{r['type']}/{r['id']}'>{r['type']}/{r['id']}</a>"

def wikidata_link(r):
    return f"<a href='https://www.wikidata.org/wiki/{r['wikidata']}'>{r['wikidata']}</a>"

def named_after_link(r):
    wd_item = wikidata_item(r['wikidata'])
    print(wd_item)
    return f"<a href='https://www.wikidata.org/wiki/{r['wikidata']}'>{r['wikidata']}</a>"

lv95 = 'EPSG:2056'
wgs84 = 'EPSG:4326'
str_verz_layer = 'sv_str_verz'
wfs_url = 'https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Strassennamenverzeichnis' 
layers = get_layers_from_wfs(wfs_url) # GetCapabilitites

# load data from WFS
str_verz_geo = load_data(wfs_url, str_verz_layer)

str_verz = [{'strassenname': f['properties']['str_name'], 'erlaeutertung': f['properties']['snb_erlaeuterung']} for f in str_verz_geo['features']]
df_str = pd.DataFrame.from_dict(str_verz)

# load data from OSM via Overpass
streets_query = """
[out:json][timeout:300];
( area["admin_level"=""]["wikidata"="Q72"]; )->.a;
(
    way["highway"]["name"]["highway"!="bus_stop"]["highway"!="elevator"]["highway"!="platform"](area.a);
    way["place"="square"]["name"](area.a);
);
out body;
>;
out skel qt;
"""
osm_result = overpass_query(streets_query)
osm_df = geopandas.GeoDataFrame.from_features(osm_result, crs=wgs84)

# Join OSM data with Strassenverzeichnis
merged_df = osm_df.merge(df_str, how="inner", left_on='name', right_on='strassenname')

# alle entfernen, die bereits name:etymology:wikidata Einträge haben
merged_df = merged_df.drop(merged_df[merged_df['name:etymology:wikidata'].notna()].index)

# filter auf alle die Personen sein könnten: Einträge in der Form «Vorname Name (Jahr-Jahr)»
filtered_df = merged_df[merged_df['erlaeutertung'].str.match(r'^[\s\w]+\(\d{4}-\d{4}\)')==True].reset_index(drop=True)

filtered_df['osm_link'] = filtered_df.apply(osm_link, axis=1)
filtered_df['wikidata_link'] = filtered_df.apply(wikidata_link, axis=1)

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
#st.table(filtered_df[['name', 'erlaeutertung', 'osm_link']])
st.write(filtered_df[['name', 'erlaeutertung', 'wikidata_link', 'osm_link']].to_html(escape=False), unsafe_allow_html=True)
