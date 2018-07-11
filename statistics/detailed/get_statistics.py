#!/usr/bin/env python3
import pandas as pd
from statistics.detailed.scripts.lib.metadata import *

OUTPUT_DIR = 'statistics/detailed/output'
DATA_DIR = 'statistics/detailed/data'

pis = pd.read_csv(f'{DATA_DIR}/pis.csv')
datasets_cnt = pd.read_csv(f'{DATA_DIR}/datasets_cnt.csv')
owners = pd.read_csv(f'{DATA_DIR}/owners.csv')
contaminations = pd.read_csv(f'{DATA_DIR}/contaminations.csv')

contaminations = contaminations.loc[contaminations.type != 'LEFT_EATS_RIGHT'].loc[
    contaminations.type != 'RIGHT_EATS_LEFT']

MetadataCollection.load(f'{DATA_DIR}/metadata.json')


def get_datasets():
    datasets = pd.merge(datasets_cnt, owners, how='left', left_on='id', right_on='dataset_id')
    return datasets.loc[:, ['id', 'cnt', 'owner_id']]


def get_stats_by_pi():
    statistics = pd.DataFrame(
        columns=['pi_id', 'pi_name', 'seqs', 'dirty_seqs', 'clean_seqs', 'inner_contaminations',
                 'got_from_outside', 'made_to_outside'])
    datasets = get_datasets()

    for idx, row in pis.iterrows():
        new_row = dict()
        new_row['pi_id'] = row['id']
        new_row['pi_name'] = row['name']

        seqs = datasets.loc[datasets['owner_id'] == row['id']]
        new_row['seqs'] = seqs['cnt'].sum()

        seqs_list = [r['id'] for i, r in seqs.iterrows()]
        dirty_seqs = contaminations.loc[contaminations.to_id.isin(seqs_list)]

        new_row['dirty_seqs'] = dirty_seqs['cnt'].sum()
        new_row['clean_seqs'] = new_row['seqs'] - new_row['dirty_seqs']

        # received contaminations
        inner = dirty_seqs.loc[dirty_seqs.from_id.isin(seqs_list)]
        new_row['inner_contaminations'] = inner['cnt'].sum()

        outer = contaminations.loc[~contaminations.from_id.isin(seqs_list)].loc[contaminations.to_id.isin(seqs_list)]
        new_row['got_from_outside'] = outer['cnt'].sum()

        # provided contaminations
        outer = contaminations.loc[contaminations.from_id.isin(seqs_list)].loc[~contaminations.to_id.isin(seqs_list)]
        new_row['made_to_outside'] = inner['cnt'].sum()

        statistics = statistics.append([new_row], ignore_index=True)

    return statistics


def get_stats_by_dataset():
    statistics = pd.DataFrame(columns=['id', 'pi_name', 'pi_id', 'seqs', 'dirty_seqs', 'clean_seqs', 'found_in_other'])

    for idx, row in datasets.iterrows():
        new_row = dict()

        new_row['id'] = row['id']
        pi = pis[pis.id == row['provider_id']].iloc[0]
        new_row['pi_name'] = pi['name']
        new_row['pi_id'] = pi['id']

        new_row['seqs'] = row['cnt']
        new_row['dirty_seqs'] = contaminations.loc[contaminations.to_id == row['id']]['cnt'].sum()
        new_row['clean_seqs'] = new_row['seqs'] - new_row['dirty_seqs']
        new_row['found_in_other'] = contaminations.loc[contaminations.from_id == row['id']]['cnt'].sum()

        statistics = statistics.append([new_row], ignore_index=True)

    return statistics


def get_stats_by_run_id():
    statistics = pd.DataFrame(
        columns=['run_id', 'datasets_cnt', 'seqs', 'dirty_seqs', 'clean_seqs', 'inner_contaminations',
                 'outer_contaminations'])

    for run_data in datasets.groupby('run_id'):
        run_id = run_data[0]
        run_datasets = run_data[1]
        run_dataset_ids = list(run_datasets.loc[:, 'id'])

        new_row = dict()

        new_row['run_id'] = run_id
        new_row['datasets_cnt'] = len(run_data[1].index)
        new_row['seqs'] = run_datasets['cnt'].sum()

        dirty_seqs = contaminations.loc[contaminations.to_id.isin(run_dataset_ids)]['cnt'].sum()
        new_row['dirty_seqs'] = dirty_seqs
        new_row['clean_seqs'] = new_row['seqs'] - new_row['dirty_seqs']

        inner = contaminations.loc[contaminations.from_id.isin(run_dataset_ids)].loc[
            contaminations.to_id.isin(run_dataset_ids)]['cnt'].sum()
        new_row['inner_contaminations'] = inner

        outer = contaminations.loc[contaminations.to_id.isin(run_dataset_ids)].loc[
            ~contaminations.from_id.isin(run_dataset_ids)]['cnt'].sum()
        new_row['outer_contaminations'] = outer

        statistics = statistics.append([new_row], ignore_index=True)

    return statistics


def get_stats_by_date():
    datasets = get_datasets()
    dates = []

    for idx, row in datasets.iterrows():
        date = 'None'
        meta = MetadataCollection.find_by_id(row['id'])

        if meta and meta.date():
            date = meta.date()

        dates.append(date)

    dated_datasets = datasets.assign(date=dates)

    statistics = pd.DataFrame(
        columns=['date', 'ds_cnt', 'seqs', 'dirty_seqs', 'clean_seqs', 'inner_contaminations', 'got_from_outside',
                 'made_to_outside'])

    for date in list(set(dates)):
        ds = dated_datasets.loc[dated_datasets['date'] == date]
        ds_list = [r['id'] for i, r in ds.iterrows()]

        new_row = {}
        new_row['date'] = date
        new_row['ds_cnt'] = len(ds_list)
        new_row['seqs'] = ds['cnt'].sum()
        new_row['dirty_seqs'] = contaminations.loc[contaminations.to_id.isin(ds_list)]['cnt'].sum()
        new_row['clean_seqs'] = new_row['seqs'] - new_row['dirty_seqs']
        new_row['inner_contaminations'] = contaminations.loc[contaminations.to_id.isin(ds_list)].loc[
            contaminations.from_id.isin(ds_list)]['cnt'].sum()

        new_row['got_from_outside'] = contaminations.loc[contaminations.to_id.isin(ds_list)].loc[
            ~contaminations.from_id.isin(ds_list)]['cnt'].sum()

        new_row['made_to_outside'] = contaminations.loc[~contaminations.to_id.isin(ds_list)].loc[
            contaminations.from_id.isin(ds_list)]['cnt'].sum()

        statistics = statistics.append([new_row], ignore_index=True)

    return statistics

# get_stats_by_pi().to_csv(f'{OUTPUT_DIR}/stats_by_pi.csv', index=False)
get_stats_by_date().to_csv(f'{OUTPUT_DIR}/stats_by_date.csv', index=False)

# get_stats_by_dataset().to_csv(f'{OUTPUT_DIR}/stats_by_dataset.csv', index=False)
# get_stats_by_run_id().to_csv(f'{OUTPUT_DIR}/stats_by_run_id.csv', index=False)
