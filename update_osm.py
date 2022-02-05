#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import copy
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

api = osmapi.OsmApi(api="https://api.openstreetmap.org", username=user, password=pw)

def update_osm_way(row):
    print(row)
    if not row.get('named_after'):
        return
    way = api.WayGet(row['id'])
    new_way = copy.deepcopy(way)
    new_way['tag']['name:etymology:wikidata'] = row['named_after']
    pprint(way['tag'])
    pprint(new_way['tag'])
    print("Same? ", way['tag'] == new_way['tag'])
    input("Press Enter to continue")
    if not way['tag'] == new_way['tag']:
        changeset_id = api.ChangesetCreate({u"comment": u"Add name:etymology:wikidata tag"})
        changed = api.WayUpdate(new_way)
        pprint(changed['tag'])
        api.ChangesetClose()
        time.sleep(2)

filtered_df.apply(update_osm_way, axis=1)
