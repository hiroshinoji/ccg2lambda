#!/usr/bin/env python

import json, sys

input = json.load(sys.stdin, encoding='utf-8')
print(input['tokenized'])
