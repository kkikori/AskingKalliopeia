import sys
import csv
import datetime as dt
import mynlp, preparation


# def _has_premise(thread):
#     # 主張、前提の矢印を矢印の先のpostに格納する
#     for list_pi, post in enumerate(thread.posts_list):
#         for list_si, sentence in enumerate(post.sentences):
#             if not sentence.related_to:
#                 continue
#             if sentence.related_to in post.si_list:
#                 relate_si = post.si_list.index(sentence.related_to)
#                 thread.posts_list[list_pi].sentences[relate_si].has_premise.append(sentence.id)
#             else:
#                 relate_pi = thread.pi_list.index(post.reply_to_id)
#                 relate_si = thread.posts_list[relate_pi].si_list.index(sentence.related_to)
#                 thread.posts_list[relate_pi].sentences[relate_si].has_claim.append(sentence.id)
#     return


def _has_premise(thread, Post_list):
    for pi in thread.pi_list:
        post = Post_list[pi]
        for list_si, sentence in enumerate(post.sentences):
            if not sentence.related_to:
                continue
            if sentence.related_to in post.si_list:
                relate_si = post.si_list.index(sentence.related_to)
                Post_list[pi].sentences[relate_si].has_premise.append(sentence.id)
            else:
                relate_pi = post.reply_to_id
                relate_si = Post_list[relate_pi].si_list.index(sentence.related_to)
                Post_list[relate_pi].sentences[relate_si].has_claim.append(sentence.id)
    return

def _time_seikei(s):
    #t = s.split(".")
    return dt.datetime.strptime(s[:-1], "%Y-%m-%dT%H:%M:%S.%f")

def _preparate_per_thread(original_th, Post_list):
    pi_list = []
    for o_p in original_th["posts"]:
        sentences = []
        si_list = []

        tt = _time_seikei(o_p["updated_at"])
        for sentence in o_p["sentences"]:
            new_s = preparation.SentenceClass(si=sentence["id"], body=sentence["body"],
                                              related_to=sentence["related_to"],
                                              component_type=sentence["component_type"])
            sentences.append(new_s)
            si_list.append(new_s.id)
            s_t = _time_seikei(sentence["updated_at"])
            if tt < s_t:
                tt = s_t

        new_p = preparation.PostClass(pi=o_p["id"], \
                                      created_at=o_p["created_at"], \
                                      updated_at=tt, \
                                      body=o_p["body"], \
                                      reply_to_id=o_p["in_reply_to_id"], \
                                      user_id=o_p["user"], \
                                      sentences=sentences, \
                                      si_list=si_list, \
                                      belong_th_i=original_th["id"]
                                      )
        pi_list.append(new_p.id)
        Post_list[new_p.id] = new_p
        thread = preparation.ThreadClass(original_th["id"], original_th["title"], pi_list, pi_list[-1])

        _has_premise(thread, Post_list)
    return thread


# 1回以上投稿しているユーザのリストを返す
def _preparate_users(users):
    User_list = {}
    for usr in users:
        pi_list = []
        for post in usr["posts"]:
            pi_list.append(post["id"])

        new_user = preparation.UserClass(ui=usr["id"], name=usr["name"], \
                                         display_name=usr["display_name"], role=usr["role"], \
                                         pi_list=pi_list)
        if len(new_user.pi_list) > 0:
            User_list[usr["id"]] = new_user
    return User_list


def _previous_qs(Threads_list, Post_list, User_list, f_individual, f_collective):
    # 過去に問いかけしたデータを読み込む
    if not f_individual.exists():
        print("[FILE ERROR]", f_individual, "is not found.")
        sys.exit()

    with f_individual.open("r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            usr_i = Post_list[int(row[0])].user_id
            User_list[usr_i].previousQ_list.append(int(row[0]))

    if not f_collective.exists():
        print("[FILE ERROR]", f_collective, "is not found.")
        sys.exit()
    with f_collective.open("r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            th_i = Post_list[int(row[0])].belong_th_i
            Threads_list[th_i].previousQ_list.append(int(row[0]))


def preparate_main(fn_paths, threads, users):
    # スレッドを用意
    Threads_list = {}
    Post_list = {}
    for thread in threads:
        Threads_list[thread["id"]] = _preparate_per_thread(thread, Post_list)

    # ユーザリストを用意
    User_list = _preparate_users(users)

    _previous_qs(Threads_list=Threads_list, Post_list=Post_list, User_list=User_list, \
                 f_individual=fn_paths["INDIVIDUAL_Q"], \
                 f_collective=fn_paths["COLLECTIVE_Q"])

    return Threads_list, Post_list, User_list
