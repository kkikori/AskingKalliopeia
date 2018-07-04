import mynlp
import re
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


# 文節をまたいだ合成後にも対応
def __seach_dependency(phs, ph_i):
    bnst = []

    # ph_iの文節にかかる文節idをすべてとってくる
    child_is = phs[ph_i].children
    while len(child_is) != 0:
        for ci in child_is:
            bnst.append(ci)
        child_is = phs[child_is[0]].children

    r_str = ""  # 句の文字列
    r_str_words = []  # 含まれる単語列
    for si in sorted(bnst):
        for word in phs[si].words:
            if word.pos != "特殊":
                r_str += word.surface
                if word.original_words:
                    r_str_words.extend(word.original_words)
                else:
                    r_str_words.append(word.base)
            if word.pos == "助詞" and word.base == "は":
                # print("  word.pos == 助詞 word.base == は ")
                r_str = ""
                r_str_words = []
    return r_str, r_str_words


# 文節内のtarget_wordに関係しそうなところをとってくる
def __extra_relate_word_in_ph(ph, target_w):
    rt = ""
    rt_words = []

    # target_wordがその文節の中で何番目の単語が調べる
    ph_words = []
    for word in ph.words:
        ph_words.append(word.base)
    id_target_word = ph_words.index(target_w)

    # target_word前の単語を足す
    for word in ph.words[:id_target_word]:
        if word.pos != "特殊":
            rt += word.surface
            if word.original_words:
                rt_words.extend(word.original_words)
            else:
                rt_words.append(word.base)
    # target_wordが最後の単語だったら
    if id_target_word == len(ph.words) - 1:

        rt += target_w

        if ph.words[id_target_word].original_words:
            rt_words.extend(ph.words[id_target_word].original_words)
        else:
            rt_words.append(ph.words[id_target_word].base)
        return rt, rt_words

    # target_wordの後ろの単語の処理
    pos_target_w = ph.words[id_target_word].pos
    back_of_target = ph.words[id_target_word + 1]
    pos_back_of_target = back_of_target.pos

    if ph.words[id_target_word].original_words:
        rt_words.extend(ph.words[id_target_word].original_words)
    else:
        rt_words.append(ph.words[id_target_word].base)

    if pos_target_w == "動詞" and pos_back_of_target not in ["助詞", "特殊"]:
        rt = rt + ph.words[id_target_word].surface + back_of_target.base
        return rt, rt_words
    elif pos_back_of_target == "接尾辞":
        rt = rt + ph.words[id_target_word].surface + back_of_target.surface
        return rt, rt_words

    rt += ph.words[id_target_word].base
    return rt, rt_words


# ストップワードと数字を省く
def __filter_word(wordlists, stop_word_list, pos_l):
    return_words = []
    numeric = r"[0-9]+"

    for word in wordlists:
        if not re.match(numeric, word) and (word not in stop_word_list):
            return_words.append(word)
    return return_words


def _choice_pair(cand_pairs, TFIDF_pp, target):
    if len(cand_pairs) == 1:
        pair = cand_pairs[0]
        n = pair["noun"]
        a = pair["adjective"]
        return [n["phrasal"], a["phrasal"]]

    target_tfidf_score = TFIDF_pp.calc_tfidf_from_pii(int(target["pi"]))
    pair_score = []
    for cand_pair in cand_pairs:
        cand_word = []
        score_list = []
        ws1 = cand_pair["noun"]
        ws2 = cand_pair["adjective"]
        # print("    ws1[phrasal_words]", ws1["phrasal_words"])
        # print("    ws2[phrasal_words]", ws2["phrasal_words"])
        cand_word.extend(ws1["phrasal_words"])
        cand_word.extend(ws2["phrasal_words"])
        cand_word = __filter_word(wordlists=cand_word, stop_word_list=TFIDF_pp.stop_word_list, pos_l=TFIDF_pp.pos_l)

        for w in cand_word:
            try:
                score_list.append(target_tfidf_score[w])
            except:
                # print("  error in _choice_pair(", w, ")")
                print("")

        try:
            pair_score.append(sum(score_list) / len(score_list))
        except:
            # print("  error in _choice_pair(", w, ")", target_tfidf_score.keys())
            pair_score.append(-100)
    i = pair_score.index(max(pair_score))

    select_pair = cand_pairs[i]

    return (select_pair["noun"])["phrasal"], (select_pair["adjective"])["phrasal"]


