class WordClass():
    """それぞれの単語(形態素)を意味するクラス"""

    def __init__(self, surface=None, base=None, yomi=None, pos=None, pos_detail=None, \
                 descriptions=None, category=None, domain=None, \
                 another=None, proper_noun=None, original_words=None):
        self.surface = surface  # 表層形
        self.base = base  # 基本形
        self.yomi = yomi  # 読み
        self.pos = pos  # 品詞
        self.pos_detail = pos_detail  # 品詞の詳細
        self.descriptions = descriptions  # 代表表記
        self.category = category  # 意味カテゴリ
        self.domain = domain  # ドメイン
        if another:
            self.another = another
        else:
            self.another = ""  # (代表表記,意味カテゴリ,ドメイン)以外の形態素情報
        self.proper_noun = proper_noun  # 固有名詞
        if original_words:
            self.original_words = original_words
        else:
            self.original_words = []
