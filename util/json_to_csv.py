import argparse
import json
import os
import pandas
import re

'''
This script attempts to merge mappings from a mappings.json file used by
https://github.com/PublicI/fec-parse or https://github.com/esonderegger/fecfile
with the csv files in this repository. It first loads the csv into a pandas
dataframe and then adds any rows and columns that exist in the json but not
in the csv, and then overwrites the csv from this dataframe.

Example usage:
python json_to_csv.py /path/to/mappings.json "^sd" SchD.csv
'''


def df_from_form_name(form_name):
    this_file = os.path.abspath(__file__)
    this_dir = os.path.dirname(this_file)
    form_path = os.path.join(this_dir, '..', form_name)
    return pandas.read_csv(form_path, index_col=0)


def add_mappings_to_df(fecfile, df):
    fec_versions = fecfile.keys()
    versions = sorted(fec_versions, reverse=True, key=lambda v: version_cmp(v))
    for fec_key in versions:
        print(fec_key)
        df_match = None
        df_k = None
        for df_key in df.keys():
            if df_key in fec_key:
                if df_match:
                    print('double match!!')
                df_match = True
                if df_key != fec_key:
                    print('!!! {} != {}'.format(df_key, fec_key))
                df = df.rename(index=str, columns={df_key: fec_key})
                df_k = fec_key
        if df_match is None:
            print('no match for {}'.format(fec_key))
            df[fec_key] = None
            for i in range(len(fecfile[fec_key])):
                mapping = fecfile[fec_key][i]
                map_val = i + 1
                if mapping not in df[fec_key]:
                    print('{} not mapped (new column)'.format(mapping))
                    df.loc[mapping] = [None] * len(df.keys())
                df[fec_key][mapping] = map_val
            continue
        for i in range(len(fecfile[fec_key])):
            mapping = fecfile[fec_key][i]
            map_val = i + 1
            if mapping not in df[df_k]:
                print('{} not mapped'.format(mapping))
                df.loc[mapping] = [None] * len(df.keys())
                df[df_k][mapping] = map_val
                print(df[df_k][mapping])
                continue
            if df[df_k][mapping] != map_val:
                print('mismatch! {} - {} - {}'.format(
                    mapping,
                    df[df_k][mapping],
                    map_val,
                ))
                df[df_k][mapping] = map_val
    return df


def version_cmp(v):
    temp = re.sub('[^0-9P]+', '', v)
    return re.sub('P', '&', temp)


def fix_first_line(filename):
    with open(filename) as from_file:
        from_lines = from_file.readlines()
    cols = from_lines[0].strip().split(',')
    new_cols = ['' if c.startswith('Unnamed') else c for c in cols]
    new_line = ','.join(new_cols) + '\n'
    from_lines[0] = new_line
    with open(filename, mode='w') as to_file:
        to_file.writelines(from_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("json")
    parser.add_argument("regex")
    parser.add_argument("csv")
    args = parser.parse_args()
    mappings = {}
    with open(args.json) as data_file:
        mappings = json.loads(data_file.read())
    form_mappings = mappings[args.regex]
    df = df_from_form_name(args.csv)
    df = add_mappings_to_df(form_mappings, df)
    df.to_csv('../' + args.csv)
    fix_first_line('../' + args.csv)
