#!/usr/bin/python

from cso import CSO
from sys import argv, stdin
import os
from interactive import *
from time import sleep
from optparse import OptionParser
import csv

if len(argv) > 1:
    with open(argv[1]) as f:
        reader = csv.DictReader(f)
        raw = [r for r in reader]
else:
    print "reading from stdin"
    reader = csv.DictReader(stdin)
    raw = [r for r in reader]

# Make fieldnames / dictionary keys lowercase
#XXX wish there was a better way to do this
data = []
for d in raw:
    datum = {}
    for k in d:
        datum[k.lower()] = d[k]
    data.append(datum)

c = CSO()
c.start()
prompt('Navigate to client "Analyze Vulnerabilities" section and click on first control in Sequential Answer Mode')
c.batchAddAuditData(data)
c.close()
