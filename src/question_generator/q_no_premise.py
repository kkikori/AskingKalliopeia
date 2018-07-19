import sys
import simplejson as json
import random


def _read_templates(fn):
    if not fn.is_file():
        print("[file error]", fn, "is not found.")
        sys.exit()
    f = fn.open("r")
    jsonData = json.load(f)
    f.close()

    return jsonData


def _make_rmsg(sbody, fn_templates):
    templates = _read_templates(fn=fn_templates)
    r_msg = ""
    r_msg += random.choice(templates["cushions"])
    r_msg += random.choice(templates["templates"])
    r_msg += "\n"
    return r_msg.replace("<s>",sbody)

def no_premise_q_generator(s, fn_templates):
    if s.has_premise >1:
        return None
    return _make_rmsg(s.body, fn_templates)