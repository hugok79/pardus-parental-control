import gi
import subprocess
import managers.FileRestrictionManager as FileRestrictionManager

gi.require_version("AccountsService", "1.0")
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()


def get_standard_users():
    users = manager.list_users()
    users = list(
        filter(
            lambda u: u.get_account_type() == AccountsService.UserAccountType.STANDARD,
            users,
        )
    )

    return users


def _add_user_to_group(user_name, group_name):
    subprocess.run(["usermod", "-a", "-G", group_name, user_name])


def _remove_user_from_group(user_name, group_name):
    subprocess.run(["gpasswd", "-d", user_name, group_name])


def add_user_to_privileged_group(user_name):
    _add_user_to_group(user_name, FileRestrictionManager.PRIVILEGED_GROUP)
    print(user_name, "added to", FileRestrictionManager.PRIVILEGED_GROUP)


def remove_user_from_privileged_group(user_name):
    _remove_user_from_group(user_name, FileRestrictionManager.PRIVILEGED_GROUP)
    print(user_name, "removed from", FileRestrictionManager.PRIVILEGED_GROUP)
