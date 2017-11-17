#! /usr/bin/env python
import sys
import argparse

import pandas
import xarray
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='NetCDF file')
    parser.add_argument('rain', help='Rain rate')

    args = parser.parse_args()

    with xarray.open_dataset(args.file) as ds:
        infiltration = ds['soil_water_infiltration__depth'][-1].data * 1000.
        rain = pandas.DataFrame({args.rain: infiltration.flatten()})

    print(rain.to_string(index=False, header=True, float_format='%.2f'))


if __name__ == '__main__':
    main()
