#!/usr/bin/env make
#
# Simple makefile I use for long-term maintenance and update of the CME mappings.
#

OLD=$(PWD)/data/cme-expirations.csv
NEW=$(PWD)/data/cme-expirations-new.csv

# Update the local CSV database to a temporary file.
update-db:
	mulmat-update-db $(OLD) $(NEW)

# Visually inspect the differences/updates.
diff:
	xxdiff $(OLD) $(NEW)

# Commit the temporary file to the main database.
clobber:
	mv $(NEW) $(OLD)

# Regenerate Python mappings from the CSV database.
update-py:
	mulmat-update-py --database=$(OLD)
