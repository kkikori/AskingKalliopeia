import mynlp


def _extract_self_sufficient_word(words):
    for word in words:
        if word.pos in ["形容詞", "動詞"]:
            return word
    return None


def extract_cp(phs, th_i, p_i, s_i, u_i):
    if not phs:
        return []
    cps = []
    for pi, ph in phs.items():
        previous_w = mynlp.WordClass()
        if not ph.parent_id:
            continue
        for word in ph.words:
            if previous_w.pos_detail == "形式名詞":
                continue
            if word.pos_detail == "格助詞" and previous_w.pos == "名詞":
                if ph.parent_id < 0:
                    continue
                parent = phs[ph.parent_id]
                parent_self_w = _extract_self_sufficient_word(parent.words)

                if not parent_self_w:
                    continue

                cp = case_pair(th_i=th_i, p_i=p_i, s_i=s_i, u_i=u_i, particle=word.base, \
                               predicate=parent_self_w.base, category=word.category)
