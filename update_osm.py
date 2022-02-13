#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import copy
from pprint import pprint

import pandas as pd
import osmapi
from IPython.display import display

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
user = os.getenv('OSM_USER')
pw = os.getenv('OSM_PASS')

api = osmapi.OsmApi(api="https://api.openstreetmap.org", username=user, password=pw)

def update_osm_way(row):
    if not row.get('named_after'):
        return
    print(row[['type', 'id', 'strassenname', 'named_after']])
    way = api.WayGet(row['id'])
    new_way = copy.deepcopy(way)
    new_way['tag']['name:etymology:wikidata'] = row['named_after']
    pprint(way['tag'])
    pprint(new_way['tag'])
    print("Same? ", way['tag'] == new_way['tag'])
    s = input("Press Enter to continue or 'q' to quit: ")
    if s.strip().lower() == 'q':
        sys.exit(0)
    if not way['tag'] == new_way['tag']:
        with api.Changeset({"comment": f"Add name:etymology:wikidata tag to {row['name']}"}) as changeset_id:
            changed = api.WayUpdate(new_way)
            print(f"Changeset: {changeset_id}")
            pprint(changed['tag'])
        time.sleep(2)


filtered_df = pd.read_pickle('data.pkl')
filtered_df = filtered_df.drop(filtered_df[filtered_df['name:etymology:wikidata'].notna()].index).reset_index(drop=True)
filtered_df = filtered_df.drop(filtered_df[filtered_df['named_after'].isna()].index).reset_index(drop=True)

filtered_df.apply(update_osm_way, axis=1)
