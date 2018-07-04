from collections import defaultdict

# カテゴリ・ドメインを持つ単語のみ抽出
def extract_category_domain(phs):
    categorys = defaultdict(list)
    for pi, p in phs.items():
        for word in p.words:
            if word.category:
                categorys[word.category].append([word.base, pi])
            if word.domain:
                categorys[word.domain].append([word.base, pi])

    return dict(categorys)

# 文節ph_iにかかる文節idを返す
def search_dependency_pi(phs, ph_i):
    child_is = phs[ph_i].children
    bnst = []
    while len(child_is) != 0:
        for ci in child_is:
            bnst.append(ci)
        child_is = phs[child_is[0]].children

    return sorted(bnst)

# 文節ph_iにかかる全ての要素を返す
def search_dependency(phs, ph_i):
    child_is = phs[ph_i].children
    bnst = []
    while len(child_is) != 0:
        for ci in child_is:
            bnst.append(ci)
        child_is = phs[child_is[0]].children
    r_str = ""
    for si in sorted(bnst):
        for word in phs[si].words:
            if word.pos != "特殊":
                r_str += word.surface
    return r_str

# 文節内のtarget_wordに関係しそうなところをとってくる
def extra_relate_word_in_ph(ph, target_w):
    rt = ""
    # target_wordがその文節の中で何番目の単語が調べる
    ph_words = []
    for word in ph.words:
        ph_words.append(word.base)
    id_target_word = ph_words.index(target_w)

    # target_word前の単語を足す
    for word in ph.words[:id_target_word]:
        if word.pos != "特殊":
            rt += word.surface

    # target_wordが最後の単語だったら
    if id_target_word == len(ph.words) - 1:
        return rt + target_w

    # target_wordの後ろの単語の処理
    parse_target_w = ph.words[id_target_word].pos
    back_of_target = ph.words[id_target_word + 1]
    parse_back_of_target = back_of_target.pos

    if parse_target_w == "名詞" and parse_back_of_target in ["名詞", "接尾辞"]:
        return rt + target_w + back_of_target.base  # target_wordが名詞だったら
    elif parse_target_w == "動詞" and parse_back_of_target not in ["助詞", "特殊"]:
        return rt + ph.words[id_target_word].surface + back_of_target.base
    elif parse_back_of_target == "接尾辞":
        return rt + target_w + back_of_target.surface

    return rt + target_w

