#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sentences = []
sentence = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        if sentence:
            sentences.append(sentence)
        sentence = []
    else:
        sentence.append(line)
if sentence:
    sentences.append(sentence)

def unescape(token):
    if token == '-LRB-': return '('
    elif token == '-RRB-': return ')'
    else: return token

def make_t(t):
    items = t.split('\t')
    return "{}|{}|O".format(unescape(items[1]), items[4])

for sentence in sentences:
    print(' '.join([make_t(t) for t in sentence]))
