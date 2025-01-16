import gi

gi.require_version("AccountsService", "1.0")
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()


def get_active_session_user():
    users = manager.list_users()

    for u in users:
        if u.get_session() != "":
            return u

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
