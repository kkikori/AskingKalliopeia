import json, mynlp
from collections import OrderedDict


def read_mrph_per_sentence(f_path, pi, si):
    phs = OrderedDict()
    fn = str(pi) + ".json"
    f = (f_path / fn).open("r")
    jsonData = json.load(f)

    tmp = jsonData[si]
    if not tmp:
        return None
    for bnst_i, bnst in enumerate(tmp):
        ph = mynlp.Phrase()
        ph.parent_id = bnst["parent_id"]
        ph.dpndtype = bnst["dpndtype"]
        ph.children = bnst["children"]
        ph.parent = bnst["parent"]

        for mrph in bnst["words"]:
            word = mynlp.Word()
            word.surface = mrph["surface"]
            word.base = mrph["base"]
            word.yomi = mrph["yomi"]
            word.pos = mrph["pos"]
            word.pos_detail = mrph["pos_detail"]
            word.descriptions = mrph["descriptions"]
            word.category = mrph["category"]
            word.domain = mrph["domain"]
            word.another = mrph["another"]
            word.proper_noun = mrph["proper_noun"]
            ph.words.append(word)
        phs[bnst_i] = ph
    f.close()

    return phs


def read_mrph_per_post(f_path, pi):
    fn = str(pi) + ".json"
    f = (f_path / fn).open("r")
    jsonData = json.load(f)
    p_phs = []
    for tmp in jsonData:
        phs = OrderedDict()
        if tmp == None:
            p_phs.append(None)
            continue

        for bnst_i, bnst in enumerate(tmp):
            ph = mynlp.Phrase()
            ph.parent_id = bnst["parent_id"]
            ph.dpndtype = bnst["dpndtype"]
            ph.children = bnst["children"]
            ph.parent = bnst["parent"]

            for mrph in bnst["words"]:
                word = mynlp.Word()
                word.surface = mrph["surface"]
                word.base = mrph["base"]
                word.yomi = mrph["yomi"]
                word.pos = mrph["pos"]
                word.pos_detail = mrph["pos_detail"]
                word.descriptions = mrph["descriptions"]
                word.category = mrph["category"]
                word.domain = mrph["domain"]
                word.another = mrph["another"]
                word.proper_noun = mrph["proper_noun"]
                ph.words.append(word)
            phs[bnst_i] = ph
        p_phs.append(phs)
    f.close()

    return p_phs
