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


filtered_df = pd.read_pickle('data.pkl')
api = osmapi.OsmApi(api="https://api.openstreetmap.org", username=user, password=pw)
changeset_id = api.ChangesetCreate({u"comment": u"Add name:etymology:wikidata tag"})

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
    s = input("Press Enter to continue, 'n' to create a new changeset or 'q' to quit: ")
    if s.strip().lower() == 'n':
        api.ChangesetClose()
        changeset_id = api.ChangesetCreate({u"comment": u"Add name:etymology:wikidata tag"})
    if s.strip().lower() == 'q':
        api.ChangesetClose()
        sys.exit(1)
    if not way['tag'] == new_way['tag']:
        changed = api.WayUpdate(new_way)
        pprint(changed['tag'])
        time.sleep(2)


try:
    filtered_df.apply(update_osm_way, axis=1)
finally:
    api.ChangesetClose()
