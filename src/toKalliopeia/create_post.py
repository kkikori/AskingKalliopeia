import simplejson as json


def _post_post(f):
    ff = f.open("r")
    jsonData = json.load(ff)


    f.unlink()

def create_post_main(fn):
    # ファイルないの投稿をすべて投稿し、ファイルを空にする
    print("create_post")
    f_lists = list(fn.glob("*.json"))
    for f in f_lists:
        _post_post(f)