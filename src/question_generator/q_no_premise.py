import sys
import simplejson as json
import random

import mynlp


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
    return r_msg.replace("<s>", sbody)


# くっつける条件
def _bond_last_word(p_phs, si):
    b_phs = p_phs[si]
    b_last_ph_i = max(list(b_phs.keys()))
    b_ph = b_phs[b_last_ph_i]
    b_last_word = b_ph.words[-1]
    if b_last_word.pos_detail == "句点":
        return False
    if b_last_word.pos_detail == "接続助詞":
        return True
    if b_last_word.pos_detail == "読点":
        return True

    t_phs = p_phs[si + 1]
    if len(t_phs) < 3:
        return True

    return False


def _check_bond(pi, post, target_si, f_mrph):
    p_phs = mynlp.read_mrph_per_post(f_mrph, pi)
    bond_si_list = []

    # 前の文のチェック
    before_si = target_si - 1
    while before_si > -1:
        if _bond_last_word(p_phs, before_si):
            bond_si_list.append(before_si)
        else:
            break
        before_si -= 1

    # 対象の文
    bond_si_list.append(target_si)

    # 後ろの文のチェック
    s_num = len(post.sentences)
    after_si = target_si + 1
    while after_si < (s_num - 1):
        if _bond_last_word(p_phs, after_si):
            bond_si_list.append(after_si)
        else:
            break
        after_si -= 1
    return bond_si_list.sort()


def no_premise_q_generator(post, pi, s, si, fn_templates, fn_mrph):
    # 前提が多すぎる場合
    if s.has_premise > 1:
        return None

    si_list = _check_bond(pi, post, si, fn_mrph)
    sbodys = ""
    for si in si_list:
        sbodys += post.sentences[si].body

    return _make_rmsg(sbodys, fn_templates)
