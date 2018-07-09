import csv

from gensim import corpora, models

import mynlp
from tfidf.create_stop_word_list import create_stop_word_list
from tfidf.filter_word import extract_words, filter_word


def _overwrite_words(fn_words, words):
    with fn_words.open("a") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(words)
    f.close()


def _read_words(fn_words):
    with fn_words.open("r") as f:
        reader = csv.reader(f)
        data = [x for x in reader]
    return data


class TFIDF_pp():
    def __init__(self, f_dict, f_words, f_stopw, f_mrph):
        self.stop_word_list = create_stop_word_list(path_stopword=f_stopw)
        self.word_list_per_s = _read_words(fn_words=f_words)
        self.f_words = f_words
        self.f_dict = f_dict
        self.f_mrph = f_mrph
        self.dictionary = corpora.Dictionary.load_from_text(str(f_dict))
        self.courpus_tfidf = ""
        self.texts = []
        self.tfidf_model = ""
        self.corpus = ""
        self.pos_l = ["名詞", "動詞", "形容詞"]

    def add_post_words(self, f, pi):
        p_phs = mynlp.read_mrph_per_post(f, pi)
        # 調べるポストの単語を抽出
        add_words_to_dictionary = []
        for phs in p_phs:
            # 文ごとに単語を抽出（ストップワードは除く）

            wlist = filter_word(phs, self.pos_l, self.stop_word_list)
            add_words_to_dictionary.extend(wlist)

        self.dictionary.add_documents([add_words_to_dictionary])
        self.texts.append(add_words_to_dictionary)
        self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
        self.tfidf_model = models.TfidfModel(self.corpus)
        self.corpus_tfidf = self.tfidf_model[self.corpus]

        # 単語列の保存
        _overwrite_words(fn_words=self.f_words, words=add_words_to_dictionary)

    def calc_tfidf_from_pi(self, pi):
        p_phs = mynlp.read_mrph_per_post(pi=pi, f_path=self.f_mrph)
        wordlist = []
        for phs in p_phs:
            wordlist.extend(extract_words(phs, self.pos_l))

        wordlist = extract_words(phs, self.pos_l)
        wordlist_id = self.dictionary.doc2bow(wordlist)
        tfidf_model = models.TfidfModel(self.corpus)

        return tfidf_model[wordlist_id]

    def calc_tfidf_from_pii(self, pi):
        p_phs = mynlp.read_mrph_per_post(pi=pi, f_path=self.f_mrph)
        wordlist = []
        for phs in p_phs:
            words = filter_word(phs=phs, pos_l=self.pos_l, stop_word_list=self.stop_word_list)
            wordlist.extend(words)

        wordlist_id = self.dictionary.doc2bow(wordlist)
        tfidf_model = models.TfidfModel(self.corpus)

        dic = self.dictionary.token2id
        dic = {v: k for k, v in dic.items()}
        r_scores = {}
        for x in tfidf_model[wordlist_id]:
            r_scores[dic[x[0]]] = x[1]

        return r_scores

    def overwrite_dic(self):
        # 辞書の上書き
        self.dictionary.save_as_text(str(self.f_dict))
