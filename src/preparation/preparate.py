import sys
import json
import datetime
import csv
import mynlp, preparation


def _has_premise(thread):
    # 主張、前提の矢印を矢印の先のpostに格納する
    for list_pi, post in enumerate(thread.posts_list):
        for list_si, sentence in enumerate(post.sentences):
            if not sentence.related_to:
                continue
            if sentence.related_to in post.si_list:
                relate_si = post.si_list.index(sentence.related_to)
                thread.posts_list[pi].sentences[si].has_premise.append()

    for pi, post in POSTS.items():
        for si, s in enumerate(post.sentences):
            if not s.pointer_post_id:
                continue
            ppi = s.pointer_post_id
            psi = s.pointer_sentence_id
            reltag = s.reltag
            if pi == ppi:
                POSTS[ppi].sentences[psi].has_premise.append([pi, si, reltag])
            else:
                POSTS[ppi].sentences[psi].has_claim.append([pi, si, reltag])


def _preparate_per_thread(original_th):
    pi_list = []
    posts_list = []

    for o_p in original_th["posts"]:
        sentences = []
        si_list = []
        for sentence in o_p["sentences"]:
            new_s = preparation.SentenceClass(si=sentence["id"], body=sentence["body"],
                                              related_to=sentence["related_to"],
                                              component_type=sentence["component_type"])
            sentences.append(new_s)
            si_list.append(new_s.id)

        new_p = preparation.PersonClass(pi=o_p["id"], \
                                        created_at=o_p["created_at"], \
                                        body=o_p["body"], \
                                        reply_to_id=o_p["in_reply_to_id"], \
                                        user_id=o_p["user"],
                                        sentences=sentences,
                                        si_list=si_list
                                        )
        pi_list.append(new_p.id)
        posts_list.append(new_p)
    thread = preparation.ThreadClass(original_th["id"], original_th["title"], posts_list, pi_list, pi_list[-1])

    _has_premise(thread=thread)
    return thread


def _previous_qs(THREADS, POSTS, USERS, f_individual, f_collective):
    # 過去に問いかけしたデータを読み込む
    if not f_individual.exists():
        print("[FILE ERROR]", f_individual, "is not found.")
        sys.exit()

    with f_individual.open("r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            usr_i = POSTS[int(row[0])].user_id
            USERS[usr_i].previous_qs.append(int(row[0]))

    if not f_collective.exists():
        print("[FILE ERROR]", f_collective, "is not found.")
        sys.exit()
    with f_collective.open("r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            th_i = POSTS[int(row[0])].theread_id
            THREADS[th_i].previous_qs.append(int(row[0]))


def preparate_main(fn_paths, threads):
    THREADS = []
    USERS = {}

    for thread in threads:
        _preparate_per_thread(thread)

    _previous_qs(THREADS=THREADS, POSTS=POSTS, USERS=USERS, f_individual=fn_paths["INDIVIDUAL_Q"], \
                 f_collective=fn_paths["COLLECTIVE_Q"])

    return POSTS, THREADS, USERS
