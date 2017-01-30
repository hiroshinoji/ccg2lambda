#!/bin/sh

problem_name=$1
plain_json=./plain/${problem_name}.json

# function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; }

num_lines=`cat ${plain_json} | python json_to_tokenized.py | sed '/^$/d' | wc -l`
premises="single"
if [ "$num_lines" -gt 2 ]; then
    premises="multi"
fi

cd ..
coqc coqlib.v > /dev/null
ans=`timeout 100 python3 scripts/prove.py $2 --graph_out $3 --abduction 2> $4`

echo fracas_$problem_name $premises $ans

# return 0
