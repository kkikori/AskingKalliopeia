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
    fn = "file_paths.json"
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
    if DEBUG:
        # 20 2016-12-12 17:12:22
        # 40 2016-12-12 22:12:06
        # 60 2016-12-13 05:46:42
        # 80 2016-12-13 12:49:52
        # 100 2016-12-13 19:59:17
        # 120 2016-12-13 22:38:35
        # 140 2016-12-14 06:28:28
        # 160 2016-12-14 15:26:22
        # 180 2016-12-14 18:33:13
        # 200 2016-12-15 01:26:53
        # 220 2016-12-15 13:06:51
        # 240 2016-12-15 16:49:28
        # 260 2016-12-15 20:09:14
        t = "2016-12-13 05:46:42"
        now_time = dt.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
    else:
        now_time = dt.datetime.now(pytz.utc)
    print("now_time", now_time)
    f_paths = preparate_file_paths()

    ACCESS_TOKEN = {"name": "inu", "password": "test"}
    token = toKalliopeia.get_access_token(ACCESS_TOKEN["name"], ACCESS_TOKEN["password"])
    # スレッドデータをとってくる
    threads_data = toKalliopeia.get_threads_data(token=token)

    # 形態素解析部
    if DEBUG:
        print("*" * 10, "Mrph_analysis", "*" * 20)
    new_post_phs = morphological_analysis.Mrph_analysis_main(threads_data=threads_data,
                                                             fn_MrphAnalysis=f_paths["MRPH_ANALYSIS"],
                                                             fn_PastPostList=f_paths["PAST_POST_LIST"])
    if DEBUG:
        print("*" * 10, "TFIDF", "*" * 20)
    TFIDF_pp = tfidf.TFIDF_pp(f_dict=f_paths["DICTIONARY"], f_words=f_paths["WORD_LIST"], \
                              f_stopw=f_paths["STOP_WORD"], f_mrph=f_paths["MRPH_ANALYSIS"])
    if len(new_post_phs) > 0:
        for p_phs in new_post_phs:
            TFIDF_pp.add_post_words(p_phs=p_phs)

        TFIDF_pp.overwrite_dic()

    if DEBUG:
        print("*" * 10, "preparation", "*" * 20)
    # 問いかけの準備
    THREAD, USERS = preparation.preparate_main(fn_paths=f_paths, threads=threads_data)

    if DEBUG:
        print("*" * 10, "question generate", "*" * 20)
    # 問いかけ生成
    question_generator.q_generator_main(POSTS=POSTS, THREAD=THREAD, USERS=USERS, f_paths=f_paths, TFIDF_pp=TFIDF_pp,
                                        now_time=now_time)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        debug = True
    else:
        debug = False
    main(DEBUG=debug)
