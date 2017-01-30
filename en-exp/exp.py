#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os, sys
import logging
import itertools
import json
from runexp import Workflow

os.sys.path.insert(0, '../en')
from extract_entailment_problems import *

logger = logging.getLogger(__name__)

fracas_xml = '../fracas.xml'
easyccg_dir = '../parser/easyccg-0.2'
easysrl_dir = '../parser/EasySRL'
depccg_dir = '../parser/depccg/src'
# category_templates = '../en/semantic_templates_en_emnlp2015.yaml'
# category_templates = '../en/semantic_templates_en_event.yaml'
category_templates = '../../ccg2lambda-gitlab/semantic_templates_en_event.yaml'
# category_templates = '../en/semantic_templates_en_event-dts.yaml'
# coqlib = 'en/coqlib_fracas.v'
coqlib = '../ccg2lambda-gitlab/coqlib_en.v'
# coqlib = 'en/coqlib_sick.v'
# tactic = 'en/tactics_coq_en.txt'
tactic = 'ja/tactics_coq_ja.txt'
# tactic = 'en/tactics_coq_fracas.txt'

def get_problem_names():
    xml_tree = etree.parse(fracas_xml).getroot()
    problems = [problem for problem in get_fracas_problems(xml_tree) \
                if problem.problem_id != 'unknown']
    def name(problem):
        return '{:03d}_{}'.format(int(problem.problem_id), problem.section_name)
    return [name(problem) for problem in problems]

# def mk_problem_name(problem):
#     return '{:03d}_{}'.format(int(problem.problem_id), problem.section_name)

# def mk_problem_names(problems):
#     return [mk_problem_name(problem) for problem in problems]

def problem_list(task):
    task(name = 'problem_list',
         rule = 'python make_problem_list.py < {} > {}'.format(
             fracas_xml,
             'fracas_problem_list.txt'),
         target = 'fracas_problem_list.txt')

# # Extract all datasets from fracas.xml.
# # Each dataset becomes one json file.
def tokenize(task, problem_names):
    if not os.path.isdir('./plain'):
        os.makedirs('./plain')
    for problem_name in problem_names:
        tgt = 'plain/{}.json'.format(problem_name)
        task(name = 'tokenize-{}'.format(problem_name),
             rule = 'python problem_to_json.py {} < {} > {}'.format(
                 problem_name, fracas_xml, tgt),
             target = tgt)

def tagging_syntaxnet(task, problem_names):
    if not os.path.isdir('./tagged'):
        os.makedirs('./tagged')
    for problem_name in problem_names:
        src = 'plain/{}.json'.format(problem_name)
        tgt = 'tagged/{}-syntaxnet.conll'.format(problem_name)
        task(name = 'tagging-syntaxnet-{}'.format(problem_name),
             rule = 'cat {} | \
             python json_to_raw.py | \
             run_syntaxnet.sh > {} 2>/dev/null'.format(src, tgt),
             source = src,
             target = tgt)

def tagging_candc(task, problem_names):
    if not os.path.isdir('./tagged'):
        os.makedirs('./tagged')
    for problem_name in problem_names:
        src = 'plain/{}.json'.format(problem_name)
        tgt = 'tagged/{}-candc.conll'.format(problem_name)
        task(name = 'tagging-candc-{}'.format(problem_name),
             rule = 'cat {} | \
             python json_to_tokenized.py | \
             run_candc_pos.py > {}'.format(src, tgt),
             source = src,
             target = tgt)

def parse_easyccg(task, problem_names):
    if not os.path.isdir('./easyccg'):
        os.makedirs('./easyccg')
    taggers = ['candc', 'syntaxnet']
    for problem_name in problem_names:
        for tagger in taggers:
            src = 'tagged/{}-{}.conll'.format(problem_name, tagger)
            tgt = 'easyccg/{}-taggedby-{}.auto'.format(problem_name, tagger)
            task(name = 'parse-easyccg-{}-from-{}'.format(problem_name, tagger),
                 rule = 'cat {} | \
                 python conll_to_easyccg_input.py | \
                 java -jar {}/easyccg.jar \
                 --model {}/model \
                 -i POSandNERtagged \
                 -o extended \
                 --nbest 1 \
                 > {} 2> /dev/null'.format(src, easyccg_dir, easyccg_dir, tgt),
                 source = src,
                 target = tgt)

def parse_easysrl(task, problem_names):
    if not os.path.isdir('./easysrl/log'):
        os.makedirs('./easysrl/log')
    taggers = ['candc', 'syntaxnet']
    model = 'lstm_tritrain_finetune'
    for problem_name in problem_names:
        for tagger in taggers:
            src = os.path.abspath(
                'tagged/{}-{}.conll'.format(problem_name, tagger))
            tgt = os.path.abspath(
                'easysrl/{}-taggedby-{}.auto'.format(problem_name, tagger))
            log = os.path.abspath(
                'easysrl/log/{}-taggedby-{}.log'.format(problem_name, tagger))
            script = os.path.abspath('./conll_to_easyccg_input.py')
            task(name = 'parse-easysrl-{}-from-{}'.format(problem_name, tagger),
                 rule = 'cd {} && cat {} | \
                 python {} | \
                 java -jar easysrl.jar \
                 --model {} \
                 -i POSandNERtagged \
                 -o extended \
                 > {} 2> {}'.format(easysrl_dir, src, script, model, tgt, log),
                 source = src,
                 target = tgt)

