def create_stop_word_list(path_stopword):
    table = []
    for row in path_stopword.open('r'):
        tt = row.rstrip("\n")
        table.append(tt)
    return table
