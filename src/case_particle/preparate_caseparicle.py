import simplejson as json
import mynlp
from .CasepairClass import CasepairClass
from .CaseframeClass import CaseframeClass
from .extract_cp import extract_cp_and_embed_class
from .update_cases_file import update_cases_file


# クラスへの埋め込み
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


# 過去のやつを読み込む
def _read_cases(fn):
    Caseframe_list = {}
    f_lists = list(fn.glob("*.json"))
    for f in f_lists:
        new = _embed_case(f)
        Caseframe_list[new.noun] = new
    return Caseframe_list


def preparate_caseparticle(f_cases, f_mrph, Post_list, new_post_pi_list, stop_word_list):
    # 過去のやつを読み込む
    Caseframe_list = _read_cases(f_cases)

    # 新しいやつをやる
    update_nouns = set()  # 上書きする必要があるファイルリスト
    for pi in new_post_pi_list:
        p_phs = mynlp.read_mrph_per_post(f_mrph, pi)
        post = Post_list[pi]
        for si, phs in enumerate(p_phs):
            cps = extract_cp_and_embed_class(phs, post.belong_th_i, pi, si, post.user_id)
            if len(cps) == 0:
                continue
            for cp in cps:
                if cp["noun"] in stop_word_list:
                    continue
                if cp["noun"] not in Caseframe_list.keys():
                    Caseframe_list[cp["noun"]] = CaseframeClass(noun=cp["noun"])
                Caseframe_list[cp["noun"]].pairs.append(cp["cp"])
                update_nouns.add(cp["noun"])

    # ファイルの更新
    update_cases_file(f_cases, update_nouns, Caseframe_list)

    return Caseframe_list