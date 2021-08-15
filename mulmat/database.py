"""Basic functions on the full CME database.
"""
__copyright__ = "Copyright (C) 2021  Martin Blais"
__license__ = "GNU GPLv2"


import datetime
import re
from os import path
from typing import Mapping, Optional

import petl
from petl import Table, Record
from dateutil import parser, relativedelta


_CODES = 'FGHJKMNQUVXZ'


def read_cme_database(database: Optional[str] = None) -> Table:
    """Read the CME database to as PETL table."""
    if database is None:
        root = path.dirname(path.dirname(__file__))
        database = f"{root}/data/cme-expirations.csv"
    return petl.fromcsv(database)


def get_expirations_lookup(database: Table) -> dict[str, Record]:
    """Create a data structure to lookup options expirations."""
    return (database
            .selecteq('Contract Type', 'Option')
            .recordlookupone('Symbol'))


def estimate_expiration(options_symbol: str) -> datetime.date:
    """Roughly estimate the expiration date from the futures options name."""

    # TODO(blais): Eventually we should implement all the ad-hoc rules from each
    # CME product's contract spec, like "2 business days before the 3rd
    # wednesday" and such, which includes offsets due to holidays. They're all
    # different. For now we hit the last day of the expiration code's month. It
    # was verfied on a full snapshot of the CME database that this is always
    # greater or equal to the true expiration date.

    # Break down the options symbol.
    match = re.fullmatch(r'.*([FGHJKMNQUVXZ])(\d+)', options_symbol)
    if not match:
        raise ValueError(f"Invalid futures options symbol '{options_symbol}'")
    code, year = match.groups()
    month = (_CODES.index(code) % 12) + 1

    year = int(year)
    year += 2000 if year >= 10 else 2020
    return (datetime.date(year, month, 1)
            + relativedelta.relativedelta(months=1)
            - datetime.timedelta(days=1))


def get_or_estimate_expiration(database_lookup: Mapping[str, Record],
                               options_symbol: str) -> datetime.date:
    """Attempt to fetch the precise expiration date; if not, estimate it from the
    expiration month code. You have to provide an already parsed database table
    of the CME expirations.

    See also get_expirations_lookup().
    """
    rec = database_lookup.get(options_symbol, None)
    if rec is None:
        return estimate_expiration(options_symbol)
    else:
        return parser.parse(rec['Expiration']).date()
