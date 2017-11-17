#! /usr/bin/env python
import argparse
import pandas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='DSSAT WTH input file')

    args = parser.parse_args()

    data = pandas.read_csv(args.file, skiprows=4, header=0, sep=r'\s+')
    unique_storms = pandas.DataFrame({'RAIN': data['RAIN'].unique()})

    print(unique_storms.to_string(header=False, index=False))


if __name__ == '__main__':
    main()
