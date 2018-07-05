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


def _get_ui(token, name):
    users = load_users(token)
    for user in users:
        if user["name"] == name:
            return user["id"]
    return False


def get_user_info(token, name):
    ui = _get_ui(token, name)
    return load_user(token, ui)
