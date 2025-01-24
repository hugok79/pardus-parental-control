#!/usr/bin/python3

import sys
import subprocess
import time
import os
import logging

import managers.FileRestrictionManager as FileRestrictionManager
import managers.LinuxUserManager as LinuxUserManager
import managers.PreferencesManager as PreferencesManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.ApplicationManager as ApplicationManager

from NotificationApp import NotificationApp


logging.basicConfig(
    filename="/var/log/pardus-parental-control.log",
    level=logging.DEBUG,
    format="(%(asctime)s) [%(levelname)s]: %(message)s",
)


def log(msg):
    logging.debug(msg)


class PPCActivator:
    def __init__(self):
        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

        self.logged_user_name = None
        self.preferences = None
        self.preferences_manager = PreferencesManager.get_default()

    def run_check_loop(self):
        while True:
            time.sleep(1)

            if (
                self.preferences
                and self.preferences.get_is_session_time_filter_active()
            ):
                if self.is_session_time_ended():
                    notification_app = NotificationApp()
                    notification_app.run()

            current_logged_username = LinuxUserManager.get_active_session_username()

            # ignore debian-gdm
            if current_logged_username == "Debian-gdm":
                current_logged_username = None

            if self.logged_user_name != current_logged_username:
                log(
                    "active user changed: {} -> {}".format(
                        self.logged_user_name, current_logged_username
                    )
                )
                self.logged_user_name = current_logged_username

                self.on_active_session_user_changed()

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

    # Events
    def on_active_session_user_changed(self):
        # update json file values
        self.preferences_manager.update_json_from_file()

        if self.logged_user_name:
            if self.preferences_manager.has_user(self.logged_user_name):
                self.preferences = self.preferences_manager.get_user(
                    self.logged_user_name
                )

                self.apply_preferences()
            else:
                self.preferences = None
                self.clear_application_filter()
                self.clear_website_filter()
                log(
                    "User not found in preferences.json: {}".format(
                        self.logged_user_name
                    )
                )
                log("Cleared all filters")
        else:
            self.preferences = None


if __name__ == "__main__":
    activator = PPCActivator()
    if len(sys.argv) == 2:
        if sys.argv[1] == "--disable":
            activator.clear_application_filter()
            activator.clear_website_filter()
            sys.exit(0)

    activator.run_check_loop()
