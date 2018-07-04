from __future__ import unicode_literals
import re
import unicodedata


def unicode_normalize(cls, s):
    pt = re.compile('([{}]+)'.format(cls))

    def norm(c):
        return unicodedata.normalize('NFKC', c) if pt.match(c) else c

    s = ''.join(norm(x) for x in re.split(pt, s))
    return s


def remove_extra_spaces(s):
    s = re.sub('[ 　]+', ' ', s)
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                      '\u3040-\u309F',  # HIRAGANA
                      '\u30A0-\u30FF',  # KATAKANA
                      '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                      '\uFF00-\uFFEF'  # HALFWIDTH AND FULLWIDTH FORMS
                      ))
    basic_latin = '\u0000-\u007F'

    def remove_space_between(cls1, cls2, s):
        p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
        while p.search(s):
            s = p.sub(r'\1\2', s)
        return s

    s = remove_space_between(blocks, blocks, s)
    s = remove_space_between(blocks, basic_latin, s)
    s = remove_space_between(basic_latin, blocks, s)
    return s


def normalize_neologd(s):
    s = s.strip()
    s = unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)

    def maketrans(f, t):
        return {ord(x): ord(y) for x, y in zip(f, t)}

    #jumanの場合
    s = s.translate(
        maketrans('"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
                  '”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))
    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
    s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    s = remove_extra_spaces(s)
    s = re.sub('[’]', '\'', s)
    s = re.sub('[”]', '', s)
    s = re.sub(r"(http://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)", '', s)  # url削除
    s = re.sub(r"\([\d\s\wぁ-んァ-ヶ亜-熙]*\)", "", s)  # 括弧書き中削除
    s = s.replace("\t","")
    s = re.sub(r"!+", "!", s)
    s = s.replace(" ", "　")
    return s.lower()


def normalize_main(ss):
    assert "0123456789" == normalize_neologd("０１２３４５６７８９")
    assert "abcdefghijklmnopqrstuvwxyz" == normalize_neologd("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ")
    assert "abcdefghijklmnopqrstuvwxyz" == normalize_neologd("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")
    assert "＝。、・「」" == normalize_neologd("＝。、・「」")
    assert "ハンカク" == normalize_neologd("ﾊﾝｶｸ")
    assert "o-o" == normalize_neologd("o₋o")
    assert "majikaー" == normalize_neologd("majika━")
    assert "わい" == normalize_neologd("わ〰い")
    assert "スーパー" == normalize_neologd("スーパーーーー")
    assert "ゼンカクスペース" == normalize_neologd("ゼンカク　スペース")
    assert "おお" == normalize_neologd("お             お")
    assert "おお" == normalize_neologd("      おお")
    assert "おお" == normalize_neologd("おお      ")
    assert "アルゴリズムc" == normalize_neologd("アルゴリズム C")
    assert "prml副読本" == normalize_neologd("　　　ＰＲＭＬ　　副　読　本　　　")
    assert "coding　the　matrix" == normalize_neologd("Coding the Matrix")


    ss = normalize_neologd(ss)

    return ss
