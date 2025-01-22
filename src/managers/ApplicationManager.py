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


# APPLICATION RESTRICTIONS:
def restrict_application(application_id):
    if application_id in ALWAYS_ALLOWED_APPLICATIONS:
        print(application_id, " is always allowed. Skipping.")
        return

    try:
        app = Gio.DesktopAppInfo.new(application_id)
    except TypeError:
        print("Application not found:", application_id)
        return

    desktop_file_path = app.get_filename()
    executable_file_path = app.get_executable()

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

    # Don't restrict Chrom(e|ium) links:
    if "chrom" in executable_file_path and "chrom" not in application_id:
        return

    # Convert to absolute path
    if not executable_file_path.startswith("/"):
        executable_file_path = shutil.which(executable_file_path)

    FileRestrictionManager.restrict_bin_file(executable_file_path)

    print("Restricted:", desktop_file_path, "|", executable_file_path)


def unrestrict_application(application_id):
    try:
        app = Gio.DesktopAppInfo.new(application_id)
    except TypeError:
        print("Application not found:", application_id)
        return

    desktop_file_path = app.get_filename()
    executable_file_path = app.get_executable()

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

    # Don't unrestrict Chrome links:
    if "chrom" in executable_file_path and "chrom" not in application_id:
        return

    # Convert to absolute path
    if not executable_file_path.startswith("/"):
        executable_file_path = shutil.which(executable_file_path)

    FileRestrictionManager.unrestrict_bin_file(executable_file_path)

    print("Unrestricted:", desktop_file_path, "|", executable_file_path)
