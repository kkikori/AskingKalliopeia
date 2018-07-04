class ThreadClass():
    def __init__(self, th_i, title):
        self.id = th_i
        self.title = title  # 親投稿のタイトル
        self.parent_id = None  # 親投稿ポストのid
        self.pi_list = []
        self.posts_list = []  # ポストのidリスト
        self.parent_words = []  # 親投稿の単語リスト(名詞,形容詞,動詞,形容動詞)
        self.previousQ_list = []
