#!/usr/bin/env python3

import os, re, subprocess
from optparse import OptionParser
from pathlib import Path
import pandas as pd

parser = OptionParser(description="Collect raw data from Decross results")
parser.add_option("--decross_output_folder")
(options, args) = parser.parse_args()

if not options.decross_output_folder:
    raise Exception("Output folder must be provided")

RAW_DATA_PATH = os.path.join('statistics/detailed/raw_data')
DECROSS_PATH = os.path.join(options.decross_output_folder, 'results')
DATASETS_PATH = os.path.join(options.decross_output_folder, 'datasets')
TYPES_PATH = os.path.join(options.decross_output_folder, 'types.csv')


def prepare_contaminations():
    contams = pd.DataFrame(columns=['to_id', 'from_id', 'cnt'])

    for path in Path(DECROSS_PATH).glob("MMETSP*_contaminations.csv"):
        to_id = re.findall('MMETSP\d{4}', str(path))[0]

        for idx, row in pd.read_csv(path, names=['from_id', 'cnt']).iterrows():
            contams = contams.append([{'to_id': to_id, 'from_id': row['from_id'], 'cnt': row['cnt']}],
                                     ignore_index=True)

    contams.to_csv(os.path.join(RAW_DATA_PATH, 'contaminations.csv'), index=False)


def prepare_datasets():
    datasets = pd.DataFrame(columns=['id', 'cnt'])

    for path in Path(DATASETS_PATH).glob('MMETSP*.fas'):
        result = subprocess.run(f"grep -c '>' {path}", shell=True, stdout=subprocess.PIPE)
        dataset_id = re.findall(r'MMETSP\d{4}', str(path))[-1]
        cnt = int(result.stdout.strip())

        datasets = datasets.append([{'id': dataset_id, 'cnt': cnt}], ignore_index=True)

    datasets.to_csv(os.path.join(RAW_DATA_PATH, 'datasets_cnt.csv'), index=False)


def prepare_pis():
    pass


# prepare_contaminations()
prepare_datasets()
