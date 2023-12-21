import gi
gi.require_version('AccountsService', '1.0')
from gi.repository import AccountsService  # noqa

manager = AccountsService.UserManager.get_default()


def get_standard_users():
    users = manager.list_users()
    users = list(filter(lambda u: u.get_account_type() ==
                 AccountsService.UserAccountType.STANDARD, users))

    return users
