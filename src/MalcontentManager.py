import platform
import gi

gi.require_version("Malcontent", "0")
from gi.repository import Malcontent, Gio  # noqa


dbus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
if dbus is None:
    print("DBus SYSTEM connection error!")
    exit()

manager = Malcontent.Manager.new(dbus)


def set_application_list_from_profile(profile):
    builder = Malcontent.AppFilterBuilder.new()
    arch = platform.machine()

    # Generate AppFilter from application id list
    for e in profile["application_list"]:
        if e.startsWith("/"):
            builder.blocklist_path(e)
        else:
            builder.blocklist_flatpak_ref(f"app/{e}/{arch}/stable")

    builder.set_allow_user_installation(False)
    builder.set_allow_system_installation(True)

    new_app_filter = builder.end()
    builder.free()

    # App Filter Settings
    if profile["is_application_list_allowed"]:
        new_app_filter.app_list_type = Malcontent.AppFilterListType.ALLOWLIST
    else:
        new_app_filter.app_list_type = Malcontent.AppFilterListType.BLOCKLIST

    # Save app filter for each user
    for user_id in profile["user_list"]:
        manager.set_app_filter(
            user_id, new_app_filter, Malcontent.ManagerSetValueFlags.INTERACTIVE, None
        )


def set_session_times_from_profile(profile):
    builder = Malcontent.SessionLimitsBuilder.new()
    builder.set_daily_schedule(
        profile["session_time_start"], profile["session_time_end"]
    )
    new_session_filter = builder.end()
    builder.free()

    # Set session filter for each user
    for user_id in profile["user_list"]:
        manager.set_session_limits(
            user_id,
            new_session_filter,
            Malcontent.ManagerSetValueFlags.INTERACTIVE,
            None,
        )
