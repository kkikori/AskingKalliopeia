# 投稿内の文ごとのクラス
class SentenceClass():
    def __init__(self, si, body, related_to, component_type):
        self.id = si
        self.body = body  # row sentence(str)
        self.related_to = related_to
        self.component_type = component_type

        self.has_premise = []
        self.has_claim = []
