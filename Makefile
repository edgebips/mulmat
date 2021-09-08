#!/usr/bin/env make

OLD=$(PWD)/data/cme-expirations.csv
NEW=$(PWD)/data/cme-expirations-new.csv

update update-db:
	mulmat-update-db $(OLD) $(NEW)

diff:
	xxdiff $(OLD) $(NEW)

clobber:
	mv $(NEW) $(OLD)
