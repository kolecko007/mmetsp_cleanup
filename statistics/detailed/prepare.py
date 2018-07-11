#!/usr/bin/env python3

import pandas as pd


RAW_DATA_DIR = 'raw_data'
OUTPUT_DIR = 'output'

# poluters_datasets = pd.read_csv(f'{RAW_DATA_DIR}/polluter_dict.csv', header=None, names=['mmetsp_id', 'name', 'id'])


def prepare_polluters():
    polluters = poluters_datasets.loc[:, ['id', 'name']]
    polluters = polluters.drop_duplicates()
    polluters.to_csv(f'{OUTPUT_DIR}/polluters.csv', index=False)


def prepare_datasets():
    datasets = pd.read_csv(f'{RAW_DATA_DIR}/datasets_cnt.csv', header=None, names=['id', 'cnt'])
    datasets = datasets.loc[:, ['id', 'cnt']]

    runs = pd.read_csv(f'{RAW_DATA_DIR}/runs.csv')
    datasets = pd.merge(datasets, runs, how='left', left_on='id', right_on='dataset_id')

    datasets = pd.merge(datasets, poluters_datasets, how='left', left_on='id', right_on='mmetsp_id')
    datasets = datasets.rename(columns={'id_x': 'id', 'id_y': 'provider_id'}).loc[:,
               ['id', 'cnt', 'provider_id', 'run_id']]

    datasets = datasets.fillna('None')

    datasets.to_csv(f'{OUTPUT_DIR}/datasets.csv', index=False)


def prepare_contaminations():
    types = pd.read_csv(f'{RAW_DATA_DIR}/types.csv')
    contaminations = pd.read_csv(f'{RAW_DATA_DIR}/contaminations.csv')
    full_contaminations = pd.merge(contaminations, types,
                                   how='left',
                                   left_on=['to_id', 'from_id'],
                                   right_on=['left_id', 'right_id']).drop(columns=['left_id', 'right_id'])

    full_contaminations.to_csv(f'{OUTPUT_DIR}/contaminations.csv', index=False)


# prepare_polluters()
# prepare_datasets()
prepare_contaminations()
