#!/usr/bin/env make

update:
	mulmat-update $(PWD)/data/cme-expirations.csv $(PWD)/data/cme-expirations-new.csv
