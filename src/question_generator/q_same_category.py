import random
import numpy as np
from collections import defaultdict
import sys
import json

import mynlp


def _read_templates(fn):
    if not fn.is_file():
        print("[file error]", fn, "is not found.")
        sys.exit()
    f = fn.open("r")
    jsonData = json.load(f)
    f.close()

    return jsonData


r_only_nod = r"同意|賛成|同感|共感"


def _choicer_category_by_tfidf(p_category, c_category, common_categorys, TFIDF_pp, parent, child):
    #
    p_tfidf_score = TFIDF_pp.calc_tfidf_from_pi(parent["pi"])
    c_tfidf_score = TFIDF_pp.calc_tfidf_from_pi(child["pi"])

    category_score = {}
    for cmn_ca in common_categorys:
        tmp = []
        for w in p_category[cmn_ca]:
            try:
                tmp.append(p_tfidf_score[w[0]])
            except:
                print("")
                # print("error  ", parent["pi"], parent["si"], w[0])
        # print("")
        for w in c_category[cmn_ca]:
            try:
                tmp.append(c_tfidf_score[w[0]])
            except:
                print("")
                # print("error  ", child["pi"], child["si"], w[0])

        try:
            category_score[cmn_ca] = sum(tmp) / len(tmp)
        except:
            return random.choice(common_categorys)

    # print("category_score ", category_score)
    category_sorted = sorted(category_score, key=lambda x: x[1])

    return category_sorted[0]


# テンプレ文に埋め込む節を抽出する
def _extract_embed_word(phs="", category_words=""):
    embed_words_candidate = []
    # print("           category words", category_words)

    # カテゴリを持つ単語の文節idリスト
    category_word_ph_ids = [int(n) for n in list(np.array(category_words)[:, 1])]

    for cw in category_words:
        # print(" cw :", cw)
        depend_ids = mynlp.search_dependency_pi(phs, cw[1])
        # print("   depend_ids :", depend_ids)
        # 長すぎる名詞節は取り除く
        if len(depend_ids) > 2 and len(embed_words_candidate) != 0:
            continue
        # 単語cw[0]にかかっている文節と同カテゴリの単語の属する文節の共起をみる
        common_ph = set(depend_ids) & set(category_word_ph_ids)
        # print("   common_ph :", common_ph)
        if len(common_ph) > 0:
            embed_words_candidate.pop(-1)
        embed_words_candidate.append(
            mynlp.search_dependency(phs, cw[1]) + mynlp.extra_relate_word_in_ph(phs[cw[1]], cw[0]))
    return embed_words_candidate


# テンプレ文を生成
def _same_category(p_category, c_category, p_ph, c_ph, th_title, f_tmp):
    templates = _read_templates(fn=f_tmp)

    p_words = _extract_embed_word(phs=p_ph, category_words=p_category)
    c_words = _extract_embed_word(phs=c_ph, category_words=c_category)

    category_words = list(set(p_words + c_words))
    c = "、".join(random.sample(category_words, 3))

    rmsg = random.choice(templates["templates"]).replace("<c>", c).replace("<title>", th_title)

    return random.choice(templates["cushions"]) + rmsg


# カテゴリ・ドメインを持つ単語のみ抽出
def _extract_category_domain(phs):
    categorys = defaultdict(list)
    for pi, p in phs.items():
        for word in p.words:
            if word.category:
                categorys[word.category].append([word.base, pi])
            if word.domain:
                categorys[word.domain].append([word.base, pi])

    return dict(categorys)


# 親投稿文と投稿文が同じカテゴリに属する単語を持っている場合はテンプレ文を返す
# p_ph = 親投稿の形態素情報
def same_category_q_generator(TFIDF_pp="", parent="", child="", th_title="", f_mrph="", f_tmp=""):
    p_phs = mynlp.read_mrph_per_post(f_path=f_mrph, pi=parent["pi"])
    c_phs = mynlp.read_mrph_per_post(f_path=f_mrph, pi=child["pi"])

    if len(p_phs[parent["si"]]) == 0 or len(c_phs[child["si"]]) == 0:
        print("   phs is false")
        return None

    p_category = _extract_category_domain(p_phs[parent["si"]])
    c_category = _extract_category_domain(c_phs[child["si"]])
    # 人カテゴリ以外で共通するカテゴリを抽出
    common_category = list((set(p_category.keys()) & set(c_category.keys())) - set(["人"]))
    # print(common_category)
    if len(common_category) == 0:
        print("   common category is false")
        return None

    ca_n = _choicer_category_by_tfidf(p_category=p_category, c_category=c_category, \
                                      common_categorys=common_category, TFIDF_pp=TFIDF_pp, \
                                      parent=parent, child=child)
    r_msg = _same_category(p_category[ca_n], c_category[ca_n], p_phs[parent["si"]], c_phs[child["si"]], \
                           th_title, f_tmp)
    if not r_msg:
        print("   nazo no false")
    return r_msg
