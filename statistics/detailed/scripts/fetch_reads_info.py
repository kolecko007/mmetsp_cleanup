#!/usr/bin/env python3

from ftplib import FTP
import pandas as pd
import progressbar
import requests
import re

BASE_URL = 'http://datacommons.cyverse.org/angular/reverse/?djng_url_name=api_preview_file&djng_url_kwarg_path='
PATH = '/iplant/home/shared/imicrobe/projects/104/samples'


def prepare_file_paths():
    ftp = FTP('ftp.imicrobe.us')
    ftp.login()
    ftp.cwd('projects/104/samples')
    dirs = sorted(e for e in ftp.nlst() if '.' not in e)

    paths = []

    with open('paths.txt', 'w') as f:
        bar = progressbar.ProgressBar(max_value=len(dirs))

        for i, d in enumerate(dirs):
            reads = ftp.nlst(f"{d}/*1.fastq.gz")

            if len(reads) > 0:
                read = '/'.join([PATH, reads[0]])
                paths.append(read)
                f.write(f"{read}\n")

            bar.update(i + 1)


def download_files():
    with open('reads_preview.txt', 'w') as f:
        lines = [e.strip() for e in open('paths.txt').readlines()]
        bar = progressbar.ProgressBar(max_value=len(lines))

        for i, line in enumerate(lines):
            line = '.'.join(line.split('.')[:-1])
            url = BASE_URL + line
            r = requests.get(url)
            f.write(f"->{line}\n")
            f.write(f"{r.text}\n")

            bar.update(i + 1)


def get_run_id(read_info):
    match = re.match(r".+run=(.+)\n", read_info)
    if not match:
        return None
    return match.group(1)


def get_dataset_id(file_name):
    return re.match(r"MMETSP\d{4}", file_name).group(0)


def make_csv():
    els = [e.strip() for e in open('reads_preview.txt').read().split('->') if len(e.strip()) > 0]
    els = {e.split("\n")[0].split("/")[-1]: "\n".join(e.split("\n")[1:]) for e in els}

    with open('../prepared_data/runs.csv', 'w') as f:
        f.write("dataset_id,run_id\n")
        for k, v in els.items():
            f.write(f"{get_dataset_id(k)},{get_run_id(v)}\n")


def append_run_id_to_datasets():
    datasets_path = '../prepared_data/datasets.csv'
    datasets = pd.read_csv(datasets_path)
    runs = pd.read_csv('runs.csv')

    if 'run_id' in datasets.columns:
        datasets = datasets.loc[:, set(datasets.columns) - {'run_id'}]

    datasets = pd.merge(datasets, runs, how='left', left_on='id', right_on='dataset_id').drop(['dataset_id'], axis=1)

    datasets.to_csv(datasets_path, index=False)


# prepare_file_paths()
# download_files()
# make_csv()
append_run_id_to_datasets()
