import json
import os.path
import re

import click
import pandas as pd

TEST_FUNC_PATTERN = re.compile(r'^(?P<func>[a-zA-Z0-9_]+)(\[[^\]]*\])?$')


def get_testfunc_name(name: str):
    matching = TEST_FUNC_PATTERN.fullmatch(name)
    return matching.group('func')


def open_benchmark_file(filename: str) -> pd.DataFrame:
    with open(filename, 'r') as f:
        json_ = json.load(f)

    bms = json_['benchmarks']
    params, stats = set(), set()
    for item in bms:
        if item.get('params', None):
            params |= set(item['params'].keys())
        if item.get('stats', None):
            stats |= set(item['stats'].keys())

    params, stats = list(params), list(stats)
    columns = [
        'group_name',
        'func_name',
        *(f'param:{p}' for p in params),
        *stats,
    ]
    data = []
    for item in bms:
        item_params = dict(item.get('params', None) or {})
        item_stats = dict(item.get('stats', None) or {})
        data.append((
            item.get('group', None),
            get_testfunc_name(item['name']),
            *(item_params.get(p, None) for p in params),
            *(item_stats.get(s, None) for s in stats),
        ))

    return pd.DataFrame(data=data, columns=columns)


@click.command(context_settings=dict(help_option_names=['-h', '--help']),
               help='Transform json format file created by pytest-benchmark to simple csv format.')
@click.option('-i', '--input', 'input_filename', type=click.Path(exists=True, dir_okay=False, readable=True),
              help='Input json file.')
@click.option('-o', '--output', 'output_filename', type=click.Path(dir_okay=False),
              help='Output csv file.')
def trans(input_filename: str, output_filename: str):
    df = open_benchmark_file(input_filename)
    output_dir, _ = os.path.split(output_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(output_filename)


if __name__ == '__main__':
    trans()
