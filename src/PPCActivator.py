#!/usr/bin/python3

import sys
import time
import logging

import managers.FileRestrictionManager as FileRestrictionManager
import managers.LinuxUserManager as LinuxUserManager
import managers.PreferencesManager as PreferencesManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.ApplicationManager as ApplicationManager

from NotificationApp import NotificationApp

from gi.repository import Gio, Gtk, GLib  # noqa


logging.basicConfig(
    filename="/var/log/pardus-parental-control.log",
    level=logging.DEBUG,
    format="(%(asctime)s) [%(levelname)s]: %(message)s",
)


def log(msg):
    logging.debug(msg)


class PPCActivator(Gtk.Application):
    def __init__(self):
        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

        super().__init__(
            application_id="tr.org.pardus.parental-control.apply-settings",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        # Logged user preferences:
        self.logged_user_name = LinuxUserManager.get_active_session_username()
        self.preferences = None
        self.preferences_manager = PreferencesManager.get_default()

        if self.logged_user_name:
            if self.preferences_manager.has_user(self.logged_user_name):
                self.preferences = self.preferences_manager.get_user(
                    self.logged_user_name
                )

                if self.preferences.get_is_session_time_filter_active():
                    empty_window = Gtk.Window(application=self)  # prevent closing app

                    self.check_session_time()
                    GLib.timeout_add_seconds(60, self.check_session_time)

                self.apply_preferences()
            else:
                self.clear_application_filter()
                self.clear_website_filter()
                log(
                    "User not found in preferences.json: {}".format(
                        self.logged_user_name
                    )
                )
                log("Cleared all filters")

                # Exit if user not in preferences list.
                sys.exit(0)

    def check_session_time(self):
        if self.is_session_time_ended():
            notification_app = NotificationApp()
            notification_app.run()

            sys.exit(0)
            return GLib.SOURCE_REMOVE

        return GLib.SOURCE_CONTINUE

    def apply_preferences(self):
        log("Applying application filters for: {}".format(self.logged_user_name))

        if self.preferences.get_is_application_filter_active():
            self.apply_application_filter()
        else:
            self.clear_application_filter()
        log("Applied application filters.")

        log("Applying website filters for: {}".format(self.logged_user_name))
        if self.preferences.get_is_website_filter_active():
            self.apply_website_filter()
        else:
            self.clear_website_filter()
        log("Applied website filters.")

    # == Application Filtering ==
    def apply_application_filter(self):
        pref = self.preferences

        list_length = len(pref.get_application_list())
        if list_length == 0:
            return

        is_allowlist = pref.get_is_application_list_allowlist()
        if is_allowlist:
            for app in ApplicationManager.get_all_applications():
                if app.get_filename() in pref.get_application_list():
                    ApplicationManager.unrestrict_application(app.get_filename())
                else:
                    ApplicationManager.restrict_application(app.get_filename())
        else:
            for app_id in pref.get_application_list():
                ApplicationManager.restrict_application(app_id)

    def clear_application_filter(self):
        for app in ApplicationManager.get_all_applications():
            ApplicationManager.unrestrict_application(app.get_filename())

    # == Website Filtering ==
    def apply_website_filter(self):
        pref = self.preferences

        list_length = len(pref.get_website_list())
        if list_length == 0:
            return

        is_allowlist = pref.get_is_website_list_allowlist()

        # browser + domain configs
        NetworkFilterManager.apply_domain_filter_list(
            pref.get_website_list(),
            is_allowlist,
            self.preferences_manager.get_base_dns_servers(),
        )

    def clear_website_filter(self):
        # browser + domain configs
        NetworkFilterManager.clear_domain_filter_list()

    # == Session Time Control ==
    def is_session_time_ended(self):
        # Session Time Minutes. 1440 minutes in a day.
        start = self.preferences.get_session_time_start()
        end = self.preferences.get_session_time_end()

        if start == end:
            log("Configuration Start and End times are equal. Not applying.")
            return False

        t = time.localtime()
        minutes_now = (60 * t.tm_hour) + t.tm_min

        if minutes_now >= start and minutes_now <= end:
            return False

        log("Time is up! Shutting down...")
        return True


if __name__ == "__main__":
    activator = PPCActivator()
    if len(sys.argv) == 2:
        if sys.argv[1] == "--disable":
            activator.clear_application_filter()
            activator.clear_website_filter()
            sys.exit(0)

    activator.run()
