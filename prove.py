#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Copyright 2015 Pascual Martinez-Gomez
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import print_function

import argparse
import logging
from lxml import etree
import os
import sys
import textwrap

from abduction_tools import create_abduction_mechanism
from semantic_tools import prove_doc
from visualization_tools import convert_doc_to_mathml

def main(args = None):
    DESCRIPTION=textwrap.dedent("""\
            categories_template.yaml should contain the semantic templates
              in YAML format.
            parsed_sentence.xml contains the parsed sentences. All CCG trees correspond
            to the premises, except the last one, which is the hypothesis.
            If --arbi-types flag is specified, then the arbitrary specification of
            coq_types is enabled. Thus, semantic rule assignments should contain a
            a field such as:
            - semantics: \P x.P(x)
              category: NP
              coq_type: Animal
            If --auto-types is enabled, or no flag is specified, then the automatic
            inference of types is enabled. This automatic inference relies on the naive
            implementation in the sem/logic module of NLTK.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("sem")
    parser.add_argument("--abduction", nargs='?', type=str, default="coq")
    parser.add_argument("--gold_trees", action="store_true", default=False)
    args = parser.parse_args()
      
    if not os.path.exists(args.sem):
        print('File does not exist: {0}'.format(args.expression_templates_filename))
    abduction = create_abduction_mechanism(args.abduction)

    logging.basicConfig(level=logging.WARNING)

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(args.sem, parser)

    inference_result, coq_scripts = prove_doc(doc, abduction)
    print(inference_result, file=sys.stdout)
    html_str = convert_doc_to_mathml(doc, coq_scripts)
    print(html_str, file=sys.stderr)

if __name__ == '__main__':
    main()
