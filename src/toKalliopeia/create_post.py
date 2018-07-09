import simplejson as json
from .fetch_api import create_post


def _post_post(f, token):
    ff = f.open("r")
    jsonData = json.load(ff)
    data = {}
    data = {"body": jsonData["body"],
            "in_reply_to_id": jsonData["in_reply_to_id"]}
    create_post(token=token, data=data)

    f.unlink()


def create_post_main(fn, token):
    # ファイルないの投稿をすべて投稿し、ファイルを空にする
    print("create_post")
    f_lists = list(fn.glob("*.json"))
    for f in f_lists:
        _post_post(f, token)
        f.unlink()
