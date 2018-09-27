from pathlib import Path
import simplejson as json

import toKalliopeia


def main():
    token = toKalliopeia.get_access_token("facilitator", "test")
    f_user = Path("201810_users.json")

    f = f_user.open("r")
    jsonData = json.load(f)
    for user in jsonData:
        toKalliopeia.create_user(token, user)



if __name__ == '__main__':
    main()
