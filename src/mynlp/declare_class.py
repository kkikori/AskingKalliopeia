class Word():
    """それぞれの単語(形態素)を意味するクラス"""

    def __init__(self):
        self.surface = None  # 表層形
        self.base = None  # 基本形
        self.yomi = None  # 読み
        self.pos = None  # 品詞
        self.pos_detail = None  # 品詞の詳細
        self.descriptions = None  # 代表表記
        self.category = None  # 意味カテゴリ
        self.domain = None  # ドメイン
        self.another = ""  # (代表表記,意味カテゴリ,ドメイン)以外の形態素情報
        self.proper_noun = None  # 固有名詞
        self.original_words = None


class Phrase():
    """それぞれの文節を意味するクラス"""

    def __init__(self):
        # self.id = None  # この文節のID
        self.parent_id = None  # この文節の親文節のID
        self.parent = None  # この文節の親文節
        self.children = []  # この文節の子文節たち
        self.words = []  # この文節に含まれている単語
        self.dpndtype = ""  # 係り受けの種類

    def __str__(self):
        ret = ""
        for word in self.words:
            ret = ret + str(word.surface)
        return ret

    # 単語を返す
    def words(self):
        ret = []
        for word in self.words:
            ret.append(word.base)
        return ret

    # 名詞のみ返す
    def nouns(self, category=None):
        ret = []
        if not category:
            for word in self.words:
                if word.pos == "名詞":
                    ret.append(word.base)
            return ret
        for word in self.words:
            if word.pos == "名詞":
                ret.append([word.base, word.category])
        return ret

    # 形容詞のみ返す
    def adjectives(self):
        ret = []
        for word in self.words:
            if word.pos == "形容詞":
                ret.append(word.base)
        return ret