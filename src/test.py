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
        n_str = now_time.strftime("%Y-%m-%dT%H:%M:%S")
        now_time = dt.datetime.strptime(n_str, "%Y-%m-%dT%H:%M:%S")
    print("now_time", now_time)

    # ファイルパスの準備
    f_paths = preparate_file_paths()

    # アクセストークンの準備
    print("access")
    ACCESS_TOKEN = {"name": "facilitator", "password": "test"}
    token = toKalliopeia.get_access_token(ACCESS_TOKEN["name"], ACCESS_TOKEN["password"])

    # スレッドデータをとってくる
    print("thread")
    threads_data = toKalliopeia.get_threads_data(token=token)
    users_data = toKalliopeia.get_users_data(token=token)

    # ファシリテータのid
    print("ファシリテータのid")
    facilitator_i = toKalliopeia.read_user_id(users_data, ACCESS_TOKEN["name"])



    toKalliopeia.create_post_main(fn=f_paths["POST_API"], token=token)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        debug = True
    else:
        debug = False
    main(DEBUG=debug)
