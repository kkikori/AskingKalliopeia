import simplejson as json
import sys
import datetime
from collections import OrderedDict

import mynlp
from .normalize import normalize_main


# クラスをdic型に変換、jsonファイルにかきこめる形にする
def _json_convert(ph):
    if ph is None:
        return None

    datas = []
    for k, v in ph.items():
        data = OrderedDict()
        data["parent_id"] = v.parent_id
        data["parent"] = v.parent
        data["children"] = v.children  # この文節の子文節たち
        data["dpndtype"] = v.dpndtype

        words = []
        for word in v.words:
            w_info = OrderedDict()
            w_info["surface"] = word.surface
            w_info["base"] = word.base
            w_info["yomi"] = word.yomi
            w_info["pos"] = word.pos
            w_info["pos_detail"] = word.pos_detail
            w_info["descriptions"] = word.descriptions
            w_info["category"] = word.category
            w_info["domain"] = word.domain
            w_info["another"] = word.another
            w_info["proper_noun"] = word.proper_noun
            words.append(w_info)
        data["words"] = words  # この文節に含まれている単語

        datas.append(data)

    return datas


# 形態素解析の結果をjson形式で保存
def _save_mrph(fw_path="", post=""):
    mrph_data = []
    for sentence in post["sentences"]:
        ss = normalize_main(sentence["body"])
        phs = mynlp.convert(sentence=ss)
        if phs:
            phs_j = _json_convert(ph=phs)
        else:
            phs_j = {}
        mrph_data.append(phs_j)

    f = str(post["id"]) + ".json"
    fn = fw_path / f
    fw = fn.open("w")
    json.dump(mrph_data, fw, indent=2, ensure_ascii=False)
    fw.close()

    return mrph_data


def _past_post_list_reader(fn):
    # 過去に形態素解析した投稿idをリストで返す
    if not fn.exists():
        print("[FILE ERROR]", fn, "is not found.")
        sys.exit()
    pplist = []
    for row in fn.open("r"):
        line = row.rstrip("\n")
        pplist.append(line)
    return pplist


# スレッドごとに新しい投稿があるかどうか調べる
# 新しく形態素解析したポストの文ごとの構文解析結果をリストで返す
def _Take_out_new_posts(fr, fn_MrphAnalysis, pplist):
    if not fr.is_file():
        print("[file error]", fr.name, "is not found.")
        return []
    f = fr.open("r")
    jsonData = json.load(f)
    post_list = jsonData["posts"]

    new_post_phs = []
    new_post_pi = []
    for post in post_list:
        if str(post["id"]) in pplist:
            continue
        p_mrph = _save_mrph(fw_path=fn_MrphAnalysis, post=post)
        new_post_phs.append(p_mrph)
        new_post_pi.append(post["id"])

    return new_post_phs, new_post_pi


def _add_post_list_writer(fn, add_post_pi):
    # 新たに読み込んだ投稿をリストに追記
    with fn.open("a") as f:
        for pi in add_post_pi:
            f.write(str(pi)+ "\n")


def Mrph_analysis_main(fn_Classified, fn_MrphAnalysis, fn_PastPostList):
    # 形態素解析済みのポストリストを取得
    past_post_list = _past_post_list_reader(fn=fn_PastPostList)

    # 全スレッドのパスを取得
    files = [x for x in fn_Classified.iterdir() if x.is_dir()]

    new_post_phs = []
    add_post_pi = []
    for fp in files:
        print("reading thread", fp.name)
        phs, new_post_pi = _Take_out_new_posts(fr=fp / "classified.json", fn_MrphAnalysis=fn_MrphAnalysis,
                                               pplist=past_post_list)
        new_post_phs.extend(phs)
        add_post_pi.extend(new_post_pi)

    _add_post_list_writer(fn=fn_PastPostList, add_post_pi=add_post_pi)

    return new_post_phs
