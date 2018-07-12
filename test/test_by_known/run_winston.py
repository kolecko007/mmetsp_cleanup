#!/usr/bin/env python3

import re
import argparse
import subprocess

DEFAULT_THRESHOLDS = {"REGULAR":         1.1,
                      "CLOSE":           0.04,
                      "LEFT_EATS_RIGHT": 10,
                      "RIGHT_EATS_LEFT": 0.1}


def parse_options():
    description = """Runs Winston with different settings
    syntax of --values command:
    `REGULAR: 1.0 1.1 1.2 1.3 1.4 1.5`
    `LEFT_EATS_RIGHT: 5 6 7 8 9 10, RIGHT_EATS_LEFT: 0.2 0.17 0.14 0.12 0.11 0.1`
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-s", "--settings", required=True, help="Path to settings.yml")
    parser.add_argument("-w", "--working_folder", required=True, help="Winston working folder")
    parser.add_argument("-v", "--values", required=True, help="String of variable values and types")
    parser.add_argument("-e", "--winston", required=True, help="Path to winston")

    return parser.parse_args()


def set_setting(settings_path, setting, new_value):
    subprocess.call(f"sed -i 's#\({setting}\).*#\\1: {new_value}#' {settings_path}", shell=True)
    pass


def set_default_thresholds(settings_path):
    for pair_type, threshold in DEFAULT_THRESHOLDS.items():
        set_setting(settings_path, pair_type, threshold)


def parse_values(values_string):
    matches = re.findall('(\w+):\s?(([\d|\.]+\s?)+)', values_string)
    result = {}

    for m in matches:
        result[m[0]] = list(map(float, m[1].split()))

    return result


def run_winston(winston_path, settings_path, working_folder, thresholds):
    for i, _val in enumerate(thresholds[list(thresholds.keys())[0]]):
        results_name = f"results"

        for key in thresholds.keys():
            print(f'Setting {key} to {thresholds[key][i]}')
            results_name += f"_{key}_{thresholds[key][i]}"
            set_setting(settings_path, key, thresholds[key][i])

        command = f"{winston_path} --config_path {settings_path}"

        print(f'running winston: {command}')
        print()

        subprocess.call(command, shell=True)
        subprocess.call(f"mv {working_folder}/results {working_folder}/{results_name}", shell=True)


def main():
    options = parse_options()
    options.working_folder = options.working_folder.rstrip('/')

    set_default_thresholds(options.settings)
    set_setting(options.settings, "output", options.working_folder)

    thresholds = parse_values(options.values)
    run_winston(options.winston, options.settings, options.working_folder, thresholds)


if __name__ == '__main__':
    main()
