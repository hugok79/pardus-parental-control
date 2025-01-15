import gi
import subprocess
import pwd
import os
import managers.FileRestrictionManager as FileRestrictionManager

gi.require_version("AccountsService", "1.0")
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()


def get_logged_username():
    return pwd.getpwuid(os.getuid()).pw_name


def _get_users():
    list_users = pwd.getpwall()

    return list(filter(lambda x: "bash" in x.pw_shell, list_users))


def get_active_session_username():
    users = _get_users()

    for u in users:
        process = subprocess.run(
            ["loginctl", "show-user", u.pw_name, "-p", "State"], capture_output=True
        )

        if process.returncode == 0:
            if "=active" in process.stdout.decode():
                return u.pw_name

    print("Couldnt find active session username from loginctl.")

    return None


def get_standard_users():
    users = manager.list_users()
    users = list(
        filter(
            lambda u: u.get_account_type() == AccountsService.UserAccountType.STANDARD,
            users,
        )
    )

    return users
