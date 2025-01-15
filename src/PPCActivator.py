#!/usr/bin/python3

import sys
import subprocess
import os
import threading
import time

import managers.FileRestrictionManager as FileRestrictionManager
import managers.LinuxUserManager as LinuxUserManager
import managers.PreferencesManager as PreferencesManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.ApplicationManager as ApplicationManager

CWD = os.path.dirname(os.path.abspath(__file__))


class PPCActivator:
    def __init__(self):
        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

    def run(self):
        print("== PPCActivator STARTED ==")

        self.logged_user = LinuxUserManager.get_active_session_username()
        self.read_user_preferences()

        if self.preferences.get_is_application_filter_active():
            self.apply_application_filter()
        else:
            self.clear_application_filter()

        if self.preferences.get_is_website_filter_active():
            self.apply_website_filter()
        else:
            self.clear_website_filter()

        if self.preferences.get_is_session_time_filter_active():
            # START TIMER
            self.start_session_time_checker()

        print("== PPCActivator FINISHED ==")

    def read_user_preferences(self):
        self.preferences_manager = PreferencesManager.get_default()
        if self.preferences_manager.has_user(self.logged_user):
            self.preferences = self.preferences_manager.get_user(self.logged_user)
        else:
            print("User not found in preferences.json: {}".format(self.logged_user))
            self.clear_application_filter()
            self.clear_website_filter()
            print("Cleared all filters")
            exit(0)

    # == Application Filtering ==
    def apply_application_filter(self):
        pref = self.preferences

        list_length = len(pref.get_application_list())
        if list_length == 0:
            return

        is_allowlist = pref.get_is_application_list_allowlist()
        if is_allowlist:
            for app in ApplicationManager.get_all_applications():
                if app.get_id() not in pref.get_application_list():
                    ApplicationManager.restrict_application(app.get_id())
        else:
            for app in pref.get_application_list():
                ApplicationManager.restrict_application(app.get_id())

    def clear_application_filter(self):
        for app in ApplicationManager.get_all_applications():
            ApplicationManager.unrestrict_application(app.get_id())

    # == Website Filtering ==
    def apply_website_filter(self):
        pref = self.preferences

        list_length = len(pref.get_website_list())
        if list_length == 0:
            return

        is_allowlist = pref.get_is_website_list_allowlist()

        # browser + domain configs
        NetworkFilterManager.set_domain_filter_list(
            pref.get_website_list(),
            is_allowlist,
            self.preferences_manager.get_base_dns_server(),
        )

        # smartdns server
        if pref.get_run_smartdns():
            # resolvconf
            NetworkFilterManager.set_resolvconf_to_localhost()
            NetworkFilterManager.enable_smartdns_service()
            NetworkFilterManager.restart_smartdns_service()

    def clear_website_filter(self):
        # browser + domain configs
        NetworkFilterManager.reset_domain_filter_list()

        # smartdns-rs
        NetworkFilterManager.reset_resolvconf_to_default()
        NetworkFilterManager.stop_smartdns_service()
        NetworkFilterManager.disable_smartdns_service()

    # == Session Time Control ==
    def start_session_time_checker(self):
        # Session Time Minutes. 1440 minutes in a day.
        start = self.preferences.get_session_time_start()
        end = self.preferences.get_session_time_end()

        if start == end:
            print("Start and End times are equal. Not applying.")
            exit(0)

        def set_interval(func, sec):
            def func_wrapper():
                set_interval(func, sec)
                func()

            t = threading.Timer(sec, func_wrapper)
            t.start()
            return t

        def check_session_time():
            t = time.localtime()
            minutes_now = (60 * t.tm_hour) + t.tm_min

            if minutes_now < start or minutes_now > end:
                subprocess.Popen(
                    [
                        "zenity",
                        "--info",
                        "--text='Your time is up! Computer is shutting down in 30 seconds...'",
                    ]
                )
                time.sleep(30)
                subprocess.Popen(["loginctl", "kill-user", self.logged_user])
                exit(1)

        check_session_time()
        t = set_interval(check_session_time, 60)  # check every minute
        t.join()


if __name__ == "__main__":
    activator = PPCActivator()
    if len(sys.argv) == 2:
        if sys.argv[1] == "--clear":
            activator.clear_application_filter()
            activator.clear_website_filter()
            exit(0)

    activator.run()
