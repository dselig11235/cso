#!/usr/bin/python

from cso import CSO
from sys import argv
import os
from interactive import *
from time import sleep
from optparse import OptionParser

usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option('-f', '--format', help="Title format string")
(options, args) = parser.parse_args()

c = CSO()
c.start()
prompt("Navigate to client file repository")
for f in args:
    print_status("Adding File '{}'".format(f))
    try:
        if options.format is not None:
            c.addFileToRepo(f, title_fmt = options.format)
        else:
            c.addFileToRepo(f)
        sleep(3)
    except:
        print_status("Failed to add file '{}'".format(f))
        raise
        prompt("Navigate to client file repository")
c.close()
