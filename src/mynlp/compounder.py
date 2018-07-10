import mynlp


# 受け取った、w1,w2の単語をくっつける
# 品詞はw2を受け継ぐ
def _cross_word(w1, w2):
    nw = mynlp.WordClass()
    nw.base = w1.surface + w2.base
    nw.surface = w1.surface + w2.surface
    nw.yomi = w1.yomi + w2.yomi

    nw.pos = w2.pos
    nw.pos_detail = w2.pos_detail

    ll = w1.original_words
    if len(w2.original_words) > 0:
        ll.extend(w2.original_words)
    else:
        ll.append(w2.base)
    nw.original_words = ll

    try:
        nw.descriptions = w1.descriptions + "," + w2.descriptions
    except:
        if w1.descriptions:
            nw.descriptions = w1.descriptions
    try:
        nw.cateegory = w1.category.extend(w2.category)
    except:
        if w2.category:
            nw.cateegory = w2.category
    try:
        nw.domain = w1.domain.extend(w2.domain)
    except:
        if w2.domain:
            nw.domain = w2.domain
    try:
        nw.another = w1.another.extend(w2.another)
    except:
        if w2.domain:
            nw.domain = w2.domain
    try:
        nw.another = w1.another.extend(w2.another)
    except:
        if w2.another:
            nw.another = w2.another
    try:
        nw.proper_noun = w1.proper_noun.extend(w2.proper_noun)
    except:
        if w2.proper_noun:
            nw.proper_noun = w2.proper_noun
    return nw


# 文節をまたがり、合成語を作るものを調整する
# くっついた単語はWordクラスのoriginal_wordsにくっつく前の単語をリストで保持させる
def cross_ph_compounder(o_phs):
    if not o_phs:
        return None
    new_phs = {}  # 新しい結果を格納
    new_phs[0] = o_phs[0]

    phi_table = {0: 0, -1: -1}  # どの文節がどの文節になったか格納
    for ph_i in range(1, len(o_phs)):
        ni = max(new_phs.keys())

        last_word = new_phs[ni].words[-1]  # くっつくかどうか調べたい、一個前の文節の最後の単語
        next_word = o_phs[ph_i].words[0]  # くっつくかどうか調べたい、現在の文節の最初の単語

        if last_word.pos in ["名詞", "形容詞", "動詞"] and next_word.pos in ["名詞", "形容詞"]:
            # 文節の単語リストを統合する
            update_words = new_phs[ni].words[:-1]
            update_words.append(_cross_word(last_word, next_word))
            update_words.extend(o_phs[ph_i].words[1:])
            new_phs[ni].words = update_words
            new_phs[ni].children.extend(o_phs[ph_i].children)
            new_phs[ni].parent_id = o_phs[ph_i].parent_id
            phi_table[ph_i] = ni
            continue

        # くっつかない場合
        new_phs[ni + 1] = o_phs[ph_i]
        phi_table[ph_i] = ni + 1

    for ph_i, ph in new_phs.items():

        update_children = []
        for x in ph.children:
            if x > 0 and phi_table[x] != ph_i:
                update_children.append(phi_table[x])
            elif phi_table[x] != ph_i:
                update_children.append(x)
        new_phs[ph_i].children = update_children
        if new_phs[ph_i].parent_id:
            new_phs[ph_i].parent_id = phi_table[new_phs[ph_i].parent_id]

    return new_phs
