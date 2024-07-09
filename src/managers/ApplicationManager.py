from gi.repository import Gio
from pathlib import Path
import os
import json
import managers.FileRestrictionManager as FileRestrictionManager
import shutil


CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
ALWAYS_ALLOWED_APPLICATIONS = [""]


def get_all_applications():
    apps = Gio.AppInfo.get_all()
    # Filter only visible applications
    apps = filter(lambda a: not a.get_nodisplay(), apps)
    apps = sorted(apps, key=lambda a: a.get_name())  # Sort alphabetically

    return list(apps)

def save_all_applications():
    applist = get_all_applications()

    json_object = {}

    for app in applist:
        json_object[app.get_id()] = {
            "name": app.get_name(),
            "bin": app.get_executable(),
            "cmdline": app.get_commandline(),
        }

    save_as_json_file(json_object)


# APPLICATION RESTRICTIONS:    
def restrict_application(application_id):
    if application_id in ALWAYS_ALLOWED_APPLICATIONS:
        print(application_id, " is always allowed. SKIPPING.")
        return

    try:
        app = Gio.DesktopAppInfo.new(application_id)
    except TypeError:
        print("Application not found:", application_id)
        return

    desktop_file_path = app.get_filename()
    executable_file_path = app.get_executable()
    print("Restricted:\t", desktop_file_path)
    print("  executable_file_path:\t", executable_file_path)
    print("  cmdline:\t\t", app.get_commandline())

    # Restrict desktopfile
    FileRestrictionManager.restrict_desktop_file(desktop_file_path)

    # Restrict executable
    if (
        "flatpak" in executable_file_path
        or "snap" in executable_file_path
        or "/bin/sh" in executable_file_path
        or "/bin/bash" in executable_file_path
        or "sh" == executable_file_path
        or "bash" == executable_file_path
    ):
        print(
            "Not restricting executable because flatpak/snap/bash/sh program:",
            executable_file_path,
        )
        return
    else:
        if executable_file_path.startswith("/"):
            # absolute path, restrict it directly
            FileRestrictionManager.restrict_bin_file(executable_file_path)
        else:
            absolute_path = shutil.which(executable_file_path)
            FileRestrictionManager.restrict_bin_file(absolute_path)


def unrestrict_application(application_id):
    try:
        app = Gio.DesktopAppInfo.new(application_id)
    except TypeError:
        print("Application not found:", application_id)
        return

    desktop_file_path = app.get_filename()
    executable_file_path = app.get_executable()

    print("Unrestricted:\t", desktop_file_path)
    print("  executable_file_path:\t", executable_file_path)
    print("  cmdline:\t\t", app.get_commandline())

    # Unrestrict desktopfile
    FileRestrictionManager.unrestrict_desktop_file(desktop_file_path)

    # Unrestrict executable
    if (
        "flatpak" in executable_file_path
        or "snap" in executable_file_path
        or "/bin/sh" in executable_file_path
        or "/bin/bash" in executable_file_path
        or "sh" == executable_file_path
        or "bash" == executable_file_path
    ):
        return
    else:
        if executable_file_path.startswith("/"):
            # absolute path, restrict it directly
            FileRestrictionManager.unrestrict_bin_file(executable_file_path)
        else:
            absolute_path = shutil.which(executable_file_path)
            FileRestrictionManager.unrestrict_bin_file(absolute_path)
