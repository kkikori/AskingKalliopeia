class WordClass():
    """それぞれの単語(形態素)を意味するクラス"""

    def __init__(self, surface=None, base=None, yomi=None, pos=None, pos_detail=None, descriptions=None, category=None,
                 domain=None, another=None, proper_noun=None, original_words=None):
        self.surface = None  # 表層形
        self.base = None  # 基本形
        self.yomi = None  # 読み
        self.pos = None  # 品詞
        self.pos_detail = None  # 品詞の詳細
        self.descriptions = None  # 代表表記
        self.category = None  # 意味カテゴリ
        self.domain = None  # ドメイン
        if another:
            self.another = another
        else:
            self.another = ""  # (代表表記,意味カテゴリ,ドメイン)以外の形態素情報
        self.proper_noun = None  # 固有名詞
        self.original_words = None
