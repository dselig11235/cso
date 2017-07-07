#!/usr/bin/python
from sys import argv
from cso import CSO

if len(argv) < 2:
    print 'Usage: scan2top COMPANY'
    exit(1)
c = CSO()
c.start()
c.moveToTop(argv[1])
c.driver.close()
