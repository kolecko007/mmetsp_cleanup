#!/usr/bin/env bash
# Runs comparison for each results folder in the path provided.
# Saves detailed results to each folder.
# Saves all the statistics to comparison.csv
#
# example ./run_statistics.sh mmetsp_extracted

if [ -f comparison.csv ]; then
    rm comparison.csv
fi

for folder in $@
do
    ./compare_with_known.py -k ${folder}/extracted_contaminations.csv \
                            -c ${folder} \
                            -r ${folder}/stats.csv \
                            -s comparison.csv
done
