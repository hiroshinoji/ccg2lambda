#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, json

os.sys.path.insert(0, '../en')
from extract_entailment_problems import *

"""Usage: python problem_to_json.py 001_generalized_quantifiers < fracas.xml > 001.json
"""

def search_problem(contents, target_name):
    current_section = 'nosection'
    for node in contents:
        if node.tag == 'comment' \
           and 'class' in node.attrib \
           and node.attrib['class'] == 'section':
            current_section = normalize_section_name(node.text)
        if node.tag == 'problem':
            # Retrieve problem ID.
            problem_id = [value for key, value in node.attrib.items() if key.endswith('id')]
            assert len(problem_id) == 1, 'Problem has no ID'
            problem_id = problem_id[0]
            # Retrieve section name from phenomena, if any.
            if 'phenomena' in node.attrib:
                current_section = normalize_section_name(node.attrib['phenomena'].split(',')[0])
            problem_name = '{:03d}_{}'.format(int(problem_id), current_section)

            if problem_name != target_name: continue
            # Retrieve the first answer (there should be only one).
            answer = [value for key, value in node.attrib.items() if 'answer' in key]
            assert len(answer) <= 1, 'Multiple gold entailment answers found'
            answer = None if not answer else answer[0]
            premises = get_premises_from_node(node)
            hypothesis = get_hypothesis_from_node(node)
            sentences = premises + [hypothesis]
            # sentences = [escape_reserved_chars(s) for s in sentences]
            problem = FracasProblem(problem_id, current_section, sentences, answer)
            return problem
    raise RuntimeError("Problem {} not found.".format(target_name))


if __name__ == '__main__':
    target_name = sys.argv[1]
    xml_tree = etree.parse(sys.stdin).getroot()
    problem = search_problem(xml_tree, target_name)

    sentences = '\n'.join(problem.sentences)
    answer = problem.answer

    proc = subprocess.Popen(
        'perl ../en/tokenizer.perl -l en 2>/dev/null',
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    tokenized_sentences = proc.communicate(sentences.encode('utf-8'))[0]

    result = {
        'sentences': sentences,
        'answer': answer,
        'tokenized': tokenized_sentences.decode('utf-8')
    }
    print(json.dumps(result))
