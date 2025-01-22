import os
from gi.repository import Gio
from pathlib import Path
import managers.FileRestrictionManager as FileRestrictionManager
import shutil


CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
ALWAYS_ALLOWED_APPLICATIONS = [""]


def _get_flatpak_applications():
    apps = []

    flatpak_dir = "/var/lib/flatpak/exports/share/applications/"
    if os.path.isdir(flatpak_dir):
        for f in os.listdir(flatpak_dir):
            if ".desktop" in f:
                app = Gio.DesktopAppInfo.new_from_filename(flatpak_dir + f)
                apps.append(app)

    return apps


def get_all_applications():
    apps = Gio.AppInfo.get_all()

    if os.getuid() == 0:
        apps.extend(_get_flatpak_applications())

    # Filter only visible applications
    apps = filter(lambda a: not a.get_nodisplay(), apps)
    apps = sorted(apps, key=lambda a: a.get_name())  # Sort alphabetically

    return list(apps)


# APPLICATION RESTRICTIONS:
def restrict_application(desktop_file):
    if desktop_file in ALWAYS_ALLOWED_APPLICATIONS:
        print(desktop_file, " is always allowed. Skipping.")
        return

    try:
        app = Gio.DesktopAppInfo.new_from_filename(desktop_file)
    except TypeError:
        print("Application not found:", desktop_file)
        return

    executable_file_path = app.get_executable()

    # Restrict desktopfile
    FileRestrictionManager.restrict_desktop_file(desktop_file)

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
    if "chrom" in executable_file_path and "chrom" not in desktop_file:
        return

    # Convert to absolute path
    if not executable_file_path.startswith("/"):
        executable_file_path = shutil.which(executable_file_path)

    FileRestrictionManager.restrict_bin_file(executable_file_path)

    print("Restricted:", desktop_file, "|", executable_file_path)


def unrestrict_application(desktop_file):
    try:
        app = Gio.DesktopAppInfo.new_from_filename(desktop_file)
    except TypeError:
        print("Application not found:", desktop_file)
        return

    executable_file_path = app.get_executable()

    # Unrestrict desktopfile
    FileRestrictionManager.unrestrict_desktop_file(desktop_file)

    # Unrestrict executable
    if (
        "flatpak" in executable_file_path
        or "snap" in executable_file_path
        or "/bin/sh" in executable_file_path
        or "/bin/bash" in executable_file_path
        or "sh" == executable_file_path
        or "bash" == executable_file_path
    ):
        print("Unrestricted .desktop only:", desktop_file)
        return

    # Don't unrestrict Chrome links:
    if "chrom" in executable_file_path and "chrom" not in desktop_file:
        print("Unrestricted .desktop only:", desktop_file)
        return

    # Convert to absolute path
    if not executable_file_path.startswith("/"):
        executable_file_path = shutil.which(executable_file_path)

    FileRestrictionManager.unrestrict_bin_file(executable_file_path)

    print("Unrestricted:", desktop_file, "|", executable_file_path)
