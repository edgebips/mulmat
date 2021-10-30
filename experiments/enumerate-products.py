#!/usr/bin/env python3
"""Enumerate all mappings between options month and underlying contract month.
"""
__copyright__ = "Copyright (C) 2021  Martin Blais"
__license__ = "Apache 2.0"

import re
import collections
import pprint
from os import path
from typing import Any, Optional, Tuple

import click
import petl
from petl import Table

import mulmat
import mulmat.lists


@click.command()
@click.option('--database', type=click.Path(exists=True), help="Database filename")
@click.option('--products', '-p', is_flag=True)
@click.option('--months', '-m', is_flag=True)
def main(database: Optional[str], products: bool, months: bool):
    expirations = mulmat.read_cme_database(database)

    options = (expirations
               .selecteq('Contract Type', 'Option')
               # Many rows don't have an underlying, filter.
               .selecttrue('Underlying')
               .cut('Symbol', 'Underlying'))

    if products:
        pprint.pprint(mulmat.lists.list_products(options))
    if months:
        pprint.pprint(mulmat.lists.list_months(options))


if __name__ == '__main__':
    main()
