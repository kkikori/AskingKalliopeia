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
# siの文に対して前の文をくっつける場合はTrue、そうじゃない場合はFalseを返す
def _bond_last_word(p_phs, si):
    b_phs = p_phs[si-1]
    b_last_ph_i = max(list(b_phs.keys()))
    b_ph = b_phs[b_last_ph_i]
    b_last_word = b_ph.words[-1]
    print("         last_word", b_last_word.pos_detail, b_last_word.base)
    if b_last_word.pos_detail == "句点":
        return False
    if b_last_word.pos_detail == "接続助詞":
        return True
    if b_last_word.pos_detail == "読点":
        return True

    t_phs = p_phs[si]
    if len(t_phs) < 3:
        return True

    return False

# テンプレに埋め込む文を決定する
def _check_bond(pi, post, target_si, f_mrph):
    print("     bond checker", target_si)
    p_phs = mynlp.read_mrph_per_post(f_mrph, pi)
    bond_si_list = []

    # 前の文のチェック
    print("        check before")
    before_si = target_si
    while before_si > 0:
        if _bond_last_word(p_phs, before_si):
            bond_si_list.append(before_si-1)
        else:
            break
        before_si -= 1
    if len(bond_si_list) == 0 and len(post.sentences[target_si].body) < 3 and target_si != 0:
        bond_si_list.append(target_si-1)
    # 対象の文
    bond_si_list.append(target_si)

    # 後ろの文のチェック
    print("        check after")
    s_num = len(post.sentences)
    after_si = target_si + 1
    print("          after_si", after_si, s_num)
    while after_si < s_num:
        if _bond_last_word(p_phs, after_si):
            bond_si_list.append(after_si-1)
        else:
            break
        after_si += 1
    print("bond_si_list", bond_si_list)
    return sorted(list(set(bond_si_list)))


def no_premise_q_generator(post, pi, s, si, fn_templates, fn_mrph):
    # 前提が多すぎる場合
    if len(s.has_premise) > 1:
        print("      it has enough premise")
        return None

    si_list = _check_bond(pi, post, si, fn_mrph)
    print(si_list)

    sbodys = ""
    for s in si_list:
        sbodys += post.sentences[s].body

    return _make_rmsg(sbodys, fn_templates)