# We use the tokenization given by syntaxnet (or lemmatizer.pl for candc)
def parse_depccg(task, problem_names, taggers=['syntaxnet']):
    if not os.path.isdir('./depccg/log'):
        os.makedirs('./depccg/log')
    model = 'py/lstm_425dep_4layer'
    abp = os.path.abspath
    for tagger in taggers:
        for problem_name in problem_names:
            src = 'tagged/{}-{}.conll'.format(problem_name, tagger)
            tgt = 'depccg/{}-taggedby-{}.xml'.format(problem_name, tagger)
            log = 'depccg/log/{}-taggedby-{}.xml.log'.format(problem_name, tagger)
            script = './conll_to_raw.py'
            task(name = 'depccg-{}-{}'.format(problem_name, tagger),
                 rule = 'cd {} && cat {} | \
                 python {} | \
                 myccg \
                 -m py/lstm_425dep_4layer \
                 -l en \
                 -f xml \
                 --dep > {}'.format(
                     depccg_dir, abp(src), abp(script), abp(tgt)),
                 source = src,
                 target = tgt)

def parse_depccg_once(task, problem_names, taggers=['syntaxnet']):
    if not os.path.isdir('./depccg'):
        os.makedirs('./depccg')
    model = 'py/lstm_425dep_4layer'
    abp = os.path.abspath
    for tagger in taggers:
        src = ['tagged/{}-{}.conll'.format(name, tagger) for name in problem_names]
        srcstr = 'tagged/*-{}.conll'.format(tagger)
        tgt = 'depccg/all-taggedby-{}.xml'.format(tagger)
        script = './conll_to_raw.py'
        task(name = 'depccg-once-{}'.format(tagger),
             rule = 'cd {} && cat {} | \
             python {} | \
             myccg \
             -m py/lstm_425dep_4layer \
             -l en \
             -f xml \
             --dep > {}'.format(depccg_dir, abp(srcstr), abp(script), abp(tgt)),
             source = src,
             target = tgt)

# We assume parse with 'easysrl' is done prior to this task
def depccg_once_to_jiggxml(task, problem_names, taggers=['syntaxnet']):
    tgt_dir = './jiggxml/depccg'
    if not os.path.isdir(tgt_dir):
        os.makedirs('{}'.format(tgt_dir))
    for tagger in taggers:
        easysrl_xmls = ['jiggxml/easysrl/{}-taggedby-{}.xml'.format(name, tagger)
                        for name in problem_names]
        depccg_xml = 'depccg/all-taggedby-{}.xml'.format(tagger)
        tgt = ['{}/{}-taggedby-{}.xml'.format(tgt_dir, name, tagger)
               for name in problem_names]
        task(name = 'depccg-once-to-jigg-{}'.format(tagger),
             rule = 'python depccg_once_to_jiggxml.py {} {}'.format(
                 depccg_xml, ' '.join(easysrl_xmls)),
             source = [depccg_xml] + easysrl_xmls,
             target = tgt)

# parser is either 'easyccg' or 'easysrl'
def easyccg_to_jiggxml(task, problem_names, parser, reattach=False):
    tgt_dir = './jiggxml/{}'.format(parser)
    if not os.path.isdir(tgt_dir):
        os.makedirs("{}/log".format(tgt_dir))
    taggers = ['candc', 'syntaxnet']
    for problem_name in problem_names:
        for tagger in taggers:
            src = '{}/{}-taggedby-{}.auto'.format(parser, problem_name, tagger)
            tgt = '{}/{}-taggedby-{}.xml'.format(tgt_dir, problem_name, tagger)
            log = '{}/log/{}.xml.log'.format(tgt_dir, problem_name)

            if reattach:
                rule = 'python3 my_easyccg2jigg.py {} | \
                python reattach_period_to_root.py > {} 2> {}'.format(src, tgt, log)
            else:
                rule = 'python3 my_easyccg2jigg.py {} > {} 2> {}'.format(src, tgt, log)
            task(name = '{}-parse-{}-tag-{}-to-jigg'.format(problem_name, parser, tagger),
                 rule = rule,
                 source = src,
                 target = tgt)

def semparse(task, problem_names, parser, taggers = ['candc', 'syntaxnet']):
    tgt_dir = './semparse/{}'.format(parser)
    if not os.path.isdir(tgt_dir):
        os.makedirs("{}/log".format(tgt_dir))
    for problem_name in problem_names:
        for tagger in taggers:
            src = './jiggxml/{}/{}-taggedby-{}.xml'.format(parser, problem_name, tagger)
            tgt = '{}/{}-taggedby-{}.sem.xml'.format(tgt_dir, problem_name, tagger)
            log = '{}/log/{}.sem.xml.log'.format(tgt_dir, problem_name)
            task(name = 'semparse-{}-parse-{}-tag-{}'.format(problem_name, parser, tagger),
                 rule = 'python3 ../scripts/semparse.py \
                 {} {} {} --arbi-types 2> {}'.format(src, category_templates, tgt, log),
                 source = src,
                 target = tgt)

