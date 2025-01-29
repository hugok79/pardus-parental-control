import os
from gi.repository import Gio
from pathlib import Path
import managers.FileRestrictionManager as FileRestrictionManager
import shutil


CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
ALWAYS_ALLOWED_APPLICATIONS = [
    "xfce4-clipman.desktop",
    "xfce4-screenshooter.desktop",
    "xfce4-session-logout.desktop",
]
ALWAYS_ALLOWED_BINARIES = [
    "flatpak",
    "bash",
    "sh",
    "snap",
    "exo-open",
    "libreoffice",
    "xfce4-panel",
    "xfce4-session-logout",
    "sudo",
    "pkexec",
    "xfwm4",
    "python",
    "python3",
]


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
    # Filter XFCE apps:
    apps = filter(lambda a: not a.get_boolean("X-XfcePluggable"), apps)

    apps = sorted(apps, key=lambda a: a.get_name())  # Sort alphabetically

    return list(apps)


def _get_executable_path(app):
    executable = app.get_executable()

    # String to Path
    if executable[0] == '"':
        # '"/opt/Youtube Music/youtube-music" %u' -> '/opt/Youtube Music/youtube-music'
        cmdline = app.get_commandline()
        if cmdline:
            executable = cmdline.split('"')[1]
        else:
            print(
                "- Skip - executable and cmdline is corrupted in application:",
                executable,
                cmdline,
            )
            return None

    # Absolute Path to Executable Name
    if executable[0] == "/":
        # '/opt/Youtube Music/youtube-music' -> 'youtube-music'
        executable = executable.split("/")[-1]

    # Allowed Lists
    if executable in ALWAYS_ALLOWED_BINARIES:
        print("- Skip - Always Allowed Binary:", executable)
        return None

    # Don't restrict Chrom(e|ium) links:
    if "chrom" in executable and "chrom" not in app.get_id():
        print("- Skip - Chrome Link:", app.get_id())
        return None

    # Convert to absolute path
    return shutil.which(executable)


# APPLICATION RESTRICTIONS:
def restrict_application(desktop_file):
    # /usr/share/applications/abc.desktop -> abc.desktop
    app_id = desktop_file.split("/")[-1]

    if app_id in ALWAYS_ALLOWED_APPLICATIONS:
        print(desktop_file, " is always allowed. Skipping.")
        return

    try:
        app = Gio.DesktopAppInfo.new_from_filename(desktop_file)
    except TypeError:
        print("Application not found:", desktop_file)
        return

    # Restrict desktopfile
    FileRestrictionManager.restrict_desktop_file(desktop_file)

    executable_path = _get_executable_path(app)
    if executable_path:
        FileRestrictionManager.restrict_bin_file(executable_path)

    print("Restricted:", desktop_file, "|", executable_path)


def unrestrict_application(desktop_file):
    # /usr/share/applications/abc.desktop -> abc.desktop
    try:
        app = Gio.DesktopAppInfo.new_from_filename(desktop_file)
    except TypeError:
        print("Application not found:", desktop_file)
        return

    # Unrestrict desktopfile
    FileRestrictionManager.unrestrict_desktop_file(desktop_file)

    # Convert to absolute path
    executable_path = _get_executable_path(app)
    if executable_path:
        FileRestrictionManager.unrestrict_bin_file(executable_path)
        print("Unrestricted:", desktop_file, "|", executable_path)
    else:
        print("Unrestricted .desktop only:", desktop_file)
