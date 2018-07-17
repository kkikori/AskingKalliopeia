import simplejson as json


def _embed_caseframe(casepair_list):
    dic_casepairs = []
    for casepair in casepair_list:
        new_case = {}
        new_case["th_i"] = casepair.th_i
        new_case["p_i"] = casepair.p_i
        new_case["s_i"] = casepair.s_i
        new_case["u_i"] = casepair.u_i
        new_case["particle"] = casepair.particle
        new_case["predicate"] = casepair.predicate
        new_case["category"] = casepair.category
        dic_casepairs.append(new_case)
    return dic_casepairs


def update_cases_file(f_cases, update_nouns, Caseframe_list):
    for noun in update_nouns:
        datas = {}
        datas["noun"] = noun
        datas["pairs"] = _embed_caseframe(Caseframe_list[noun].pairs)

        # ファイル書き込み
        fname = noun + ".json"
        f = f_cases / fname
        fw = f.open("w")
        json.dump(datas, fw, indent=2, ensure_ascii=False)
        fw.close()
