#! /usr/bin/env python
import sys
import argparse

import pandas
import xarray
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='CSV map file')
    parser.add_argument('index', type=int, help='index')

    args = parser.parse_args()

    map_file = pandas.read_csv(args.file, sep=r'\s+')
    print(map_file.loc[args.index].to_string(index=True, float_format='%.1f'))


if __name__ == '__main__':
    main()
