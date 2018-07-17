import simplejson as json
import mynlp
from .CasepairClass import CasepairClass
from .CaseframeClass import CaseframeClass


def _embed_case(fn):
    f = fn.open("r")
    jsonData = json.load(f)
    noun = jsonData["noun"]
    newCaseframe = CaseframeClass(noun)
    for jd in jsonData["pairs"]:
        newCasepair = CasepairClass(jd["th_i"], jd["p_i"], jd["s_i"], jd["u_i"], \
                                    jd["particle"], jd["predicate"], jd["category"])
        newCaseframe.pairs.append(newCasepair)
    return newCaseframe


def _read_cases(fn):
    Caseframe_list = {}
    f_lists = list(fn.glob("*.json"))
    for f in f_lists:
        new = _embed_case(f)
        Caseframe_list[new.]



def preparate_caseparticle(f_cases, f_mrph, new_post_pi_list):
    # 過去のやつを読み込む
    Caseframe_list = _read_cases(f_cases)
    for pi in new_post_pi_list:
        p_phs = mynlp.read_mrph_per_post(f_mrph, pi)

    return Caseframe_list
