#!/usr/bin/env python

# Input: tokenized text (by tokenize.pl)
# Output: CoNLL-X format with only POS tags

import sys, subprocess

tagger = '../parser/candc-1.00/bin/pos'
model = '../parser/candc-1.00/models/pos'

# This is arguably imperfect but (actually) fracas does not contain bracket tokens.
def escape(token):
    if token == '(': return '-LRB-'
    elif token == ')': return '-RRB-'
    else: return token

p = subprocess.Popen(
    '{} --model {} 2> /dev/null'.format(tagger, model),
    shell=True,
    stdin=sys.stdin,
    stdout=subprocess.PIPE)

output = p.communicate()[0].decode('utf-8')

for sentence in output.split('\n'):
    sentence = sentence.strip()
    if not sentence: continue
    for i, token in enumerate(sentence.split(' ')):
        token = token.split('|')
        print("{}\t{}\t_\t_\t{}\t_\t_\t_".format(i, escape(token[0]), token[1]))
    print()
