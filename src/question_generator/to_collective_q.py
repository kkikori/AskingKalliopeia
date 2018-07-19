import re

import question_generator

r_only_nod = r"同意|賛成|同感|good|great|nice|agree"
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


# 問いかけを生成したらTrue,できなかったらFalseを返す
def to_collective_q(thread, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds, POSTS, facilitator_i):
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
        if not s.related_to:
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
                q = {"pi": target_pi, "si": si, "q_body": q3}
                #_save_and_call_q(pi=target_pi, si=si, q_body=q3, fn_postapi=f_paths["POST_API"], f_save=f_paths["COLLECTIVE_Q"])
                return q

        target_id = {"pi": target_pi, "si": si}
        pointer_id = {"pi": reply_to_id, "si": reply_to_si}
        print("try q3 generate ", target_pi, si)
        q4 = question_generator.same_category_q_generator(TFIDF_pp=TFIDF_pp, parent=pointer_id, child=target_id, \
                                                          th_title=thread.title, f_mrph=f_paths["MRPH_ANALYSIS"], \
                                                          f_same=f_paths["SAME_CATEGORY_Q_TEMPLATES"])
        if q4:
            q = {"q1": target_pi, "si": si, "q_body": q4}
            #_save_and_call_q(pi=target_pi, si=si, q_body=q4, fn_postapi=f_paths["POST_API"], f_save=f_paths["COLLECTIVE_Q"])
            return q
        else:
            print("    it is my fault")
    return False
