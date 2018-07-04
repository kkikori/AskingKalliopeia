from collections import defaultdict


class Case_frame():
    def __init__(self, noun):
        self.noun = noun
        self.pairs = []

    def search_just_same(self, t_pair):
        r_p = []
        for pair in self.pairs:
            if pair.th_i == t_pair.th_i or pair.u_i == t_pair.u_i:
                continue
            if pair.particle == t_pair.particle and pair.predicate == t_pair.predicate:
                r_p.append(pair)
        if len(r_p) == 0:
            return None
        return r_p

    def appear_thread_num(self):
        # nounが現れるスレッドを取得
        # {thread_id : そのスレッド内での出現数}を返す
        threads = defaultdict(int)
        for pair in self.pairs:
            threads[pair.th_i] += 1
        return threads

    def search_same_category(self, t_pair):
        # 同じカテゴリかつ違うスレッドのペアをリストで返す
        if not t_pair.category:
            return None
        r_p = []
        for pair in self.pairs:
            if pair.th_i == t_pair.th_i or pair.u_i == t_pair.u_i:
                continue
            if pair.category == t_pair.category:
                r_p.append(pair)
        if len(r_p) == 0:
            return None
        return r_p

    def search_same_particle(self, t_pair):
        # 同じ助詞かつ違うスレッドのペアをリストで返す
        r_p = []
        for pair in self.pairs:
            if pair.th_i == t_pair.th_i or pair.u_i == t_pair.u_i:
                continue
            if pair.predicate == t_pair.predicate:
                r_p.append(pair)

        if len(r_p) == 0:
            return None
        return r_p
