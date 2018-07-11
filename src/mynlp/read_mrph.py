import simplejson as json
from collections import OrderedDict
import mynlp

# dict型をクラスに格納する
def _embed_to_class(bnsts):
    phs = OrderedDict()
    if not bnsts:
        return None
    for bnst_i, bnst in enumerate(bnsts):
        ph = mynlp.PhraseClass(parent_id=bnst["parent_id"], parent=bnst["parent"],
                               children=bnst["children"], dpndtype=bnst["dpndtype"])

        for mrph in bnst["words"]:
            word = mynlp.WordClass(mrph["surface"],mrph["base"],mrph["yomi"],
                                   mrph["pos"],mrph["pos_detail"],mrph["descriptions"],
                                   mrph["category"],mrph["domain"],mrph["another"],
                                   mrph["proper_noun"])
            ph.words.append(word)
        phs[bnst_i] = ph
    return phs


def read_mrph_per_sentence(f_path, pi, si):
    fn = str(pi) + ".json"
    f = (f_path / fn).open("r")
    jsonData = json.load(f)
    tmp = jsonData[si]
    phs = _embed_to_class(tmp)
    f.close()
    return phs


def read_mrph_per_post(f_path, pi):
    fn = str(pi) + ".json"
    f = (f_path / fn).open("r")
    jsonData = json.load(f)
    p_phs = []
    for tmp in jsonData:
        phs = _embed_to_class(tmp)
        p_phs.append(phs)
    f.close()

    return p_phs
