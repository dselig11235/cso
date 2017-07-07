#!/usr/bin/python

from cso import CSO
from sys import argv
import os
from interactive import *
from time import sleep

c = CSO()
c.start()
prompt("Navigate to client file repository")
for f in argv[1:]:
    print_status("Adding File '{}'".format(f))
    try:
        c.addFileToRepo(f)
        sleep(3)
    except:
        print_status("Failed to add file '{}'".format(f))
        prompt("Navigate to client file repository")
c.close()
