import platform
import gi
gi.require_version('Malcontent', '0')
from gi.repository import Malcontent, Gio  # noqa


dbus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
if dbus is None:
    print("DBus SYSTEM connection error!")
    exit()

manager = Malcontent.Manager.new(dbus)


def set_application_list_from_profile(profile, user_id):
    builder = Malcontent.AppFilterBuilder.new()
    arch = platform.machine()

    # Generate AppFilter from application id list
    for e in profile["application_list"]:
        if e.startsWith("/"):
            builder.blocklist_path(e)
        else:
            builder.blocklist_flatpak_ref(f"app/{e}/{arch}/stable")

    new_app_filter = builder.end()
    builder.free()

    # App Filter Settings
    if profile["is_application_list_allowed"]:
        new_app_filter.app_list_type = Malcontent.AppFilterListType.ALLOWLIST
    else:
        new_app_filter.app_list_type = Malcontent.AppFilterListType.BLOCKLIST
    new_app_filter.allow_system_installation = False
    new_app_filter.allow_user_installation = False

    # Save app filter
    manager.set_app_filter(user_id, new_app_filter,
                           Malcontent.ManagerSetValueFlags.INTERACTIVE, None)
