import sys
import random
import simplejson as json

import case_particle


def _read_templates(fn):
    if not fn.is_file():
        print("[file error]", fn, "is not found.")
        sys.exit()
    f = fn.open("r")
    jsonData = json.load(f)
    f.close()

    return jsonData


def _create_rmsg(fn_templates, cp, title, sentence):
    templates = _read_templates(fn_templates)
    tt = cp["noun"] + cp["cp"].particle + cp["cp"].predicate
    select_tmp = random.choice(templates["templates"])
    select_tmp = select_tmp.replace("<cp1>", tt).replace("<title>", title).replace("<s>", sentence)
    r_msg = ""
    r_msg += random.choice(templates["cushions"])
    r_msg += select_tmp
    return select_tmp


def _judge_q(Caseframe_list, cps, th_threshold):
    candidate_cps = []
    for t_cp in cps:
        if t_cp["noun"] not in Caseframe_list:
            continue
        noun_case = Caseframe_list[t_cp["noun"]]

        # 出てくるスレッドが多すぎor1つのスレッドにしか現れないのはダメ
        atn = noun_case.appear_thread_num()
        if len(atn) < 2 or len(atn) > th_threshold:
            continue

        # nounのスレッド内で出てくる回数が多いところ
        max_th = max(atn, key=atn.get)
        if max_th == t_cp["cp"].th_i:
            v = atn.pop(max_th)
            max_th = max(atn, key=atn.get)

        # 同じ(格助詞＋述語)ペアが別のスレッドで現れている場合
        tt = noun_case.search_just_same(t_pair=t_cp["cp"])
        if tt:
            candidate_cps.append([t_cp, random.choice(tt)])
            continue

        # 同じカテゴリかつ違うスレッドのペアのリスト
        tt = noun_case.search_same_category(t_pair=t_cp["cp"])
        if tt:
            candidate_cps.append([t_cp, random.choice(tt)])
            continue

        # 同じ助詞かつ違うスレッドのペアのリスト
        tt = noun_case.search_same_particle(t_pair=t_cp["cp"])
        if tt:
            candidate_cps.append([t_cp, random.choice(tt)])
            continue

        # 名詞がでているスレッドが極端に少ない場合
        if len(noun_case.pairs) < th_threshold / 10:
            for tt in noun_case.pairs:
                candidate_cps.append([t_cp, tt])

    if len(candidate_cps) == 0:
        return None

    return random.choice(candidate_cps)


def over_thread_q_generator(post, si, phs, Post_list, Thread_list, Caseframe_list, fn_templates, stop_word_list):
    cps = case_particle.extract_cp_and_embed_class(phs, post.belong_th_i, post.id, si, post.user_id)
    if len(cps) == 0:
        return None
    cut_cps = []
    for cp in cps:
        if cp["noun"] in stop_word_list:
            continue
        cut_cps.append(cp)
    select_cp = _judge_q(Caseframe_list, cut_cps, len(Thread_list) / 5)
    if select_cp:
        select = random.choice(select_cp)
        similary_s = Post_list[select.p_i].sentences[select.s_i]
        title = Thread_list[select.th_i].title
        return _create_rmsg(fn_templates, select, title, similary_s)
    return None
