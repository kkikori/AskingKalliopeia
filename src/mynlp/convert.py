import pyknp
from collections import OrderedDict
import mynlp

"""
合成語に対応する
名詞　+ 名詞 →　名詞
名詞　+ 動詞　→　動詞
名詞 + 名詞性名詞接尾辞 →　名詞
名詞 + 形容詞性名詞接尾辞　→　形容詞
名詞 + 動詞性接尾辞　→　動詞
ナorイ形容詞接頭辞　+ 名詞　→　形容詞
"""


# 文からPhraseのツリーを生成
def _knp(sentence):
    if sentence == "":
        return None

    knp = pyknp.KNP()
    try:
        result = knp.parse(sentence)
    except:
        return None

    # 情報をクラスに格納
    phrases = OrderedDict()  # 文節クラスのディクショナリ
    for bnst in result.bnst_list():
        ph = mynlp.PhraseClass(parent_id=bnst.parent_id, dpndtype=bnst.dpndtype)

        # この文節にふくまれる単語情報を格納
        for mrph in bnst.mrph_list():  # mrph_list:文節内の形態素リスト
            word = mynlp.WordClass(surface=mrph.midasi, base=mrph.genkei, yomi=mrph.yomi)

            # 品詞関連詳細情報
            pos_info = mrph.spec().split(" ")  # or .new_spec()
            # 表層形 読み 見出し語 品詞大分類 品詞大分類ID 品詞細分類 品詞細分類ID 活用型 活用型ID 活用形 活用形ID 意味情報
            word.pos = pos_info[3]  # 品詞
            word.pos_detail = pos_info[5]  # 品詞細分類

            # 意味情報関連
            imis = mrph.imis.split()  # 代表表記,漢字読み,カテゴリなど
            for imi in imis:
                if "代表表記" in imi:
                    word.descriptions = imi.split(":", 1)[-1]
                elif "カテゴリ" in imi:
                    word.category = imi.split(":", 1)[-1]
                elif "ドメイン" in imi:
                    word.domain = imi.split(":", 1)[-1]
                elif ("人名:" in imi) or ("地名:" in imi):  # 固有名詞
                    word.proper_noun = imi.split(":", 1)[-1]
                else:
                    word.another = word.another + imi + " "

            ph.words.append(word)

        phrases[bnst.bnst_id] = ph

    for ph_i, ph in phrases.items():
        if ph.parent_id != -1:
            phrases[ph.parent_id].children.append(ph_i)

    return phrases


def convert(sentence, combine=True):
    # 構文木を返す
    phs = _knp(sentence=sentence)

    # knpでエラーが出た場合
    if not phs:
        return None

    # 合成処理をしない場合
    if not combine:
        return phs

    new_phs = {}  # 新しい結果を格納
    for ph_i, ph in phs.items():
        new_phs[ph_i] = ph

        o_words = ph.words  # その文節の単語クラスのリスト
        new_words = [o_words[-1]]
        oi = len(o_words) - 2

        # o_words[oi] == new_words[0]の一個まえの単語になるようにoiを動かす
        while oi > -1:
            n_w = new_words[0]
            # 合成する可能性がない場合
            if n_w.pos not in ["接尾辞", "名詞", "形容詞"] and not (n_w.base == "する" and o_words[oi].pos == "名詞"):
                new_words.insert(0, o_words[oi])
                oi -= 1
                continue

            """品詞ごとに合成するかどうか判定(合成しない場合はcontinueで抜ける)"""
            if n_w.pos == "名詞":
                # 合成しない場合
                if o_words[oi].pos not in ["名詞", "接頭辞", "動詞", "形容詞"]:
                    new_words.insert(0, o_words[oi])
                    oi -= 1
                    continue

                if o_words[oi].pos_detail == "ナ形容詞接頭辞":
                    new_words[0].pos = "形容詞"
                    new_words[0].pos_detail = "ナ形容詞"
                elif o_words[oi].pos_detail == "イ形容詞接頭辞":
                    new_words[0].pos = "形容詞"
                    new_words[0].pos_detail = "イ形容詞"
            elif n_w.pos == "形容詞":
                # 合成しない場合
                if o_words[oi].pos not in ["名詞", "形容詞", "接頭辞"]:
                    new_words.insert(0, o_words[oi])
                    oi -= 1
                    continue
            elif n_w.pos == "接尾辞":
                if n_w.pos_detail in ["名詞性名詞接尾辞", "名詞性述語接尾辞"]:
                    new_words[0].pos = "名詞"
                    new_words[0].pos_detail = "*"

                elif n_w.pos_detail == "動詞性接尾辞":
                    # 「思っています」とかは「思い＋ます」のままにしとく
                    if o_words[oi].pos == "動詞":
                        new_words.insert(0, o_words[oi])
                        oi -= 1
                        continue
                    else:
                        new_words[0].pos = "動詞"
                        new_words[0].pos_detail = "*"
                elif n_w.pos_detail in ["形容詞性名詞接尾辞", "形容詞性述語接尾辞"]:
                    new_words[0].pos = "形容詞"
                    new_words[0].pos_detail = "*"
                else:
                    # if o_words[oi].pos != "接尾辞":
                    # print("compounder error", "*" * 1000)
                    # mynlp.print_details(phs)
                    new_words[0].pos = o_words[oi].pos
                    new_words[0].pos_detail = o_words[oi].pos_detail

            """合成があった場合の共通の処理"""
            new_words[0].original_words.extend([o_words[oi].base, new_words[0].base])
            # baseとsurfaceのいじる順番を変えちゃダメ
            new_words[0].base = o_words[oi].surface + new_words[0].base
            new_words[0].surface = o_words[oi].surface + new_words[0].surface
            new_words[0].yomi = o_words[oi].yomi + new_words[0].yomi

            try:
                new_words[0].descriptions = new_words[0].descriptions + "," + o_words[oi].descriptions
            except:
                if o_words[oi].descriptions:
                    new_words[0].descriptions = o_words[oi].descriptions
            try:
                new_words[0].cateegory = new_words[0].category.extend(o_words[oi].category)
            except:
                if o_words[oi].category:
                    new_words[0].cateegory = o_words[oi].category
            try:
                new_words[0].domain = new_words[0].domain.extend(o_words[oi].domain)
            except:
                if o_words[oi].domain:
                    new_words[0].domain = o_words[oi].domain
            try:
                new_words[0].another = new_words[0].another.extend(o_words[oi].another)
            except:
                if o_words[oi].domain:
                    new_words[0].domain = o_words[oi].domain
            try:
                new_words[0].another = new_words[0].another.extend(o_words[oi].another)
            except:
                if o_words[oi].another:
                    new_words[0].another = o_words[oi].another
            try:
                new_words[0].proper_noun = new_words[0].proper_noun.extend(o_words[oi].proper_noun)
            except:
                if o_words[oi].proper_noun:
                    new_words[0].proper_noun = o_words[oi].proper_noun
            oi -= 1
        new_phs[ph_i].words = new_words

    return new_phs
