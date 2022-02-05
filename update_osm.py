#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
from pprint import pprint

import requests
import geopandas
import pandas as pd
import xml.etree.ElementTree as ET
import osm2geojson
import osmapi
from IPython.display import display
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
user = os.getenv('OSM_USER')
pw = os.getenv('OSM_PASS')


filtered_df = pd.read_pickle('data.pkl')
display(filtered_df[['name', 'wikidata', 'named_after', 'type', 'id']])

#api = osmapi.OsmApi(api="https://api.openstreetmap.org", username=user, password=pw)

def update_osm_way(row):
    #changeset_id = api.ChangesetCreate({u"comment": u"Add name:etymology:wikidata tag"})
    print(row['wikidata'])
    if not row.get('wikidata'):
        return
    way = api.WayGet(row['wikidata'])
    new_way = way.copy()
    new_way['tag']['name:etymology:wikidata'] = row['named_after']
    print(new_way)
    print("Has changed?", way != new_way) 
    time.sleep(2)
    #api.WayUpdate(way)
    #api.ChangesetClose()

filtered_df.apply(update_osm_way)
