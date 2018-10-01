import csv
import datetime as dt

import toKalliopeia


def _time_seikei(s):
    # print(s)
    t = s.split("+")
    s = t[0]
    # print(s)
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")


def time_comparison(user, targets):
    counter = [0, 0, 0, 0, 0]
    for post in user["posts"]:
        # "2018-10-01T17:20:18.850047+09:00"
        created_at = _time_seikei(post["created_at"])
        for i, target in enumerate(targets):
            if created_at.day == target.day:
                counter[i] += 1
                continue
    return counter


def count_comments():
    token = toKalliopeia.get_access_token("facilitator", "test")
    users_data = toKalliopeia.get_users_data(token)

    targets = [
        dt.datetime(2018, 10, 1),
        dt.datetime(2018, 10, 2),
        dt.datetime(2018, 10, 3),
        dt.datetime(2018, 10, 4),
        dt.datetime(2018, 10, 5)
    ]

    csv_datas = []
    csv_header = ["name", "day1", "day2", "day3", "day4", "day5", "total"]
    csv_datas.append(csv_header)
    for user in users_data:
        counter = time_comparison(user, targets)
        counter.append(sum(counter))
        counter.insert(0, user["display_name"])
        csv_datas.append(counter)

    f = open("/Users/ida/Dropbox/201810_1week/user_com_counter.csv","w")
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(csv_datas)
    f.close()


if __name__ == '__main__':
    count_comments()
