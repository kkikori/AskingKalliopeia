class ThreadClass():
    def __init__(self, th_i, title, posts_list=None, pi_list=None, parent_id=None):
        self.id = th_i
        self.title = title  # 親投稿のタイトル

        if not parent_id:
            self.parent_id = None  # 親投稿ポストのid
        else:
            self.parent_id = parent_id

        if not pi_list:
            self.pi_list = []
        else :
            self.pi_list = pi_list

        if not posts_list:
            self.posts_list = []  # ポストのidリスト
        else :
            self.posts_list = posts_list

        self.parent_words = []  # 親投稿の単語リスト(名詞,形容詞,動詞,形容動詞)
        self.previousQ_list = []
