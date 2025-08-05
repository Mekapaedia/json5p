#!/usr/bin/env python3

import sys
import os
import re
from lark import Lark, Transformer, v_args

class ProtoDef:
    def __init__(self, key):
        self.key = key

class Undefined:
    pass

include_re = re.compile(r"(\$include\s*[\"']?([$a-zA-Z\._\-0-9/]+)[\"']?)")
json5p_grammar = None
with open("json5p.lark") as f:
    json5p_grammar = f.read()
parser = Lark(json5p_grammar)


class TreeToJson(Transformer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.refs = {}

    def start(self, s):
        return s[0]

    def string(self, s):
        return s[0]

    def quoted(self, s):
        return bytes(s[0].value[1:-1], "utf-8").decode("unicode_escape")

    def cname(self, s):
        return s[0].value

    def pair(self, s):
        key = s[0]
        value = s[1]
        if isinstance(key, ProtoDef):
            self.refs[key.key] = value
            return None
        return (key, value)

    def proto(self, s):
        return ProtoDef(s[0])

    def null(self, s):
        return None

    def true(self, s):
        return True

    def false(self, s):
        return False

    def undefined(self, s):
        return Undefined

    def number(self, s):
        s = s[0]
        if s.type == "SIGNED_NUMBER":
            try:
                s = int(s.value)
            except ValueError:
                s = float(s.value)
        elif s.type == "HEX_NUMBER":
            s = int(s.value, 16)
        elif s.type == "OCT_NUMBER":
            s = int(s.value, 8)
        elif s.type == "BIN_NUMBER":
            s = int(s.value, 2)
        return s

    def object(self, s):
        return s[0]

    def object_inner(self, s):
        s = [x for x in s if x is not None]
        return dict(s)

    def array(self, s):
        return list(s)

    def set_ref(self, s):
        self.refs[s[0]] = s[1]
        return s[1]

    def value(self, s):
        return s[0]

    def use_ref(self, s):
        ret  = self.refs[s[0]]
        if len(s) > 1:
            val = s[1]
            if isinstance(val, dict):
                ret = {**ret, **val}
            else:
                ret = val
        if ret is Undefined:
            raise Exception("Value is undefined")
        if isinstance(ret, dict):
            for key, val in ret.items():
                if val is Undefined:
                    raise Exception("Key {} is undefined".format(key))
        return ret


input_text = None
input_file_path = sys.argv[1]
input_file_dir = os.path.dirname(input_file_path)
with open(input_file_path) as f:
    input_text = f.read()
includes = include_re.findall(input_text)
while includes:
    for include in includes:
        include_path = include[1].replace("$dir", input_file_dir)
        include_text = None
        with open(include_path) as f:
            include_text = f.read()
        input_text = input_text.replace(include[0], include_text)
    includes = include_re.findall(input_text)
parse = parser.parse(input_text)
parse.pretty()
print(TreeToJson().transform(parse))
