# mulmat: Futures, Expirations and Multipliers Database

## Overview

"Mulmat" is a Python library that maps **futures option codes** to their
corresponding **underlyings** and **expiration date**. Futures options and their
underlying futures contracts have distinct expiration dates which cannot always
be calculated in a straightforward manner (may be affected by holidays, and are
irregular in some products, such as ags). For example, the option code `/OZFX1`
(options 5-Year T-Note treasuries) has an underlying of `/ZFZ1` and an
expiration of `10/22/2021` (of the option itself, not of the underlying
contract).

"Mulmat" also provides a simple database of size multipliers for each product.

The local database of contracts is stored in this repository as a static file
and updated regularly by the author running the script. See commit history for
the latest updates. A script is included that can download a list of fresh
contract data from the CME website and aggregate it in the existing database, in
order to maintain data for expired contracts. Historical expirations will be
accumulated. I started this database in August 2021; prior data is not
available.

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

It also supports TOS-style expirations with the decade, e.g., `LOX21` and a
leading slash, e.g. `/R3EX1`. (This is relevant because it's really that
particular platform which is not providing us with this information in the first
place other than it being rendered in the UI which uses decades in the contract
names.)

## License

This project is under the Apache license.

## Credits

Author: Martin Blais <blais@furius.ca>

(Note: The project is named as such as a token of appreciation of Pete Mulmat, a
futures expert previously at the CME and currently a commentator on futures
markets and show host on the Tastytrade network.)
