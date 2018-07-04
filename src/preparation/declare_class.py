class THREAD():
    def __init__(self):
        self.title = ""  # 親投稿のタイトル
        self.posts = []  # ポストのidリスト
        self.parent = None  # 親投稿ポストのid
        self.parent_words = []  # 親投稿の単語リスト(名詞,形容詞,動詞,形容動詞)
        self.previous_qs = []


# 投稿のクラス
class POST():
    def __init__(self):
        self.sentences = []  # センテンスクラスが格納される
        self.parent_id = ""
        self.created_at = ""
        self.theread_id = ""
        self.user_id = ""
        self.facilitator = False
        # self.depth_in_thread = 0


# 投稿内の文ごとのクラス
class SENTENCE():
    def __init__(self):
        self.id = ""
        self.body = ""  # row sentence(str)
        # self.phrases = []  # result morphological_analysis of sentence
        self.tag = ""  # sentence tag (CLAIM  or PREMISE)
        self.pointer_post_id = ""  # pointer post id
        self.pointer_sentence_id = ""  # pointer sentence id
        self.reltag = ""  # relation tag
        self.has_premise = []
        self.has_claim = []


# ユーザクラス
class PersonClass():
    def __init__(self, name):
        self.username = name
        self.post_id_list = []  # ユーザのコメントIDリスト
        self.post_time_list = []
        self.previous_qs = []
