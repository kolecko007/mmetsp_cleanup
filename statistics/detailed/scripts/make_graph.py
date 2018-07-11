#!/usr/bin/env python3

import os
import networkx as nx
from statistics.detailed.scripts.lib.metadata import *


def get_key(left, right):
    return ','.join([left, right])


import pandas as pd

MIN_CNT = 1

MIN_DATE_INNER_PCT = 0
MIN_PI_INNER_PCT = 0

RAW_PATH = 'statistics/detailed/data'
OUTPUT_PATH = 'statistics/detailed/output'

graph = nx.MultiDiGraph()
MetadataCollection.load(os.path.join(RAW_PATH, 'metadata.json'))

datasets = pd.read_csv(os.path.join(RAW_PATH, 'datasets_cnt.csv'))
contams = pd.read_csv(os.path.join(RAW_PATH, 'contaminations.csv'))
owners = pd.read_csv(os.path.join(RAW_PATH, 'owners.csv'))

def get_filtered_stats(stats, key, min_pct):
    stats = stats.loc[:, [key, 'dirty_seqs', 'inner_contaminations']]\
        .assign(pct=(stats.inner_contaminations/stats.dirty_seqs)*100)
    return stats.loc[stats.pct>=min_pct]

if MIN_DATE_INNER_PCT > 0:
    global date_stats
    date_stats = pd.read_csv(os.path.join(OUTPUT_PATH, 'stats_by_date.csv'))
    date_stats = get_filtered_stats(date_stats, 'date', MIN_DATE_INNER_PCT)

if MIN_PI_INNER_PCT > 0:
    global pi_stats
    pi_stats = pd.read_csv(os.path.join(OUTPUT_PATH, 'stats_by_pi.csv'))
    pi_stats = get_filtered_stats(pi_stats, 'pi_id', MIN_PI_INNER_PCT)

def is_date_allowed(date):
    if not date:
        date = 'None'

    return date in date_stats['date'].unique()

def is_pi_allowed(pi_id):
    return pi_id in pi_stats['pi_id'].unique()

for i, row in datasets.iterrows():
    id = row['id']
    owner = owners.loc[owners.dataset_id == id]
    owner_name = owner.owner_name.item()
    owner_id = owner.owner_id.item()

    meta = MetadataCollection.find_by_id(id)
    genus = str(meta.genus())
    species = str(meta.species())
    date = str(meta.date())

    if MIN_DATE_INNER_PCT > 0 and not is_date_allowed(meta.date()):
        continue

    if MIN_PI_INNER_PCT > 0 and not is_pi_allowed(owner_id):
        continue

    graph.add_node(id, cnt=float(row['cnt']), owner=owner_name, genus=genus, species=species, date=date)

contam_dict = {}

for i, row in contams.iterrows():
    key = get_key(row['from_id'], row['to_id'])
    cnt = int(row['cnt'])
    contam_dict[key] = row

for key, value in contam_dict.items():
    left, right = value['to_id'], value['from_id']
    cnt = int(value['cnt'])

    if cnt >= MIN_CNT and left in graph and right in graph:
        graph.add_edge(left, right, weight=cnt, type=value['type'])

postfix = ''
if MIN_DATE_INNER_PCT > 0 or MIN_PI_INNER_PCT > 0:
    postfix += '_filtered_by'

    if MIN_DATE_INNER_PCT > 0:
        postfix += f'_date_{MIN_DATE_INNER_PCT}'

    if MIN_PI_INNER_PCT > 0:
        postfix += f'_pi_{MIN_PI_INNER_PCT}'

nx.write_gml(graph, f'{OUTPUT_PATH}/contaminations_min_{MIN_CNT}{postfix}.gml')
