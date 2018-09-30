import re
import question_generator

r_question = r"\?$|？$|でしょうか"


def _judge_user_term(post, usr, now_time, thresholds):
    if (now_time - post.created_at) < thresholds["t_user"]:
        print("     time setting", post.created_at)
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


def to_individual_q(user, target_pi, post, now_time, f_paths, TFIDF_pp, thresholds, facilitator_i):
    print("   user", user.name, len(user.pi_list))
    # no_premise_qがダメだった場合のみ、q2が起動
    # どちらか問いかけが生成された場合はTrue、失敗した場合はFalseを返す

    # ファシリテータは対象外
    if user.id == facilitator_i:
        print("        it is facilitator ")
        return False

    judge = _judge_user_term(post=post, usr=user, now_time=now_time, thresholds=thresholds)
    if not judge:
        print("   judge is not")
        return False

    # print("         ",post.sentences[-1])
    for si, s in enumerate(post.sentences):
        print("        ", s.body)
        if s.component_type != "CLAIM":
            continue
            print("     not claim")
        if re.search(r_question, s.body):
            print("      re,search")
            # 質問文は除く措置
            continue
        if len(s.body) < 7:
            print("      short", s.body)
            continue

        q1 = question_generator.no_premise_q_generator(post=post, pi=target_pi, s=s, si=si,
                                                       fn_templates=f_paths["NO_PREMISE_Q_TEMPLATES"], \
                                                       fn_mrph=f_paths["MRPH_ANALYSIS"])

        if q1:
            q = {"pi": target_pi, "si": si, "q_body": q1}
            return q
        else:
            print("       it is my fault")
            # q2 = question_generator.over_thread_q_generator(THREAD=)

    return False
