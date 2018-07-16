import simplejson as json
import mynlp


def _read_cases(fn):
    f = fn.open("r")
    jsonData = json.load(f)


def preparate_caseparticle(f_cases, f_mrph, new_post_pi_list):
    # 過去のやつを読み込む
    Caseframe_list = _read_cases(f_cases)
    for pi in new_post_pi_list:
        p_phs = mynlp.read_mrph_per_post(f_mrph, pi)


    return Caseframe_list
