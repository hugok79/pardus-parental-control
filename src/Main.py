#!/usr/bin/python3
import gi
import sys
import threading
import managers.FileRestrictionManager as FileRestrictionManager
import time
import os
import subprocess

from ui.MainWindow import MainWindow

gi.require_version("Gtk", "4.0")
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


"""
if args.startup:
    import managers.ProfileManager as ProfileManager

    if not os.path.exists(ProfileManager.APPLIED_PROFILE_PATH):
        print("Profile is not activated. Exiting.")
        exit(0)

    profile_manager = ProfileManager.get_default()
    profile = ProfileManager.Profile(
        profile_manager.load_json_from_file(ProfileManager.APPLIED_PROFILE_PATH)
    )

    user_list = profile.get_user_list()

    if len(user_list) == 0:
        print("There is no user in user_list in profile. Nothing happened.")
        exit(0)

    import pwd

    username = pwd.getpwuid(os.getuid()).pw_name

    if username not in user_list:
        print("User is not in the list")
        exit(0)

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
            time.sleep(2)
            subprocess.Popen(["loginctl", "kill-user", username])
            exit(1)

    check_session_time()
    t = set_interval(check_session_time, 60)  # check every minute
    t.join()

else:
"""
# Privileged run check
if not FileRestrictionManager.check_user_privileged():
    sys.stderr.write("You are not privileged to run this script.\n")
    sys.exit(1)

if __name__ == "__main__":
    app = Main()
    app.run(sys.argv)
