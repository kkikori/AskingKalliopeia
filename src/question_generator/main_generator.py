import datetime, csv, json, re
import question_generator, mynlp

r_only_nod = r"同意|賛成|同感|good|great|nice|agree"
r_question = r"?$|？$|でしょうか"


def _setting_q_threshold(fn):
    f = fn.open("r")
    jsonData = json.load(f)
    thresholds = {}

    thresholds["t_user"] = datetime.timedelta(minutes=int(jsonData["threshold_t_user"]))
    thresholds["c_user"] = int(jsonData["threshold_c_user"])
    thresholds["t_thread"] = datetime.timedelta(minutes=int(jsonData["threshold_t_thread"]))
    thresholds["c_thread"] = int(jsonData["threshold_c_thread"])
    return thresholds


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


def _judge_user_term(post, usr, now_time, thresholds):
    if (now_time - post.created_at) < thresholds["t_user"]:
        return False

    # 今まで一度も問いかけしていなかったら
    if len(usr.previous_qs) == 0:
        return True

    # 最後に質問した投稿のid
    pq_i = usr.previous_qs[-1]
    pq_idx = usr.post_id_list.index(pq_i)

    if len(usr.post_id_list) - 1 - pq_idx > thresholds["c_user"]:
        return True
    return False


def _to_individual_q(user, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds):
    # no_premise_qがダメだった場合のみ、q2が起動
    # どちらか問いかけが生成された場合はTrue、失敗した場合はFalseを返す
    judge = _judge_user_term(post=post, usr=user, now_time=now_time, thresholds=thresholds)
    if not judge:
        return False
    for si, s in enumerate(post.sentences):
        if s.tag != "CLAIM" or len(s.has_premise) > 1:
            continue
        elif re.search(r_question, s.body):
            # 質問文は除く措置
            continue
        else:
            phs = mynlp.read_mrph_per_sentence(f_path=f_paths["MRPH_ANALYSIS"], pi=target_pi, si=si)
            q1 = question_generator.no_premise_q_generator(target={"pi": target_pi, "si": si}, phs=phs, \
                                                           TFIDF_pp=TFIDF_pp, \
                                                           f_template=f_paths["NO_PREMISE_Q_TEMPLATES"])

        if q1:
            _save_and_call_q(pi=target_pi, si=si, q_body=q1, fn_postapi=f_paths["POST_API"],
                             f_save=f_paths["INDIVIDUAL_Q"])
            return True

            # q2 = question_generator.over_thread_q_generator(THREAD=)

    return False


# 問いかけを生成したらTrue,できなかったらFalseを返す
def _to_collective_q(thread, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds, POSTS):
    judge = _judge_thread_term(thread=thread, post=post, now_time=now_time, thresholds=thresholds)
    if not judge:
        return False
    for si, s in enumerate(post.sentences):
        if s.tag != "CLAIM" or not s.pointer_post_id:
            continue
        # q2をやる
        if len(s.body) < 10 and re.search(r_only_nod, s.body):
            print("try q2 generate", target_pi, si, thread.title)
            q3 = question_generator.has_nod_q_generator(post=POSTS[s.pointer_post_id], si=s.pointer_sentence_id, \
                                                        thread_title=thread.title, f_tmp=f_paths["HAS_NOD_Q_TEMPLATES"])
            if q3:
                _save_and_call_q(pi=target_pi, si=si, q_body=q3, fn_postapi=f_paths["POST_API"], \
                                 f_save=f_paths["COLLECTIVE_Q"])
                return True

        target_id = {"pi": target_pi, "si": si}
        pointer_id = {"pi": s.pointer_post_id, "si": s.pointer_sentence_id}
        print("try q3 generate ", target_pi, si)
        q4 = question_generator.same_category_q_generator(TFIDF_pp=TFIDF_pp, parent=pointer_id, child=target_id, \
                                                          th_title=thread.title, f_mrph=f_paths["MRPH_ANALYSIS"], \
                                                          f_tmp=f_paths["SAME_CATEGORY_Q_TEMPLATES"])
        if q4:
            _save_and_call_q(pi=target_pi, si=si, q_body=q4, fn_postapi=f_paths["POST_API"], \
                             f_save=f_paths["COLLECTIVE_Q"])
            return True
    return False


def _judge_thread_term(thread, post, now_time, thresholds):
    if now_time - post.created_at < thresholds["t_thread"]:
        return False

    if len(thread.previous_qs) == 0:
        return True

    # 最後に質問した投稿のid
    pq_i = thread.previous_qs[-1]
    pq_idx = thread.posts.index(pq_i)

    if len(thread.posts) - 1 - pq_idx > thresholds["c_thread"]:
        return True
    return False


def q_generator_main(POSTS, THREAD, USERS, f_paths, TFIDF_pp, now_time):
    # 閾値の設定
    thresholds = _setting_q_threshold(f_paths["SETTING"])

    """
    to_individual_q
    """
    individual = True
    for user_i, user in USERS.items():
        target_pi = user.post_id_list[-1]
        q = _to_individual_q(user=user, target_pi=target_pi, post=POSTS[target_pi], now_time=now_time, f_paths=f_paths,
                             TFIDF_pp=TFIDF_pp, thresholds=thresholds)
        if q:
            individual = False

    # 一回でもq1をやったら終わる
    # if individual:
    #     return


    """
    to_collective_q
    """
    for th_i, thread in THREAD.items():
        target_pi = thread.posts[-1]
        q = _to_collective_q(thread=thread, target_pi=target_pi, post=POSTS[target_pi], now_time=now_time, \
                             f_paths=f_paths, TFIDF_pp=TFIDF_pp, thresholds=thresholds, POSTS=POSTS)

    return
