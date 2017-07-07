#!/usr/bin/python


from TraceNmapParser import NmapParser
from sys import argv
from json import dumps
import os,csv,re


echoes = []
with open(argv[1]) as f:
    for ln in f:
        m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ln)
        if m:
            echoes.append(m.group(1))

if(argv[2] == "-t"):
    type=argv[3]
    files = argv[4:]
else:
    type="gnmap"
    files = argv[2:]

path = os.path.dirname(os.path.realpath(__file__))
parser = NmapParser()
parser.open(files, type)
dataStr = dumps(parser.data)
uniqueIps = set(x[0] for x in parser.data)
with open(os.path.join(path, 'addPorts.js'), 'r') as f:
    funcStr = f.read()
print '{} addPorts({})'.format(funcStr, dataStr)

dataStr = dumps([x for x in uniqueIps])
echoesStr = dumps(echoes)
with open(os.path.join(path, 'addICMP.js'), 'r') as f:
    funcStr = f.read()
print '{} addICMP({}, {})'.format(funcStr, dataStr, echoesStr)
