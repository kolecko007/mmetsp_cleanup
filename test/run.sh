#!/bin/bash
set -e

pushd `dirname $0` > /dev/null
ROOT_PATH="$(dirname "`pwd -P`")"
OUT_PATH=$ROOT_PATH/test/output
INPUT_PATH=$ROOT_PATH/test/input

$ROOT_PATH/prepare.rb --datasets_path=$INPUT_PATH/datasets.tar.gz \
                                  --one_vs_all_path=$INPUT_PATH/one_vs_all.tar.gz \
                                  --all_vs_all_path=$INPUT_PATH/all_vs_all.tar.gz \
                                  --output_path=$OUT_PATH
