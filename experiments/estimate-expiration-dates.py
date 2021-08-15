#!/usr/bin/env python3
"""Estimate expiration dates based on historical data.
"""
__copyright__ = "Copyright (C) 2021  Martin Blais"
__license__ = "Apache 2.0"

from os import path
from typing import Any, Optional, Tuple
import collections
import datetime
import pprint
import re

import click
import petl
from petl import Table
from dateutil import parser
from dateutil import relativedelta

from johnny.base import discovery
from johnny.base import mark
from johnny.base import chains_pb2
from johnny.base import chains as chainslib
from johnny.base import config as configlib
from johnny.base import instrument
from johnny.base import recap as recaplib
from johnny.base.etl import petl, Table

import mulmat


CODES = 'FGHJKMNQUVXZ'


OF_INTEREST = {'ZN', 'CL', 'PL', 'ZT', 'GE', 'NG', 'ZW', 'HE', 'MNQ', 'ZF', 'GC', '6J',
               'RTY', 'ZC', 'SI', 'VX', 'ZB', '6E', 'NQ', 'ZS', '6C', 'ES', '6A', 'MES',
               'M2K', 'YM', '6B', 'LE', 'HG'}


def get_first_day(symbol: str) -> datetime.date:
    """Get the day of the given product's expiration month."""
    match = re.fullmatch(r'.*([FGHJKMNQUVXZ])(\d+)', symbol)
    assert match
    code, year = match.groups()
    month = (CODES.index(code) % 12) + 1
    return datetime.date(2020 + int(year), month, 1)


def get_last_day(symbol: str) -> datetime.date:
    """Get the day of the given product's expiration month."""
    match = re.fullmatch(r'.*([FGHJKMNQUVXZ])(\d+)', symbol)
    assert match
    code, year = match.groups()
    month = (CODES.index(code) % 12) + 1
    return (datetime.date(2020 + int(year), month, 1)
            + relativedelta.relativedelta(months=1)
            - datetime.timedelta(days=1))


@click.command()
@click.option('--database', type=click.Path(exists=True), help="Database filename")
def main(database: Optional[str]):
    expirations = mulmat.read_cme_database(database)

    expirations = (expirations
                   .selecteq('Contract Type', 'Option')
                   .select(lambda r: re.fullmatch(r'.*[FGHJKMNQUVXZ][12]$', r['Symbol']))
                   .select(lambda r: re.fullmatch(r'.*[FGHJKMNQUVXZ][12]$', r['Underlying']))
                   .select(lambda r: r['Underlying'][:-2] in OF_INTEREST)
                   .cut('Underlying', 'Symbol', 'Expiration', 'Product')
                   .convert('Expiration', lambda v: parser.parse(v).date())
                   .addfield('LastDay', lambda r: get_last_day(r.Symbol))
                   .addfield('DaysDiff', lambda r: (r.Expiration - r.LastDay).days)
                   .sort(['Underlying', 'Symbol'])
                   .selectgt('DaysDiff', 0)
                   )

    print(expirations.lookallstr())


if __name__ == '__main__':
    main()
