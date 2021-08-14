#!/usr/bin/env python
"""Test uniqueness of symbol column as potential index.
"""
import collections

import petl

import argparse
import logging

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('filename', help='Filenames')
    args = parser.parse_args()

    table = petl.fromcsv(args.filename)
    print(table.nrows())
    print(len(set(table.values('Symbol'))))

    cdict = collections.defaultdict(list)
    for row in table.records():
        key = (row['Symbol'], row['Contract Type'])
        cdict[key].append(row)

    for rows in cdict.values():
        if len(rows) > 1:
            pp(rows)


if __name__ == '__main__':
    main()
