import platform
import gi
from managers.ProfileManager import Profile
import managers.LinuxUserManager as LinuxUserManager

gi.require_version("Malcontent", "0")
from gi.repository import Malcontent, Gio  # noqa


dbus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
if dbus is None:
    print("DBus SYSTEM connection error!")
    exit()

manager = Malcontent.Manager.new(dbus)


def reset_app_filter_for_all_users():
    new_app_filter = _new_app_filter([])

    # Save app filter for each user
    for user in LinuxUserManager.get_standard_users():
        user_id = user.get_uid()
        manager.set_app_filter(
            user_id, new_app_filter, Malcontent.ManagerSetValueFlags.NONE, None
        )


def _new_app_filter(app_id_list):
    builder = Malcontent.AppFilterBuilder.new()
    arch = platform.machine()

    # Generate AppFilter from application id list
    for e in app_id_list:
        if e.startswith("/"):
            builder.blocklist_path(e)
        else:
            builder.blocklist_flatpak_ref(f"app/{e}/{arch}/stable")

    builder.set_allow_user_installation(True)
    builder.set_allow_system_installation(True)

    new_app_filter = builder.end()

    return new_app_filter


def _new_session_times_filter(start, end):
    builder = Malcontent.SessionLimitsBuilder.new()

    builder.set_daily_schedule(start, end)
    new_session_filter = builder.end()

    return new_session_filter


def set_application_list_from_profile(profile: Profile):
    reset_app_filter_for_all_users()

    new_app_filter = _new_app_filter(profile.get_application_list())
    print(profile.get_application_list())

    # App Filter Settings
    if profile.get_is_application_list_allowlist():
        new_app_filter.app_list_type = Malcontent.AppFilterListType.ALLOWLIST
    else:
        new_app_filter.app_list_type = Malcontent.AppFilterListType.BLOCKLIST

    # Save app filter for each user
    for user_id in profile.get_user_list():
        print(user_id, " filtered ")
        manager.set_app_filter(
            user_id, new_app_filter, Malcontent.ManagerSetValueFlags.NONE, None
        )


def set_session_times_from_profile(profile: Profile):
    new_session_times_filter = _new_session_times_filter(
        profile.get_session_time_start(), profile.get_session_time_end()
    )
    # Set session filter for each user
    for user_id in profile.get_user_list():
        manager.set_session_limits(
            user_id,
            new_session_times_filter,
            Malcontent.ManagerSetValueFlags.NONE,
            None,
        )


def reset_session_times_for_all_users():
    builder = Malcontent.SessionLimitsBuilder.new()

    builder.set_none()
    new_session_times_filter = builder.end()

    # Set session filter for each user
    for user in LinuxUserManager.get_standard_users():
        user_id = user.get_uid()
        manager.set_session_limits(
            user_id,
            new_session_times_filter,
            Malcontent.ManagerSetValueFlags.NONE,
            None,
        )
