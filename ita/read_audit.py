#!/usr/bin/python

from cso import CSO
from sys import argv, stdout
import os
from interactive import *
from time import sleep
from optparse import OptionParser
import csv

def usage():
    raise Exception("read_report <output filename>")

if len(argv) < 2:
    usage()
c = CSO()
c.start()
prompt('Navigate to client "Analyze Vulnerabilities" section and click on first control in Sequential Answer Mode')
data = c.getAllControls()
c.close()

fieldnames = [
            'asset', 'control', 'verification', 'resources', 'observation',
            'recommendation', 'date', 'method', 'source'
        ]

recoded = []
for d in data:
    datum = {}
    for k,v in d.iteritems():
        datum[k] = v.encode('utf8')
    recoded.append(datum)

with open(argv[1], 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for d in recoded:
        writer.writerow(d)
