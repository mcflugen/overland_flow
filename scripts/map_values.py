#! /usr/bin/env python
import sys
import os
import argparse
from itertools import islice

import pandas
import xarray
import numpy as np


def load_wtm(fname):
    with open(fname, 'r') as fp:
        header = ''.join(list(islice(fp, 4)))

    data = pandas.read_csv(fname, skiprows=4, header=0, sep=r'\s+')

    return data, header

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='DSSAT input file')

    args = parser.parse_args()

    data, header = load_wtm(args.file)
    # with open(args.file, 'r') as fp:
    #     header = list(islice(fp, 4))

    # data = pandas.read_csv(args.file, skiprows=4, header=0, sep=r'\s+')

    map_values = pandas.read_csv(sys.stdin, sep=r'\s+', header=None,
                                 names=['FROM', 'TO'])
    d = dict(zip(map_values['FROM'], map_values['TO']))
    d[0.0] = 0.0
    data['RAIN'] = data['RAIN'].map(d)

    print(header, end='')
    print(data.to_string(index=False))


if __name__ == '__main__':
    main()
