# ユーザクラス
class UserClass():
    def __init__(self, ui, name, display_name, role):
        self.id = ui
        self.name = name
        self.display_name = display_name
        self.role = role
        self.pi_list = []  # {"thi":th_i,"pi":pi} を一要素とするリスト
