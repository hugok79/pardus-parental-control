#!/usr/bin/python3

import sys
import time
import datetime
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


class PPCActivator(Gtk.Application):
    def __init__(self, argv):
        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

        super().__init__(
            application_id="tr.org.pardus.parental-control.apply",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )

        self.setup_variables()

        if argv[1] and argv[1] != "--disable" and len(argv) == 3:
            self.logged_user_id = argv[1]
            self.logged_user_name = argv[2]

            for session in LinuxUserManager.get_sessions():
                if session["user"] == self.logged_user_name:
                    self.session_id = session["session"]
                    self.last_active_session_id = self.session_id
                    break

    def setup_variables(self):
        self.preferences = None
        self.preferences_manager = PreferencesManager.get_default()
        self.session_time_started = None

    def do_activate(self):
        self.log("PPCActivator Launched.")

        _empty_window = Gtk.Window(
            application=self
        )  # this is needed to make application status "activated", otherwise 120 seconds of preventing user logout happens

        if self.logged_user_name:
            if self.preferences_manager.has_user(self.logged_user_name):
                self.preferences = self.preferences_manager.get_user(
                    self.logged_user_name
                )

                self.apply_preferences()
            else:
                self.log("No preferences found.")

                self.clear_preferences()

            self.connect_user_active_status()

    def check_session_time(self):
        if self.is_session_time_ended():
            notification_app = NotificationApp(self.logged_user_name)
            notification_app.run()

            sys.exit(0)
            return GLib.SOURCE_REMOVE

        return GLib.SOURCE_CONTINUE

    def apply_preferences(self):
        if not self.preferences:
            self.log("No preferences found.")
            self.clear_preferences()
            return

        self.preferences_manager.update_json_from_file()
        self.preferences = self.preferences_manager.get_user(self.logged_user_name)

        session_time_prefs = self.get_session_time_preferences()
        if session_time_prefs.get_active():
            if self.session_time_started is None:
                self.log(
                    f"Session Time checking started. Start:{session_time_prefs.get_start()}, End:{session_time_prefs.get_end()}"
                )
                self.check_session_time()
                self.session_time_started = GLib.timeout_add_seconds(
                    60, self.check_session_time
                )
        elif self.session_time_started is not None:
            GLib.Source.remove(self.session_time_started)
            self.session_time_started = None

            self.log("Session Time checking stopped.")

        self.log(" - Application filters...")
        if self.preferences.get_application().get_active():
            self.apply_application_filter()
        else:
            self.clear_application_filter()

        self.log(" - Website filters...")
        if self.preferences.get_website().get_active():
            self.apply_website_filter()
        else:
            self.clear_website_filter()
        self.log("Applied!")

    def clear_preferences(self):
        self.clear_application_filter()
        self.clear_website_filter()

        # Clear session time tick:
        if self.session_time_started is not None:
            GLib.Source.remove(self.session_time_started)
            self.session_time_started = None

        self.log("Cleared all filters.")

    # == Application Filtering ==
    def apply_application_filter(self):
        pref = self.preferences

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

            ApplicationManager.restrict_flatpaks(blocked_app_ids, self.logged_user_id)

        else:
            for desktop_file in pref.get_application().get_list():
                ApplicationManager.restrict_application(desktop_file)

            blocked_app_ids = []
            for app in ApplicationManager.get_flatpak_applications():
                if app.get_filename() in pref.get_application().get_list():
                    app_id = app.get_id()[:-8]  # remove .desktop suffix
                    blocked_app_ids.append(app_id)

            ApplicationManager.restrict_flatpaks(blocked_app_ids, self.logged_user_id)

    def clear_application_filter(self):
        ApplicationManager.unrestrict_all_flatpaks()

        for app in ApplicationManager.get_all_applications():
            ApplicationManager.unrestrict_application(app.get_filename())

    # == Website Filtering ==
    def apply_website_filter(self):
        pref = self.preferences

        list_length = len(pref.get_website().get_list())
        if list_length == 0:
            return

        is_allowlist = pref.get_website().get_allowlist()

        # browser + domain configs
        NetworkFilterManager.apply_domain_filter_list(
            pref.get_website().get_list(),
            is_allowlist,
            self.preferences_manager.get_base_dns_servers(),
        )

    def clear_website_filter(self):
        # browser + domain configs
        NetworkFilterManager.clear_domain_filter_list()

    # == Session Time Control ==
    def get_session_time_preferences(self):
        pref = self.preferences.get_session_time()

        is_current_day_weekend = (
            datetime.datetime.today().weekday() > 4
        )  # 5: Sat, 6: Sun

        week = pref.get_weekend() if is_current_day_weekend else pref.get_weekday()

        return week

    def is_session_time_ended(self):
        week = self.get_session_time_preferences()

        # Session Time Minutes. 1440 minutes in a day.
        start = week.get_start()
        end = week.get_end()

        if start == end:
            print(
                "Session Time Configuration Start and End times are equal. Not applying."
            )
            return False

        t = time.localtime()
        minutes_now = (60 * t.tm_hour) + t.tm_min

        if minutes_now >= start and minutes_now <= end:
            return False

        self.log("Time is up! Shutting down...")
        return True

    def seat_properties_changed(self, _proxy, properties_changed, _properties_removed):
        props = properties_changed.unpack()
        if "ActiveSession" in props:
            # Active session changed:
            (session_id, _session_path) = props["ActiveSession"]
            self.log(
                f"Active Session Changed: {self.last_active_session_id}->{session_id}"
            )
            if session_id == self.session_id:
                self.log("Session opened, applying preferences.")
                self.apply_preferences()
            elif self.last_active_session_id == self.session_id:
                self.log("Session closed, clearing preferences.")
                self.clear_preferences()

            self.last_active_session_id = session_id

    def connect_user_active_status(self):
        self.dbus_connection = Gio.DBusProxy.new_for_bus_sync(
            bus_type=Gio.BusType.SYSTEM,
            flags=Gio.DBusProxyFlags.DO_NOT_AUTO_START,
            info=None,
            name="org.freedesktop.login1",
            object_path="/org/freedesktop/login1/seat/seat0",
            interface_name="org.freedesktop.login1.Seat",
            cancellable=None,
        )
        self.dbus_connection.connect(
            "g-properties-changed", self.seat_properties_changed
        )

        self.log("DBus Connected.")

    def log(self, msg):
        message = f"({self.logged_user_name}@{self.session_id}): {msg}"
        print(message)
        logging.debug(message)


if __name__ == "__main__":
    activator = PPCActivator(sys.argv)
    if len(sys.argv) == 2:
        if sys.argv[1] == "--disable":
            activator.clear_application_filter()
            activator.clear_website_filter()
            sys.exit(0)
    elif len(sys.argv) == 3:
        activator.run()
