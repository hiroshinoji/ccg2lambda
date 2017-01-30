#!/bin/sh

# Input: untokenized text
# Output: CoNLL-X format with only POS tags

syntaxnet=../parser/models/syntaxnet
parser=bazel-bin/syntaxnet/parser_eval
model_base=syntaxnet/models/parsey_mcparseface
context=$model_base/context.pbtxt
model=$model_base/tagger-params

eval "$(pyenv init -)"
export PYENV_VERSION=2.7.13

cd $syntaxnet
$parser --input=stdin --output=stdout-conll --hidden_layer_sizes=64 --arg_prefix=brain_tagger --graph_builder=structured --task_context=$context --model_path=$model --slim_mode --batch_size=1024 --alsologtostderr
