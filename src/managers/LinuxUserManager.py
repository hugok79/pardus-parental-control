import gi
import subprocess
import json

gi.require_version("AccountsService", "1.0")
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()
manager.list_users()


def get_user_object(username):
    return manager.get_user(username)


def get_active_session_username():
    process = subprocess.run(
        ["loginctl", "list-sessions", "-o", "json"], capture_output=True
    )

    if process.returncode != 0:
        print("[ERR] loginctl process failed: {}".format(process.returncode))
        return None

    json_array = json.loads(process.stdout.decode().strip())
    # example data: [{"session":"19","uid":1000,"user":"ef","seat":"seat0","tty":"tty2"}]

    if len(json_array) == 0:
        print("[ERR] loginctl no session found.")
        return None

    return json_array[0]["user"]


def get_standard_users():
    users = manager.list_users()
    users = list(
        filter(
            lambda u: u.get_account_type() == AccountsService.UserAccountType.STANDARD,
            users,
        )
    )

    return users
