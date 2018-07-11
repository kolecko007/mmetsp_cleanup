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

            # Adding the reasons of deletion
            if deleted:
                opts = (contaminations_dir_path, parsed_id['db_id'], parsed_id['full_seq_id'])
                extra_data = os.popen("cat %s%s_deleted_stats.csv | grep '%s'" % opts).read().strip()
                extra_data = extra_data.split("\n")[0]

                if extra_data.strip() == '':
                    raise Exception(
                        'Fail: cannot detect %s in %s deleted stats' % (parsed_id['full_seq_id'], parsed_id['db_id']))

                extra_data = ','.join(extra_data.split(',')[1:])
                result += ",%s" % extra_data

            output.write("%s\n" % result)
            pb.update(i + 1)
