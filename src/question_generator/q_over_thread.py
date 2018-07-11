import sys
import random
from collections import defaultdict
import simplejson as json


def _read_templates(fn):
    if not fn.is_file():
        print("[file error]", fn, "is not found.")
        sys.exit()
    f = fn.open("r")
    jsonData = json.load(f)
    f.close()

    return jsonData

def over_thread_q_generator(taget, THREAD):
    print("a")