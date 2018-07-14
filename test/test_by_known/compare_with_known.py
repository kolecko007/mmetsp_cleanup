#!/usr/bin/env python3
import os
import re
from optparse import OptionParser

import progressbar


def parse_options():
    parser = OptionParser()
    parser.add_option("-k", "--known_contaminations_path", help="Path for known contaminations .csv file")
    parser.add_option("-c", "--contaminations_dir_path", help="Path for the folder with find_contaminations.py output")
    parser.add_option("-r", "--results_path", default="contamination_stats.csv",
                      help="Path for the output file")
    parser.add_option("-s", "--stat_result_path", help="Path for the run statistics (mis. deleted and mis. kept %)")

    return parser.parse_args()[0]


def parse_org_id(full_string):
    found = re.search('(MMETSP.+)-((\d+)\|(\d+))', full_string)

    if found:
        return {'full_seq_id': found.group(0), 'db_id': found.group(1)}
    else:
        raise Exception('Cannot detect organism seq id')


if __name__ == '__main__':
    options = parse_options()

    contaminations_dir_path = os.path.join(options.contaminations_dir_path, '')
    known_contaminations_path = options.known_contaminations_path

    contaminations = {}
    pb = progressbar.ProgressBar(max_value=int(os.popen('cat %s | wc -l' % known_contaminations_path).read()))

    with open(known_contaminations_path, 'r') as known, open(options.results_path, 'w') as output:
        for i, line in enumerate(known.readlines()):
            line = line.strip()
            parsed_id = parse_org_id(line)
            result = line

            # Checking if the sequence deleted
            deleted = False
            opts = (contaminations_dir_path, parsed_id['db_id'], parsed_id['full_seq_id'])
            found = os.popen("cat %s%s_deleted.fasta | grep '%s$'" % opts).read().strip()
            if found != '':
                deleted = True

            result += ",%s" % deleted

            output.write("%s\n" % result)
            pb.update(i + 1)

    if options.stat_result_path:
        stats = {
            'bad': 0,
            'kept_bad': 0,
            'good': 0,
            'deleted_good': 0
        }

        with open(options.results_path) as f:
            lines = f.readlines()
            for line in lines:
                _seq, seq_type, deleted = line.strip().split(',')

                if seq_type == 'bad':
                    stats['bad'] += 1
                    if deleted == 'False':
                        stats['kept_bad'] += 1
                elif seq_type == 'good':
                    stats['good'] += 1
                    if deleted == 'True':
                        stats['deleted_good'] += 1

        mistakenly_kept_pct = round((stats['kept_bad']/stats['bad'])*100, 2)
        mistakenly_deleted_pct = round((stats['deleted_good']/stats['good'])*100, 2)

        if not os.path.exists(options.stat_result_path):
            with open(options.stat_result_path, 'w') as f:
                f.write(f"run_id,mistakenly_kept_pct,mistakenly_deleted_pct\n")

        with open(options.stat_result_path, 'a') as f:
            f.write(f"{contaminations_dir_path.split('/')[-2]},{mistakenly_kept_pct},{mistakenly_deleted_pct}\n")



