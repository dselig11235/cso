#!/usr/bin/python

from cso import CSO
from sys import argv, exit
import os
from interactive import *
from time import sleep
from optparse import OptionParser

usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option('-f', '--format', help="format string for resource title. eg '2017 ITA-{title}' ({title} fills in filename) ")
parser.add_option('-d', '--driver', help='Specify firefox/chromium driver', default='firefox')
(options, args) = parser.parse_args()

if len(args) == 0:
    print parser.print_help()
    exit(1)

c = CSO(driver=options.driver)
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
