#!/usr/bin/python


from TraceNmapParser import NmapParser
from sys import argv
from json import dumps
import os,csv,re


def popsummary(icmpfile, nmapfiles, nmaptype="gnmap"):
    echoes = []
    with open(icmpfile) as f:
        for ln in f:
            m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ln)
            if m:
                echoes.append(m.group(1))

    path = os.path.dirname(os.path.realpath(__file__))
    parser = NmapParser()
    parser.open(nmapfiles, nmaptype)
    dataStr = dumps(parser.data)
    uniqueIps = set(x[0] for x in parser.data)
    with open(os.path.join(path, 'addPorts.js'), 'r') as f:
        funcStr = f.read()
    output = '{} addPorts({});\n'.format(funcStr, dataStr)

    dataStr = dumps([x for x in uniqueIps])
    echoesStr = dumps(echoes)
    with open(os.path.join(path, 'addICMP.js'), 'r') as f:
        funcStr = f.read()
    output += '{} addICMP({}, {})'.format(funcStr, dataStr, echoesStr)
    return output


def main():
    if(argv[2] == "-t"):
        popsummary(argv[1], argv[4], nmaptype=argv[3])
    else:
        popsummary(argv[1], argv[2])

