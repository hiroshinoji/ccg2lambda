#!/usr/bin/env python

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
    return unescape(items[1])

for sentence in sentences:
    print(' '.join([make_t(t) for t in sentence]))

