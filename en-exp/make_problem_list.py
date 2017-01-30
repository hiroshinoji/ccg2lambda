#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Usage: python make_problem_list.py < fracas.xml > problem_list.txt
"""

import os

os.sys.path.insert(0, '../en')
from extract_entailment_problems import *

xml_tree = etree.parse(sys.stdin).getroot()

for problem in get_fracas_problems(xml_tree):
    if problem.problem_id != 'unknown':
        print('{:03d}_{}.json'.format(int(problem.problem_id), problem.section_name))
