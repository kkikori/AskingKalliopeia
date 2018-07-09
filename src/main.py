import sys
from pathlib import Path
import datetime as dt
import pytz
import simplejson as json

import morphological_analysis
import preparation
import question_generator
import tfidf
import toKalliopeia


def time_setting(f_path):
    if not f_path.is_file():
        print("[file error]", f_path.name, "is not found.")
        sys.exit()

    f = f_path.open("r")
    jsonData = json.load(f)
    t = dt.timedelta(minutes=int(jsonData["interval_time"]))
    return t


def preparate_file_paths():
    # ファイルパスの準備
    fn = Path("file_paths.json")
    if not fn.is_file():
        print("[file error]", fn.name, "is not found.")
        sys.exit()

    f_paths = {}
    f = fn.open("r")
    jsonData = json.load(f)

    for fgroup in jsonData:
        data_root = fgroup.pop("DATA_ROOT")
        root_path = Path(data_root)
        for fn, fp in fgroup.items():
            f_paths[fn] = root_path / fp
    return f_paths


def main(DEBUG):
    # 現在時刻の取得
    if DEBUG:
        t = "2016-12-13 05:46:42"
        now_time = dt.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
    else:
        now_time = dt.datetime.now(pytz.utc)
    print("now_time", now_time)

    # ファイルパスの準備
    f_paths = preparate_file_paths()

    # アクセストークンの準備
    ACCESS_TOKEN = {"name": "inu", "password": "test"}
    token = toKalliopeia.get_access_token(ACCESS_TOKEN["name"], ACCESS_TOKEN["password"])

    # スレッドデータをとってくる
    threads_data = toKalliopeia.get_threads_data(token=token)
    users_data = toKalliopeia.get_users_data(token=token)

    # ファシリテータのid
    facilitator_i = toKalliopeia.read_user_id(users_data, ACCESS_TOKEN["name"])

    # 形態素解析部
    if DEBUG:
        print("*" * 10, "Mrph_analysis", "*" * 20)
    new_post_phs,new_post_pi = morphological_analysis.Mrph_analysis_main(threads_data=threads_data,
                                                             fn_MrphAnalysis=f_paths["MRPH_ANALYSIS"],
                                                             fn_PastPostList=f_paths["PAST_POST_LIST"])


    if DEBUG:
        print("*" * 10, "TFIDF", "*" * 20)
    print("new_post_phs",new_post_phs)
    TFIDF_pp = tfidf.TFIDF_pp(f_dict=f_paths["DICTIONARY"], f_words=f_paths["WORD_LIST"], \
                              f_stopw=f_paths["STOP_WORD"], f_mrph=f_paths["MRPH_ANALYSIS"])
    if len(new_post_pi) > 0:
        for pi in new_post_pi:
            TFIDF_pp.add_post_words(pi=pi,f= f_paths["MRPH_ANALYSIS"])

        TFIDF_pp.overwrite_dic()

    if DEBUG:
        print("*" * 10, "preparation", "*" * 20)
    # 問いかけの準備
    THREAD, POSTS, USERS = preparation.preparate_main(fn_paths=f_paths, threads=threads_data, users=users_data)

    print("threads", THREAD.keys())
    print("posts", POSTS.keys())
    print("users", USERS.keys())

    if DEBUG:
        print("*" * 10, "question generate", "*" * 20)
    # 問いかけ生成
    question_generator.q_generator_main(POSTS=POSTS, THREAD=THREAD, USERS=USERS, f_paths=f_paths, TFIDF_pp=TFIDF_pp,
                                        now_time=now_time,facilitator_i=facilitator_i)





if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        debug = True
    else:
        debug = False
    main(DEBUG=debug)
