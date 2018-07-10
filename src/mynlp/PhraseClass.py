class PhraseClass():
    """それぞれの文節を意味するクラス"""

    def __init__(self, parent_id=None, parent=None, children=None, words=None, dpndtype=None):
        # self.id = None  # この文節のID
        self.parent_id = parent_id  # この文節の親文節のID
        self.parent = parent  # この文節の親文節
        if children:
            self.children = children  # この文節の子文節たち
        else:
            self.children = []
        if words:
            self.words = words
        else:
            self.words = []  # この文節に含まれている単語
        if dpndtype:
            self.dpndtype = dpndtype
        else:
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
