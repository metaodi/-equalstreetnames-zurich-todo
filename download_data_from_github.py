#!/usr/bin/env python
# coding: utf-8

import os
import io
import zipfile
import pandas as pd

from ghapi.all import GhApi
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# read data.pkl from GitHub Actions Artifacts
github_token = os.environ['GITHUB_TOKEN']
api = GhApi(owner='metaodi', repo='equalstreetnames-zurich-todo', token=github_token)
artifacts = api.actions.list_artifacts_for_repo()['artifacts']
download = api.actions.download_artifact(artifact_id=artifacts[0]['id'], archive_format="zip")

with zipfile.ZipFile(io.BytesIO(download)) as zip_ref:
    zip_ref.extractall('.')

df = pd.read_pickle("data.pkl")
print(df[['name', 'wikidata', 'id', 'type']])

