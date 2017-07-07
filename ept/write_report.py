#!/usr/bin/python

import os
from cso import CSO
from ps import popsummary
from interactive import *
from time import sleep

c = CSO()
c.start()
w = os.environ['WORKDIR']
vdirs = [os.path.join(w, 'vuln', v) for v in os.listdir(os.path.join(w, 'vuln'))]
prompt("Navigate to report vulnerabilites tab")
for v in vdirs:
    c.addVulnerability(v)
    sleep(2)
prompt("Navigate to 'Summaries' tab")
with open(os.path.join(w, 'appendix')) as f:
    for file in f:
        c.addAppendixFigure(file.strip())
ls = os.listdir(os.path.join(w, 'combined'))
gnmaps = [os.path.realpath(os.path.join(w, 'combined', g)) for g in ls if g[-6:] == '.gnmap']
script = popsummary(os.path.join(w, 'ICMP Echo Request.spl'), gnmaps, "gnmap")
c.driver.execute_script(script)
