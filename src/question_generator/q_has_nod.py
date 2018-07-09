import random
import sys
import json

def _read_templates(fn):
    if not fn.is_file():
        print("[file error]", fn, "is not found.")
        sys.exit()
    f = fn.open("r")
    jsonData = json.load(f)
    f.close()

    return jsonData


def has_nod_q_generator(post, si, thread_title,fn):
    templates = _read_templates(fn)
    select_template = random.choice(only_nod_template_with_premise)

    claim_s = post.sentences[si].body

    if si > 1:
        if post.sentences[si - 1].tag == "PREMISE":
            premise_s = post.sentences[si - 1].body
            return select_template.replace("<title>", thread_title).replace("<s1>", premise_s).replace("<s2>", claim_s)
    elif len(post.sentences) > si + 2:
        if post.sentences[si + 1].tag == "PREMISE":
            premise_s = post.sentences[si + 1].body
            return select_template.replace("<title>", thread_title).replace("<s1>", claim_s).replace("<s2>", premise_s)

    return select_template.replace("<title>", thread_title).replace("<s1>", claim_s).replace("<s2>", "")
