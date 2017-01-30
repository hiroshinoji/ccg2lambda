#!/usr/bin/env python

import sys
import re

templates_path = sys.argv[1]
gold_path = sys.argv[2]
results_path = sys.argv[3]

# results maybe 'result/{parser}-taggedby-{tagger}.results'
# each line may be 'fracas_001_generalized_quantifiers single yes'
# we will reconstruct html path from these information

# problem may be '001_generalized_quantifiers'
# return '{parser}/html/001_generalized_quantifiers-taggedby-{tagger}.html'
def problem_to_html(problem, parser, tagger):
    return '{}/html/{}-taggedby-{}.html'.format(parser, problem, tagger)

header = """<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Evaluation results of %s</title>
  <style>
    body {
      font-size: 2em;
    }
  </style>
</head>
<body>
<table border='1'>
<tr>
  <td>fracas problem</td>
  <td>gold answer</td>
  <td>system answer</td>
</tr>""" % (templates_path)

footer = """</body>
</html>
"""

r = re.compile('/([^/]*)-taggedby-(.*).results')
m = r.search(results_path)
parser = m.group(1)
tagger = m.group(2)

red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"
white_color="rgb(255,255,255)"
gray_color="rgb(136,136,136)"

results = [line for line in open(results_path)]
golds = [line for line in open(gold_path)]
body = []

for (result, gold) in zip(results, golds):
    result = result.strip().split(' ')
    gold = gold.strip().split(' ')
    if not result:
        assert(not gold)
        continue
    problem_name = result[0][7:] # remove fracas_
    if len(result) < 3:
        system_answer = ""
    else:
        system_answer = result[2]
    gold_answer = gold[2]

    if gold_answer == "yes" or gold_answer == "no":
        if gold_answer == system_answer:
            color = green_color
        else:
            color = red_color
    elif system_answer == "unknown" or system_answer == "undef":
        color = gray_color
    else:
        color = white_color

    html = problem_to_html(problem_name, parser, tagger)
    body.append("""<tr>
    <td><a style="background-color:{};" href="{}">{}</a></td>
    <td>{}</td>
    <td>{}</td>
    </tr>""".format(color, html, result[0], gold_answer, system_answer))

o = [header] + body + [footer]
print('\n'.join(o))
