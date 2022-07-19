#!/usr/bin/env python3
"""Enumerate all mappings between options month and underlying contract month.
"""
__copyright__ = "Copyright (C) 2021  Martin Blais"
__license__ = "Apache 2.0"

import re
import collections
from os import path
import datetime
import logging
from typing import Any, Optional, Tuple

from dateutil import parser
import click
import petl
from petl import Table


def split_month(symbol: str, settle_year: int) -> Tuple[str, str, str]:
    match = re.match('(.*)([FGHJKMNQUVXZ])(\d{1,2})$', symbol)
    if match is None:
        raise ValueError
    product, month, year = match.groups()
    if len(year) == 1:
        decade = (settle_year % 100) - (settle_year % 10)
        year = decade + int(year)
    else:
        year = int(year)
    return product, month, year


def list_products(options: Table):
    """Print a mapping of (option, underlying) product codes."""

    # Calculate a mapping of option product code to corresponding underlying.
    mapping = collections.defaultdict(set)
    for rec in options.records():
        settle = parser.parse(rec['Settle']).date()
        try:
            option_product, _, __ = split_month(rec['Symbol'], settle.year)
            under_product, _, __ = split_month(rec['Underlying'], settle.year)
        except ValueError:
            continue
        mapping[option_product].add(under_product)

    # Check uniqueness.
    for option, underlyings in list(mapping.items()):
        if len(underlyings) > 1:
            raise ValueError(
                f"Multivalent mapping from option {option} to futures: {underlyings}")
        mapping[option] = next(iter(underlyings))

    return dict(mapping)


def only(aset: set[Any]) -> Any:
    assert len(aset) == 1
    return next(iter(aset))


def list_months(options: Table):
    """Print mapping of ((option, option-month), (underlying, underlying-month)) codes."""

    # Calculate a mapping of option product code to corresponding underlying.
    mapping = collections.defaultdict(lambda: collections.defaultdict(
        lambda: collections.defaultdict(set)))
    for rec in options.records():
        settle = parser.parse(rec['Settle']).date()
        try:
            oproduct, omonth, oyear = split_month(rec['Symbol'], settle.year)
            uproduct, umonth, uyear = split_month(rec['Underlying'], settle.year)
        except ValueError:
            continue
        yeardiff = uyear - oyear
        if yeardiff >= 10:
            continue
        if yeardiff < 0:
            raise ValueError(f"Invalid value for year diff: {yeardiff}; {rec}")
        mapping[uproduct][oproduct][omonth].add((umonth, yeardiff, oyear))

    # Remove default dicts.
    mapping = {key1: {key2: {key3: value3
                             for key3, value3 in value2.items()}
                      for key2, value2 in value1.items()}
               for key1, value1 in mapping.items()}

    # Reconstruct a mapping for option to underlying, with the year difference.
    option_under_mapping = {}
    for uproduct, oproducts in mapping.items():
        for oproduct, omonths in oproducts.items():
            for omonth, umonths in omonths.items():
                smonths = sorted({(umonth, yeardiff) for umonth, yeardiff, oyear in umonths})
                if len(smonths) > 1:
                    for umonth, yeardiff, oyear in umonths:
                        option_under_mapping[(oproduct, omonth, oyear)] = (uproduct, umonth, yeardiff)
                    option_under_mapping[(oproduct, omonth)] = None  # Mark as impossible.
                else:
                    (umonth, yeardiff) = only(smonths)
                    option_under_mapping[(oproduct, omonth)] = (uproduct, umonth, yeardiff)

    return option_under_mapping
