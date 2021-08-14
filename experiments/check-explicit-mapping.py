#!/usr/bin/env python3
"""Check my explicit mapping against this derived one for correctness.
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

from johnny.base import discovery
from johnny.base import mark
from johnny.base import chains_pb2
from johnny.base import chains as chainslib
from johnny.base import config as configlib
from johnny.base import instrument
from johnny.base import recap as recaplib
from johnny.base.etl import petl, Table

from mulmat import months


@click.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help="Configuration filename. Default to $JOHNNY_CONFIG")
@click.option('--database', type=click.Path(exists=True), help="Database filename")
def main(config: Optional[str], database: Optional[str]):

    # Read Johnny database with futures code mapping.
    filename = configlib.GetConfigFilenameWithDefaults(config)
    config = configlib.ParseFile(filename)

    for month in config.futures_option_month_mapping.months:
        key = month.option_product[1:], month.option_month
        value = month.future_product[1:], month.future_month
        value2 = months.MONTHS[key]
        if value == value2[:2]:
            print('DIFFERENT', key, value, value2)


if __name__ == '__main__':
    main()
