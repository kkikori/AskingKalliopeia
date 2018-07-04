import sys
import json
import datetime
import csv
import mynlp, preparation


def _preparate_per_thread(fr, POSTS, THREADS, USERS):
    # スレッドごとにクラスに格納
    if not fr.is_file():
        print("[file error]", fr.name, "is not found.")
        return []

    f = fr.open("r")
    jsonData = json.load(f)
    post_list = jsonData["posts"]
    th_title = jsonData["title"]

    thread = preparation.THREAD()
    th_i = int(fr.parent.name)
    thread.title = th_title

    for j_post in post_list:
        post = preparation.POST()
        if not j_post["parent_id"]:
            post.parent_id = -1
        else:
            post.parent_id = int(j_post["parent_id"])
        post.created_at = datetime.datetime.strptime(j_post["created_at"], "%Y/%m/%d %H:%M:%S")
        post.theread_id = th_i
        post.user_id = j_post["user_id"]

        for j_s in j_post["sentences"]:
            s = preparation.SENTENCE()
            s.id = j_s["id"]
            s.body = j_s["body"]
            s.tag = j_s["component_type"]
            s.pointer_post_id = j_s["link_post_id"]
            s.pointer_sentence_id = j_s["link_sentence_id"]
            s.reltag = j_s["stance_type"]
            post.sentences.append(s)
        POSTS[j_post["id"]] = post
        thread.posts.append(j_post["id"])
        if post.parent_id < 0:
            thread.parent = post.parent_id

        if post.user_id not in USERS.keys():
            USERS[post.user_id] = preparation.PersonClass(post.user_id)
        USERS[post.user_id].post_id_list.append(j_post["id"])

    THREADS[th_i] = thread


def _has_premise(POSTS):
    # 主張、前提の矢印を矢印の先のpostに格納する
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


def preparate_main(fn_paths):
    print("c")
    POSTS = {}
    THREADS = {}
    USERS = {}

    # 全スレッドのパスを取得
    files = []
    files = [x for x in fn_paths["THREAD_CLASSIFIED"].iterdir() if x.is_dir()]

    for fn in files:
        _preparate_per_thread(fr=fn / "classified.json", POSTS=POSTS, THREADS=THREADS, USERS=USERS)
        _has_premise(POSTS=POSTS)

    _previous_qs(THREADS=THREADS, POSTS=POSTS, USERS=USERS, f_individual=fn_paths["INDIVIDUAL_Q"], \
                 f_collective=fn_paths["COLLECTIVE_Q"])

    return POSTS, THREADS, USERS
