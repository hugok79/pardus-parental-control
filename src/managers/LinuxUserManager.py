import gi
import subprocess
import json

import managers.OSManager as OSManager

gi.require_version("AccountsService", "1.0")
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()
manager.list_users()


def get_user_object(username):
    return manager.get_user(username)


def get_sessions():
    os_codename = OSManager.get_os_codename()
    if os_codename == "yirmiuc":
        process = subprocess.run(
            ["loginctl", "list-sessions", "-o", "json"], capture_output=True
        )
    else:
        # This has changed in Pardus 25
        process = subprocess.run(
            ["loginctl", "list-sessions", "--json=short"], capture_output=True
        )

    if process.returncode != 0:
        print("[ERR] loginctl process failed: {}".format(process.returncode))
        return None

    json_array = json.loads(process.stdout.decode().strip())
    # example data on 'yirmiuc': [{"session":"19","uid":1000,"user":"ef","seat":"seat0","tty":"tty2"}]
    # example data on 'yirmibes': [{"session":"7","uid":1001,"user":"cocuk","seat":"seat0","leader":9619,"class":"user","tty":"tty2","idle":false,"since":null},
    #                              {"session":"8","uid":1001,"user":"cocuk","seat":null,"leader":9641,"class":"manager","tty":null,"idle":false,"since":null}]
    # 'manager' session added in yirmibes

    if len(json_array) == 0:
        print("[ERR] loginctl no session found.")
        return None

    return json_array


def get_standard_users():
    users = manager.list_users()
    users = list(
        filter(
            lambda u: u.get_account_type() == AccountsService.UserAccountType.STANDARD,
            users,
        )
    )

    return users
