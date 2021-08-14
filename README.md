# mulmat: Futures, Expirations and Multipliers Database

## Overview

"Mulmat" is a Python library that maps futures option codes to their
corresponding underlyings and expiration date. Futures options and their
underlying futures contracts have distinct expiration dates which cannot always
be calculated in a straightforward manner (may be affected by holidays, and are
irregular in some products, such as ags).

"Mulmat" also provides a simple database of size multipliers for each product.

The local database of contracts is stored in this repository as a static file
and updated regularly by the author running the script. A script is included
that can download a list of future contracts from the CME website. Historical
expirations will be kept here. I started this database in August 2021; prior
data is not available.

The Python library provides simple indexing into this library. The list of
contracts updated in the local database by default are those commonly available
in retail platforms, but the code supports any product. If you'd like to me to
add more to the list, please send email.

## Usage

Some retail platforms only provide futures options codes and one cannot
thereafter determine the expiration date for that contract. This is intended to
make it easy to do this mapping and maintain a database of it.

You lookup a name like this:

    $ mulmat-lookup LOX1
    {
      "Product Group": "Crude Oil",
      "Product": "Crude Oil Option",
      "Symbol": "LOX1",
      "Underlying": "CLX1",
      "First Trade": "11/20/2015",
      "Expiration": "10/15/2021 13:30",
      "Settle": "10/15/2021",
      "Clearing": "LO",
      "Globex": "LO",
      "Prs": "LO",
      "Floor": "LO",
      "Group": "LO",
      "Itc": "LO",
      "Exchange": "NYMEX",
      "Contract Type": "Option"
    }

It also supports TOS-style expirations with the decade, e.g.:

    $ mulmat-lookup LOX1

(Most relevant because it's really that platform which is not providing us with
this information in the first place other than it being rendered in the UI.)

## License

This project is under the Apache license.

## Credits

Author: Martin Blais <blais@furius.ca>
