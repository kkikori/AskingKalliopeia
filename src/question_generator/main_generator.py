import datetime, csv, json, re
import question_generator, mynlp

r_only_nod = r"同意|賛成|同感|good|great|nice|agree"
r_question = r"\?$|？$|でしょうか"


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
        print("     time setting")
        return False

    # 今まで一度も問いかけしていなかったら
    if len(usr.previousQ_list) == 0:
        return True

    # 最後に質問した投稿のid
    pq_i = usr.previousQ_list[-1]
    pq_idx = usr.pi_list.index(pq_i)

    if len(usr.pi_list) - 1 - pq_idx > thresholds["c_user"]:
        return True
    return False


def _to_individual_q(user, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds, facilitator_i):
    print("   user", user.name, len(user.pi_list))
    # no_premise_qがダメだった場合のみ、q2が起動
    # どちらか問いかけが生成された場合はTrue、失敗した場合はFalseを返す

    # ファシリテータは対象外
    if user.id == facilitator_i:
        print("        it is facilitator ")
        return False

    judge = _judge_user_term(post=post, usr=user, now_time=now_time, thresholds=thresholds)
    if not judge:
        return False
        print("   judge is not")
    for si, s in enumerate(post.sentences):
        if s.component_type != "CLAIM" or len(s.has_premise) > 1:
            continue
            print("     not claim")
        elif re.search(r_question, s.body):
            print("      re,search")
            # 質問文は除く措置
            continue
        else:
            phs = mynlp.read_mrph_per_sentence(f_path=f_paths["MRPH_ANALYSIS"], pi=target_pi, si=si)
            q1 = question_generator.no_premise_q_generator(sbody=s.body,
                                                           fn_templates=f_paths["NO_PREMISE_Q_TEMPLATES"])

        if q1:
            _save_and_call_q(pi=target_pi, si=si, q_body=q1, fn_postapi=f_paths["POST_API"],
                             f_save=f_paths["INDIVIDUAL_Q"])
            return True
        else:
            print("       it is my fault")
            # q2 = question_generator.over_thread_q_generator(THREAD=)

    return False


# 問いかけを生成したらTrue,できなかったらFalseを返す
def _to_collective_q(thread, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds, POSTS, facilitator_i):
    # ファシリテータは対象外
    if post.user_id == facilitator_i:
        return False
    judge = _judge_thread_term(thread=thread, post=post, now_time=now_time, thresholds=thresholds)
    if not judge:
        print("   judge is not")
        return False
    if not post.reply_to_id:
        print("   post.reply_to_id")
        return False
    if POSTS[post.reply_to_id].user_id == facilitator_i:
        print("   to facilitator")
        return False

    reply_to_id = post.reply_to_id
    related_to_post = POSTS[reply_to_id]

    for si, s in enumerate(post.sentences):
        if s.component_type != "CLAIM":
            print("     not claim")
            continue
        reply_to_si = related_to_post.si_list.index(s.related_to)
        # q2をやる
        if len(s.body) < 10 and re.search(r_only_nod, s.body):
            print("try q2 generate", target_pi, si, thread.title)

            q3 = question_generator.has_nod_q_generator(post=POSTS[reply_to_id], si=reply_to_si, \
                                                        thread_title=thread.title, f_tmp=f_paths["HAS_NOD_Q_TEMPLATES"])
            if not q3:
                print("    it is my fault")
            if q3:
                _save_and_call_q(pi=target_pi, si=si, q_body=q3, fn_postapi=f_paths["POST_API"], \
                                 f_save=f_paths["COLLECTIVE_Q"])
                return True

        target_id = {"pi": target_pi, "si": si}
        pointer_id = {"pi": reply_to_id, "si": reply_to_si}
        print("try q3 generate ", target_pi, si)
        q4 = question_generator.same_category_q_generator(TFIDF_pp=TFIDF_pp, parent=pointer_id, child=target_id, \
                                                          th_title=thread.title, f_mrph=f_paths["MRPH_ANALYSIS"], \
                                                          f_same=f_paths["SAME_CATEGORY_Q_TEMPLATES"])
        if q4:
            _save_and_call_q(pi=target_pi, si=si, q_body=q4, fn_postapi=f_paths["POST_API"], \
                             f_save=f_paths["COLLECTIVE_Q"])
            return True
        else:
            print("    it is my fault")
    return False


def _judge_thread_term(thread, post, now_time, thresholds):
    if now_time - post.created_at < thresholds["t_thread"]:
        print("     time setting", now_time, post.created_at)
        return False

    if len(thread.previousQ_list) == 0:
        return True

    # 最後に質問した投稿のid
    pq_i = thread.previousQ_list[-1]
    pq_idx = thread.pi_list.index(pq_i)

    if len(thread.pi_list) - 1 - pq_idx > thresholds["c_thread"]:
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
        q = _to_individual_q(user=user, target_pi=target_pi, post=POSTS[target_pi], now_time=now_time, f_paths=f_paths,
                             TFIDF_pp=TFIDF_pp, thresholds=thresholds, facilitator_i=facilitator_i)
        if q:
            individual = False

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
        q = _to_collective_q(thread=thread, target_pi=target_pi, post=POSTS[target_pi], now_time=now_time, \
                             f_paths=f_paths, TFIDF_pp=TFIDF_pp, thresholds=thresholds, POSTS=POSTS,
                             facilitator_i=facilitator_i)

    return
