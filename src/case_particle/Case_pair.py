class case_pair():
    def __init__(self, th_i="", p_i="", s_i="", u_i="", particle="", predicate="", category=""):
        if th_i == "":
            self.th_i = None
        else:
            self.th_i = th_i  # 出現したスレッドid
        if p_i == "":
            self.p_i = None
        else:
            self.p_i = p_i
        if s_i == "":
            self.s_i = None
        else:
            self.s_i = s_i
        if u_i == "":
            self.u_i = None
        else:
            self.u_i = u_i
        self.particle = particle  # 格助詞
        self.predicate = predicate  # 述語
        self.category = category