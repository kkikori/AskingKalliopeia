from .fetch_api import load_thread, load_threads, load_users, load_user


def _get_thi_list(token):
    threads = load_threads(token)

    thi_list = []
    for thread in threads:
        thi_list.append(thread["id"])
    return thi_list


def get_threads_data(token):
    thi_list = _get_thi_list(token)

    threads_data = []
    for th_i in thi_list:
        threads_data.append(load_thread(token, th_i))

    return threads_data


def _get_ui_list(token):
    users = load_users(token)
    ui_list = []
    for user in users:
        ui_list.append(user["id"])
    return ui_list


def get_users_data(token):
    ui_list = _get_ui_list(token)

    users_data = []
    for ui in ui_list:
        users_data.append(load_user(token, ui))
    return users_data


def read_user_id(users, name):
    #nameのユーザidを返す
    for user in users:
        if user["name"] == name:
            return user["id"]
    return False
