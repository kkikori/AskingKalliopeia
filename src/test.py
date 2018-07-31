import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import datetime as dt

FACILITATER_ID = 24
except_usr_id = ["unagi", "maguro", "saba", "iwashi", "aji", "shirauo", "facilitator", "structure_estimator"]
except_usr_id = [18, 19, 20, 21, 22, 23, 24, 25]
fn_path = "/Users/ida/Desktop/0723_resutls/threads/"

start_time = "2018-07-23T07:20:00"
finish_time = "2018-07-23T08:20:00"

start_t = dt.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
finish_t = dt.datetime.strptime(finish_time, "%Y-%m-%dT%H:%M:%S")
five_min = dt.timedelta(minutes=5)


def _except_others(pi_list, Post_list):
    pi_except_other_list = []
    for pi in pi_list:
        if Post_list[pi].user_id in except_usr_id:
            continue
        pi_except_other_list.append(pi)
    return pi_except_other_list


def _comment_nums(Thread_list, Post_list, group_n):
    names_label = []
    coms = []
    for th_i, thread in Thread_list.items():
        names_label.append(thread.title)
        pi_except_other_list = _except_others(thread.pi_list, Post_list)
        coms.append(len(pi_except_other_list))

    coms = np.array(coms)
    plt.bar(list(range(len(coms))), coms, tick_label=names_label, align="center")
    plt.title(group_n)
    plt.ylim(0, 70)
    plt.xticks(list(range(len(coms))), names_label, rotation=70)
    plt.savefig(fn_path + group_n + "_comment_num" + ".png")
    plt.show()

    print("最大値,", coms.max())
    print("最小値,", coms.min())
    print("合計コメント数", coms.sum())
    print("スレッド数", len(coms))
    print("平均", coms.sum() / len(coms))
    print("分散", coms.var())
    coms = list(coms)
    coms.remove(0)
    try:
        coms.remove(0)
    except:
        coms = coms
    print("平均,", sum(coms) / len(coms))


def _temporal_sequence_extract(thread, Post_list):
    # startからfilishまで5分刻みで投稿の個数を数える
    nums = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], \
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

    for pi in thread.pi_list:

        num_i = 0
        while num_i < len(nums):
            limit_t = start_t + five_min * (num_i + 1)
            if Post_list[pi].created_at < limit_t:
                if Post_list[pi].user_id in except_usr_id:
                    nums[num_i][1] += 1
                else:
                    nums[num_i][0] += 1
                break
            num_i += 1

    nums[11][0] += nums[12][0]
    nums[11][1] += nums[12][1]
    nums.pop(-1)

    return np.array(nums)


def _check_start(counts):
    height = list(counts[:, 0])
    print(height)

    for i, post_num in enumerate(height):
        if post_num == 0:
            continue
        r_height = height[i:]
        print("r_height", r_height)
        r_left = list(range(i, len(height)))
        print("r_left  ", r_left)
        if len(r_height) != len(r_left):
            print("you cannot list")
            return False
        return r_left, r_height
    return False


def _time_series(Thread_list, Post_list, group_n):
    # 抽出
    thread_post_nums = []
    titles = []
    for th_i in range(1, len(Thread_list)):
        thread = Thread_list[th_i]
        print(" title", thread.title)
        thread_post_nums.append(_temporal_sequence_extract(thread, Post_list))
        titles.append(thread.title)

    # とりあえず表示
    # 折れ線グラフを出力

    for th_i, counts in enumerate(thread_post_nums):
        thread = Thread_list[th_i + 1]

        left, height = _check_start(counts)
        plt.plot(left, height, label=thread.id)
        plt.plot(left[0], height[0], 'o')


    plt.xticks(list(range(len(thread_post_nums))),
               ["2018/07/23 \n 16:20", "", "16:30", "", "16:40", "", "16:50", "", "17:00", "", "17:10", "", "17:20"], )
    plt.legend()
    plt.show()


def thread_analysis_main(Thread_list, Post_list, group_n):
    # _comment_nums(Thread_list, Post_list, group_n)
    _time_series(Thread_list, Post_list, group_n)
