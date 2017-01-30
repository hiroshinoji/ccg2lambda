#!/usr/bin/env python

import sys
import json

paths = sys.stdin.read().strip().split(' ')

def get_name(path):
    f = path[path.rfind('/')+1:] # plain/aaa.json -> aaa.json
    return f[:-5] # aaa.json -> aaa

for path in paths:
    j = json.load(open(path), encoding='utf-8')
    name = get_name(path)
    num_lines = len(j['tokenized'].strip().split('\n'))
    if num_lines > 2:
        premises = "multi"
    else:
        premises = "single"
    print('fracas_{} {} {}'.format(name, premises, j['answer']))
