#!/usr/bin/python3
import gi
import sys
import argparse
import threading
import managers.FileRestrictionManager as FileRestrictionManager
import time
import os
import subprocess

# Privileged run check
if not FileRestrictionManager.check_user_privileged():
    sys.stderr.write("You are not privileged to run this script.\n")
    sys.exit(1)


gi.require_version("Gtk", "4.0")
from ui_gtk4.MainWindow import MainWindow

from gi.repository import Gtk, Gio  # noqa


class Main(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="tr.org.pardus.parental-control",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

        self.window = None

    def do_activate(self):
        if self.window is None:
            self.window = MainWindow(self)

        self.window.show_ui()


# Argument Parsing
parser = argparse.ArgumentParser(description="Parental Control app for Pardus.")

parser.add_argument(
    "--startup",
    action="store_true",
    help="Applies new settings if the user or any settings changed.",
)
args = parser.parse_args()


# pardus-parental-control --startup # this is running when user logged in, stored in /etc/xdg/autostart
if args.startup:
    import managers.ProfileManager as ProfileManager

    if not os.file.exists(ProfileManager.APPLIED_PROFILE_PATH):
        print("Profile is not activated. Exiting.")
        exit(0)

    profile_manager = ProfileManager.get_default()
    profile = ProfileManager.Profile(
        profile_manager.load_json_from_file(ProfileManager.APPLIED_PROFILE_PATH)
    )

    """
    # TODO: Not filtering by user right now
    user_list = profile.get_user_list()

    if len(user_list) == 0:
        print("There is no user in user_list in profile. Nothing happened.")
        exit(0)

    if os.getuid() not in user_list:
        print(
            "Revert back to original settings, this user is not in the restricted users list."
        )

        process = PPCActivator.run_activator(False)

        exit(process.returncode)
    """

    # Session Time check timer
    starts = profile.get_session_time_start()
    ends = profile.get_session_time_end()

    if starts == ends:
        print("Session Time is not set. Not applying.")
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
        secs = (3600 * t.tm_hour) + (60 * t.tm_min) + t.tm_sec

        if secs < starts or secs > ends:
            subprocess.Popen(
                [
                    "zenity",
                    "--info",
                    "--text='Your time is up! Computer is shutting down...'",
                ]
            )
            time.sleep(3)
            subprocess.Popen(["poweroff"])
            exit(1)

    check_session_time()
    set_interval(60, check_session_time)  # check every minute

else:
    app = Main()
    app.run(sys.argv)
