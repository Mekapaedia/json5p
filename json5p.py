#!/usr/bin/env python3

import sys
from lark import Lark


json5p_grammar = None
with open("json5p.lark") as f:
    json5p_grammar = f.read()
parser = Lark(json5p_grammar)

input_file = "basic.j5p"

input_text = None
with open(input_file) as f:
    input_text = f.read()

print(parser.parse(input_text).pretty())
if len(sys.argv) > 1:
    input_text = None
    with open(sys.argv[1]) as f:
        input_text = f.read()
    print(parser.parse(input_text).pretty())
