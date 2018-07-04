# 投稿のクラス
class PostClass():
    def __init__(self, pi, created_at, body, reply_to_id, user_id):
        self.id = pi
        self.created_at = created_at
        self.body = body
        self.reply_to_id = reply_to_id
        self.user_id = user_id

        self.sentences = []
        self.si_list = []
