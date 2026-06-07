"""Application and Website filter apply/clear operations.

Used by PPCDaemon (system service) and ppc_disabler.py.
"""

import managers.ApplicationManager as ApplicationManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.PreferencesManager as PreferencesManager
import managers.SystemPreferencesManager as SystemPreferencesManager


def apply_preferences(username, user_id):
    """Re-reads preferences.json and applies (or clears) the application and
    website filters of the given user."""
    preferences_manager = PreferencesManager.get_default()
    preferences_manager.update_json_from_file()

    if not preferences_manager.has_user(username):
        clear_all_filters()
        return

    preferences = preferences_manager.get_user(username)

    if preferences.get_application().get_active():
        apply_application_filter(preferences, user_id)
    else:
        clear_application_filter()

    if preferences.get_website().get_active():
        apply_website_filter(preferences)
    else:
        clear_website_filter()


def clear_all_filters():
    clear_application_filter()
    clear_website_filter()


# == Application Filtering ==
def apply_application_filter(preferences, user_id):
    pref = preferences

    list_length = len(pref.get_application().get_list())
    if list_length == 0:
        return

    is_allowlist = pref.get_application().get_allowlist()
    if is_allowlist:
        for app in ApplicationManager.get_all_applications():
            if (
                "flatpak" not in app.get_filename()
                and app.get_filename() in pref.get_application().get_list()
            ):
                ApplicationManager.unrestrict_application(app.get_filename())
            else:
                ApplicationManager.restrict_application(app.get_filename())

        blocked_app_ids = []
        for app in ApplicationManager.get_flatpak_applications():
            if app.get_filename() not in pref.get_application().get_list():
                app_id = app.get_id()[:-8]  # remove .desktop suffix
                blocked_app_ids.append(app_id)

        ApplicationManager.restrict_flatpaks(blocked_app_ids, user_id)

    else:
        for desktop_file in pref.get_application().get_list():
            ApplicationManager.restrict_application(desktop_file)

        blocked_app_ids = []
        for app in ApplicationManager.get_flatpak_applications():
            if app.get_filename() in pref.get_application().get_list():
                app_id = app.get_id()[:-8]  # remove .desktop suffix
                blocked_app_ids.append(app_id)

        ApplicationManager.restrict_flatpaks(blocked_app_ids, user_id)


def clear_application_filter():
    ApplicationManager.unrestrict_all_flatpaks()

    for app in ApplicationManager.get_all_applications():
        ApplicationManager.unrestrict_application(app.get_filename())


# == Website Filtering ==
def apply_website_filter(preferences):
    pref = preferences

    list_length = len(pref.get_website().get_list())
    if list_length == 0:
        return

    is_allowlist = pref.get_website().get_allowlist()

    # browser + domain configs
    NetworkFilterManager.apply_domain_filter_list(
        pref.get_website().get_list(),
        is_allowlist,
        SystemPreferencesManager.get_default().get_base_dns_servers(),
    )


def clear_website_filter():
    # browser + domain configs
    NetworkFilterManager.clear_domain_filter_list()
