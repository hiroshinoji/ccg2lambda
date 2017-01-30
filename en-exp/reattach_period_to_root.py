#!/usr/bin/env python

# Input: jiggxml
# Output: jiggxml with reattached parse tree

from lxml import etree
import sys

parser = etree.XMLParser(remove_blank_text=True)
xml_tree = etree.parse(sys.stdin, parser)

root = xml_tree.getroot()

def find_parent(child_id, spans):
    for span in spans:
        if 'child' not in span.attrib:
            continue
        childs = span.attrib['child'].split(' ')
        if child_id in childs:
            return span

def rewrite_sentence(sentence):
    ccg = sentence.find('.//ccg')
    orig_root_id = ccg.attrib['root']
    spans = ccg.findall('span')
    final = spans[-1]
    if final.attrib['category'] != '.':
        return sentence
    final_id = final.attrib['id']

    period_parent = find_parent(final_id, spans)
    period_parent_id = period_parent.attrib['id']
    if period_parent_id == orig_root_id:
        return sentence # nothing to do

    left_child_id = period_parent.attrib['child'].split(' ')[0]
    assert(left_child_id != final_id) # final_id is the right child

    period_grandparent = find_parent(period_parent_id, spans)
    grandparent_child_ids = period_grandparent.attrib['child'].split(' ')
    if grandparent_child_ids[0] == period_parent_id:
        grandparent_child_ids[0] = left_child_id
    else:
        assert(grandparent_child_ids[1] == period_parent_id)
        grandparent_child_ids[1] = left_child_id
    period_grandparent.attrib['child'] = ' '.join(grandparent_child_ids)

    old_root = [span for span in spans if span.attrib['id']==orig_root_id][0]
    new_root_span = period_parent
    a = new_root_span.attrib
    a['child'] = '{} {}'.format(orig_root_id, final_id)
    a['category'] = old_root.attrib['category']

    ccg.attrib['root'] = period_parent_id

    return sentence

sentences = root.findall('.//sentence')
for sentence in sentences:
    rewrite_sentence(sentence)

result = etree.tostring(
    xml_tree,
    xml_declaration=True,
    encoding=xml_tree.docinfo.encoding,
    pretty_print=True)
print(result.decode('utf-8'))