def result(task, problem_names, parser, taggers = ['candc', 'syntaxnet']):
    tgt_dir = './result/{}'.format(parser)
    if not os.path.isdir(tgt_dir):
        os.makedirs("{}/answer/log".format(tgt_dir))
        os.makedirs("{}/html".format(tgt_dir))

    abp = os.path.abspath
    for i, problem_name in enumerate(problem_names):
        for tagger in taggers:
            src = './semparse/{}/{}-taggedby-{}.sem.xml'.format(
                parser, problem_name, tagger)
            tgt = [
                '{}/answer/{}-taggedby-{}.answer'.format(tgt_dir, problem_name, tagger),
                '{}/html/{}-taggedby-{}.html'.format(tgt_dir, problem_name, tagger)]
            log = '{}/answer/log/{}-taggedby-{}.answer.log'.format(
                tgt_dir, problem_name, tagger)
            task(name = 'answer-{}-{}-{}'.format(i, parser, tagger),
                 rule = './error_agnostic_prove.sh {} {} {} {} > {}'.format(
                     problem_name, abp(src), abp(tgt[1]), abp(log), abp(tgt[0])),
                 source = src,
                 target = tgt[0]) # tgt[1] may not be created when error occurs

def aggregate_result(task, problem_names, parser, taggers = ['candc', 'syntaxnet']):
    for tagger in taggers:
        src = ['./result/{}/answer/{}-taggedby-{}.answer'.
               format(parser, problem, tagger) for problem in problem_names]
        tgt = './result/{}-taggedby-{}.results'.format(parser, tagger)
        task(name = 'aggregate-{}-{}'.format(parser, tagger),
             rule = 'cat {} > {}'.format(' '.join(src), tgt),
             source = src,
             target = tgt)

def aggregate_gold(task, problem_names):
    src = ['plain/{}.json'.format(name) for name in problem_names]
    tgt = 'gold.results'
    task(name = 'aggregate-gold',
         rule = 'echo {} | python aggregate-gold.py > {}'.format(' '.join(src), tgt),
         source = src,
         target = tgt)

def calc_score(task, parser, taggers = ['candc', 'syntaxnet']):
    for tagger in taggers:
        src = ['./result/{}-taggedby-{}.results'.format(parser, tagger),
               'gold.results']
        tgt = './result/{}-taggedby-{}.score'.format(parser, tagger)
        task(name = 'score-{}-{}'.format(parser, tagger),
             rule = 'python ../en/report_results.py {} {} > {}'.format(src[1], src[0], tgt),
             source = src,
             target = tgt)

def main_html(task, parser, taggers = ['candc', 'syntaxnet']):
    for tagger in taggers:
        src = ['gold.results',
               'result/{}-taggedby-{}.results'.format(parser, tagger)]
        tgt = './result/{}-taggedby-{}-main.html'.format(parser, tagger)
        task(name = 'html-{}-{}'.format(parser, tagger),
             rule = 'python export_main_html.py {} {} {} > {}'.format(category_templates, src[0], src[1], tgt),
             source = src,
             target = tgt)

def prepare_coq(task):
    task(name = 'prepare coq',
        rule = 'cd .. && cp {} coqlib.v && coqc coqlib.v && cp {} tactics_coq.txt'.format(coqlib, tactic),
        always = True)

def semparse_to_output(task, problem_names, parser, taggers):
    semparse(exp, problem_names, parser, taggers)
    result(exp, problem_names, parser, taggers)
    aggregate_result(exp, problem_names, parser, taggers)
    calc_score(exp, parser, taggers)
    main_html(exp, parser, taggers)

def easyccg_experiment(task, problems, parser):
    if parser == 'easyccg':
        parse_easyccg(task, problem_names)
    elif parser == 'easysrl':
        parse_easysrl(task, problem_names)
    # easyccg_to_jiggxml(exp, problem_names, parser, reattach=True)
    easyccg_to_jiggxml(task, problem_names, parser, reattach=False)
    semparse_to_output(task, problem_names, parser, taggers=['candc', 'syntaxnet'])

def depccg_experiment(task, problem_names):
    parse_depccg_once(task, problem_names)
    depccg_once_to_jiggxml(task, problem_names)
    semparse_to_output(task, problem_names, 'depccg', taggers=['syntaxnet'])

logger.debug('set tasks')
exp = Workflow()

prepare_coq(exp)

problem_names = get_problem_names()

# tokenize(exp, problem_names)
# tagging_syntaxnet(exp, problem_names)
# tagging_candc(exp, problem_names)

# aggregate_gold(exp, problem_names)

# easyccg_experiment(exp, problem_names, 'easyccg')
# easyccg_experiment(exp, problem_names, 'easysrl')
depccg_experiment(exp, problem_names)

logger.debug('run tasks')
if not exp.run():
    sys.exit(1)
