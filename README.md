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
that can download a list of future contracts from the CME website.

The Python library provides simple indexing into this library. The list of
contracts updated in the local database by default are those commonly available
in retail platforms, but the code supports any product. If you'd like to me to
add more to the list, please send email.

## Usage

Some retail platforms only provide futures options codes and one cannot
thereafter determine the expiration date for that contract. This is intended to
make it easy to do this mapping and maintain a database of it.

## License

This project is under the Apache license.

## Credits

Author: Martin Blais <blais@furius.ca>
