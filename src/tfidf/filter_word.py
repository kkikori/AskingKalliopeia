import re

# ストップワードと数字を省く
def filter_word_from_wordlists_per_p(wordlists_per_s, stop_word_list):
    return_words = []
    numeric = r"[0-9]+"
    for wordlist in wordlists_per_s:
        for word in wordlist:
            if not re.match(numeric, word) and (word not in stop_word_list):
                return_words.append(word)
    return return_words

# 構文木から単語列を抽出
# phs:構造木、pos_l:抽出対象の品詞
def extract_words(phs, pos_l):
    words = []
    for pi, p in phs.items():
        for word in p.words:
            if word.pos in pos_l:
                words.append(word.base)
    return words

# 辞書型のときに使う
# phs:dict型、pos_l:抽出対象の品詞
def _extract_words(phs, pos_l):
    words = []
    for pi, p in enumerate(phs):
        for word in p["words"]:
            if word["pos"] in pos_l:
                words.append(word["base"])
    return words


# ストップワードと数字を省く
def filter_word(phs, pos_l, stop_word_list):
    return_words = []
    numeric = r"[0-9]+"

    if not phs:
        return return_words
    if type(phs) == list :
        words = _extract_words(phs=phs, pos_l=pos_l)
    else:
        words = extract_words(phs=phs, pos_l=pos_l)
    for word in words:
        if not re.match(numeric, word) and (word not in stop_word_list):
            return_words.append(word)
    return return_words
