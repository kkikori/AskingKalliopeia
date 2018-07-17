import mynlp
from .CasepairClass import CasepairClass


def _extract_self_sufficient_word(words):
    for word in words:
        if word.pos in ["形容詞", "動詞"]:
            return word
    return None


def extract_cp(phs):
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

                cp = {}
                cp["noun"] = previous_w.base
                cp["particle"] = word.particle
                cp["predicate"] = parent_self_w.base
                cp["cateogory"] = word.category

                cps.append(cp)
    return cps


def extract_cp_and_embed_class(phs, th_i, p_i, s_i, u_i):
    if not phs:
        return []
    cps = extract_cp(phs)
    cps_class_list = []
    for cp in cps:
        tmp = CasepairClass(th_i=th_i, p_i=p_i, s_i=s_i, u_i=u_i, particle=cp["particle"], \
                            predicate=cp["predicate"], category=cp["category"])
        cps_class_list.append({"noun": cp["noun"], "cp": tmp})
    return cps