# 名詞と形容詞の係り受けペアを抽出
# ペアを全て返す
def _extract_cand_pair(phs):
    cand_pairs = []
    """cand_pairの形
    pair = {
        "noun":{
            "original":元の単語,
            "phrasal":テンプレに埋め込む形,
            "phrasal_words":phrasalに含まれる単語},
            "ph_i":文節id
        "adjective"{nounと同様}
        "priority":nounとadjectiveどっちが文中だと先に出てくるか
        }
    """
    for pi, ph in phs.items():
        # print(pi)
        # 係り先がなかった場合
        if ph.parent_id < 0:
            continue

        # 係り先を調査
        parent = phs[ph.parent_id]
        # 文節に名詞があり、係り先に形容詞があった場合
        if len(ph.nouns()) > 0 and len(parent.adjectives()) > 0:

            new_pair = {}
            # nounに関する処理、nounにかかる文節とnounの文節内をくっつける
            noun1 = {}
            noun1["phrasal_words"] = []
            noun1["original"] = ph.nouns()[0]
            noun1["ph_i"] = pi

            r1_str, r1_words = __seach_dependency(phs, pi)
            r2_str, r2_words = __extra_relate_word_in_ph(ph, noun1["original"])

            # print("noun_original", noun1["original"])
            # print("r1_words, r2_words", r1_words, r2_words)

            noun1["phrasal"] = r1_str + r2_str
            r1_words.extend(r2_words)
            noun1["phrasal_words"] = r1_words
            # print("   phrasal_words", noun1["phrasal_words"])
            new_pair["noun"] = noun1

            # adjectiveに関する処理、adjectiveの文節内をくっつける
            adjective1 = {}
            adjective1["phrasal_words"] = []
            adjective1["original"] = (parent.adjectives())[0]
            adjective1["ph_i"] = ph.parent_id
            r_str, r_words = __extra_relate_word_in_ph(parent, adjective1["original"])
            # print("    r_words", r_words)
            adjective1["phrasal"] = r_str
            adjective1["phrasal_words"] = r_words
            new_pair["adjective"] = adjective1
            new_pair["priority"] = "noun"
            cand_pairs.append(new_pair)

        elif len(ph.adjectives()) > 0 and len(parent.nouns()) > 0:

            new_pair = {}
            # adjectiveに関する処理
            a1 = {}
            a1["phrasal_words"] = []
            a1["original"] = ph.adjectives()[0]
            a1["ph_i"] = pi
            r1_str, r1_words = __seach_dependency(phs, pi)
            r2_str, r2_words = __extra_relate_word_in_ph(ph, a1["original"])
            a1["phrasal"] = r1_str + r2_str
            r1_words.extend(r2_words)
            a1["phrasal_words"] = r1_words
            new_pair["adjective"] = a1

            # adjectiveに関する処理、adjectiveの文節内をくっつける
            n1 = {}
            n1["phrasal_words"] = []
            n1["original"] = (parent.nouns())[0]
            n1["ph_i"] = ph.parent_id
            r_str, r_words = __extra_relate_word_in_ph(parent, n1["original"])
            n1["phrasal"] = r_str
            n1["phrasal_words"] = r_words
            new_pair["noun"] = n1
            new_pair["priority"] = "adjective"
            cand_pairs.append(new_pair)

    return cand_pairs


# 形容動詞で形の変形が必要な場合は変形する
def _deform_a1(n1, a1, f_template):
    n1a1_templates = _read_templates(fn=f_template)
    rc = random.choice(n1a1_templates["cushions"])
    tmp = n1a1_templates["templates"]

    list_demand_adjust = [0, 1]
    ri = random.randint(0, len(tmp) - 1)
    if (ri in n1a1_templates["need_demand"]) and (a1[-1] == "だ"):
        rmsg = tmp[ri].replace("<n>", n1).replace("<a>", a1[:-1] + "な")
    else:
        rmsg = tmp[ri].replace("<n>", n1).replace("<a>", a1)

    return rc + rmsg


def no_premise_q_generator(f_template, target="", phs="", TFIDF_pp="", ):
    cross_phs = mynlp.cross_ph_compounder(o_phs=phs)

    cand_pairs = _extract_cand_pair(phs=cross_phs)

    if len(cand_pairs) == 0:
        return None
    n1, a1 = _choice_pair(cand_pairs=cand_pairs, TFIDF_pp=TFIDF_pp, target=target)

    return _deform_a1(n1, a1, f_template)
