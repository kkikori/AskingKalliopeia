import datetime
import csv
import json
import question_generator


# 時間とかの条件を読み込む
def _setting_q_threshold(fn):
    f = fn.open("r")
    jsonData = json.load(f)
    thresholds = {}

    thresholds["t_user"] = datetime.timedelta(minutes=int(jsonData["threshold_t_user"]))
    thresholds["c_user"] = int(jsonData["threshold_c_user"])
    thresholds["t_thread"] = datetime.timedelta(minutes=int(jsonData["threshold_t_thread"]))
    thresholds["c_thread"] = int(jsonData["threshold_c_thread"])
    return thresholds


# 2箇所に発言内容を保存する
def _save_and_call_q(pi, si, q_body, fn_postapi, f_save):
    # save to file
    add_row = [pi, si, q_body]
    with f_save.open("a") as f:
        writer = csv.writer(f, lineterminator='\n')  # 行末は改行
        writer.writerow(add_row)
    f.close()

    # api attack
    save_q = {"body": q_body, "in_reply_to_id": pi}

    fn = str(pi) + ".json"
    f = (fn_postapi / fn).open("w")
    json.dump(save_q, f, indent=2, ensure_ascii=False)
    f.close()

    return


# ファイシリテータへの返信だったら、Trueを返す
# スレッドの親投稿だったら、Trueを返す
# それ以外はFalse
def _exception_checker(target_pi, POSTS, facilitator_i):
    target_post = POSTS[target_pi]
    if not target_post.reply_to_id:
        return True

    reply_to = POSTS[target_post.replpy_to_id]
    if POSTS[reply_to].user_id == facilitator_i:
        return True
    return False


def q_generator_main(POSTS, THREAD, USERS, f_paths, TFIDF_pp, now_time, facilitator_i):
    # 閾値の設定
    thresholds = _setting_q_threshold(f_paths["SETTING"])

    """
    to_individual_q
    """
    individual = True
    print("to_individual_q")
    for user_i, user in USERS.items():
        target_pi = user.pi_list[-1]
        # 構造解析器により注釈がつけられていない場合（時刻で判定）
        if not POSTS[target_pi].created_at < POSTS[target_pi].updated_at:
            print("           POSTS[target_pi] is not has updated_at")
            print("                created_at", POSTS[target_pi].created_at, "  updated_at",
                  POSTS[target_pi].updated_at)
            # tagがついてない場合
            try:
                target_pi = user.pi_list[-2]
            except:
                continue

        # 問いかけ対象外を弾く
        if _exception_checker(target_pi, POSTS, facilitator_i):
            continue

        q = question_generator.to_individual_q(user=user, target_pi=target_pi, \
                                               post=POSTS[target_pi], now_time=now_time, f_paths=f_paths, \
                                               TFIDF_pp=TFIDF_pp, thresholds=thresholds, \
                                               facilitator_i=facilitator_i)
        if q:
            individual = False
            _save_and_call_q(q["pi"], q["si"], q["q_body"], f_paths["POST_API"], f_paths["INDIVIDUAL_Q"])

    # 一回でもq1をやったら終わる
    # if individual:
    #     return


    """
    to_collective_q
    """
    print("to_collective_q")
    for th_i, thread in THREAD.items():
        print("  thread :", thread.title)
        target_pi = thread.pi_list[-1]
        # """
        if not POSTS[target_pi].created_at < POSTS[target_pi].updated_at:
            print("           POSTS[target_pi] is not has updated_at")
            print("                created_at", POSTS[target_pi].created_at, "  updated_at",
                  POSTS[target_pi].updated_at)
            try:
                target_pi = thread.pi_list[-2]
            except:
                continue
        # """

        # 問いかけ対象外を除く
        if _exception_checker(target_pi, POSTS, facilitator_i):
            continue

        q = question_generator.to_collective_q(thread=thread, target_pi=target_pi, \
                                               post=POSTS[target_pi], now_time=now_time, \
                                               f_paths=f_paths, TFIDF_pp=TFIDF_pp, \
                                               thresholds=thresholds, POSTS=POSTS, \
                                               facilitator_i=facilitator_i)
        if q:
            _save_and_call_q(q["pi"], q["si"], q["q_body"], f_paths["POST_API"], f_paths["COLLECTIVE_Q"])

    return
