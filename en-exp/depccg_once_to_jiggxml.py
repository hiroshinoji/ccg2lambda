#!/usr/bin/env python

'''This script is highly hard-coded for internal use in
'depccg_once_to_jiggxml' task in exp.py

Input: depccg_xml (one file) and easysrl_xmls
Output: jigg xml separated by each problem
'''

import sys
from lxml import etree
import re
import tempfile
import subprocess

def clean_category(depccg_tree):
    def clean(a):
        cat = a['cat']
        if cat[0] == '(' and cat[-1] == ')':
            a['cat'] = cat[1:-1]

    lfs = depccg_tree.findall('.//lf')
    rules = depccg_tree.findall('.//rule')

    for lf in lfs:
        clean(lf.attrib)
    for rule in rules:
        clean(rule.attrib)
    return depccg_tree

# depccg_tree has, e.g.,
# <lf start="0" span="1" word="An" lemma="An" pos="DT" chunk="I-NP" entity="O" cat="(NP/N)" />
# where lemma and pos are not correctly annotated. We fix this.
def annotate(depccg_tree, jigg_sentence):
    # depccg_tree = clean_category(depccg_tree)
    lfs = depccg_tree.findall('.//lf')
    tokens = jigg_sentence.findall('.//token')
    assert(len(lfs) == len(tokens))
    for (lf, token) in zip(lfs, tokens):
        a = lf.attrib
        a['lemma'] = token.attrib['base']
        a['pos'] = token.attrib['pos']
        # del a['start']
        # del a['span']
    return depccg_tree

def output(depccg_trees, problem_name, tagger, encoding):
    candc = etree.Element('candc')
    for t in depccg_trees:
        candc.append(t)
    result = etree.tostring(
        candc, xml_declaration=True, encoding=encoding, pretty_print=True)

    tgt = 'jiggxml/depccg/{}-taggedby-{}.xml'.format(problem_name, tagger)

    tmp = tempfile.NamedTemporaryFile()
    tmp.write(result.decode('utf-8'))
    tmp.flush()

    # subprocess.check_call(
    #     'python ../en/candc2transccg.py {} | \
    #     python reattach_period_to_root.py > {}'.format(tmp.name, tgt), shell=True)
    subprocess.check_call(
        'python ../../ccg2lambda-gitlab/candc2transccg.py {} > {}'.format(tmp.name, tgt), shell=True)

    # with open(tgt, 'w') as o:
    #     o.write(result.decode('utf-8'))

depccg_xml = sys.argv[1]
easysrl_xmls = sys.argv[2:]

parser = etree.XMLParser(remove_blank_text=True)

depccg_tree = etree.parse(depccg_xml, parser)
depccg_trees = depccg_tree.getroot().findall('ccg')
easysrl_tree_list = [etree.parse(path, parser) for path in easysrl_xmls]

encoding = depccg_tree.docinfo.encoding

easysrl_sentences_list = [tree.getroot().findall('.//sentence')
                          for tree in easysrl_tree_list]

sentence_offset = 0

for (easysrl_xml_path, easysrl_sentences) in zip(easysrl_xmls, easysrl_sentences_list):
    # Each easysrl_xml_path has a structure
    # jiggxml/easysrl/{problem_name}-taggedby-{tagger}.xml
    # We extract {problem_name} and {tagger}
    r = re.compile('([^/]*)-taggedby-(.*).xml')
    m = r.search(easysrl_xml_path)
    problem_name = m.group(1)
    tagger = m.group(2)

    depccg_slice = depccg_trees[sentence_offset:sentence_offset+len(easysrl_sentences)]

    # We annotate each tree in depccg_slice with corresponding (jiggxml) sentence
    depccg_slice = [annotate(dctree, sentence)
                    for (dctree, sentence) in zip(depccg_slice, easysrl_sentences)]

    output(depccg_slice, problem_name, tagger, encoding)

    sentence_offset += len(easysrl_sentences)
