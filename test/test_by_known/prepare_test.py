#!/usr/bin/env python3

import os
import re
import argparse
import itertools
import subprocess
from random import shuffle


def parse_options():
    description = """Preparing the test for WinstonCleaner on MMETSP
    
    The script:
    1. select randomly half of good/bad contigs
    2. extracts hits/fastas for these organisms and put it to a new working folder
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-k", "--known", required=True, help="Known contaminations (.csv)")
    parser.add_argument("-m", "--mmetsp", required=True, help="MMETSP data folder (prepared for Winston)")
    parser.add_argument("-o", "--output", required=True, help="Output folder")
    return parser.parse_args()


def make_known_dict(path):
    result = {}

    with open(path) as f:
        for l in f.readlines():
            spl = l.split(',')
            key = spl[1].strip()

            if key not in ['good', 'bad']:
                continue

            if key not in result:
                result[key] = []

            result[key].append(spl[0])

    return result


def extract_random_seqs(known_dict):
    result = {}

    for t, seqs in known_dict.items():
        shuffle(seqs)
        result[t] = seqs[:int(len(seqs) / 2)]

    return result


def save_extracted_seqs(extracted_dict, output_path):
    with open(f"{output_path}/extracted_contaminations.csv", 'w') as f:
        for t, seqs in extracted_dict.items():
            for seq in seqs:
                f.write(f"{seq},{t}\n")


def extract_org_id(seq_id):
    return re.search(r'MMETSP\d{4}', seq_id.strip()).group()


def get_unique_orgs(seq_dict):
    seqs = list(itertools.chain.from_iterable(seq_dict.values()))
    return list(set(map(extract_org_id, seqs)))


def create_folders(base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    else:
        raise Exception("Output is not empty")

    os.makedirs(os.path.join(base_path, "blast_results"))
    os.makedirs(os.path.join(base_path, "blast_results", "one_vs_all"))
    os.makedirs(os.path.join(base_path, "datasets"))


def extract_data_from_mmetsp(mmetsp_path, output_path, org_list):
    for org_id in org_list:
        dataset_path = os.path.join(output_path, 'datasets', org_id + '.fas')
        subprocess.call(f"touch {dataset_path}", shell=True)

        mmetsp_one_vs_all_path = os.path.join(mmetsp_path, "blast_results", "one_vs_all")
        output_one_vs_all_path = os.path.join(output_path, "blast_results", "one_vs_all")
        subprocess.call(f"cp -v {mmetsp_one_vs_all_path}/{org_id}.blastab {output_one_vs_all_path}", shell=True)


def copy_common_files(mmetsp_path, output_path):
    subprocess.call(f"cp -v {mmetsp_path}/types.csv {output_path}", shell=True)
    subprocess.call(f"cp -v {mmetsp_path}/system_names.csv {output_path}", shell=True)


def main():
    options = parse_options()
    options.output = options.output.rstrip('/')
    options.mmetsp = options.mmetsp.rstrip('/')

    create_folders(options.output)

    known_dict = make_known_dict(options.known)
    rand_known_dict = extract_random_seqs(known_dict)
    save_extracted_seqs(rand_known_dict, options.output)
    org_list = get_unique_orgs(rand_known_dict)

    extract_data_from_mmetsp(options.mmetsp, options.output, org_list)
    copy_common_files(options.mmetsp, options.output)


if __name__ == '__main__':
    main()
