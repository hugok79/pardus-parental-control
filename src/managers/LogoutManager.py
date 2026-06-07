"""Desktop-environment-aware clean logout.

Used by PPCAgent (which runs inside the user session, so it has access to the
session bus and XDG_CURRENT_DESKTOP). A clean DE logout lets the desktop tear
itself down gracefully so the display manager returns to the greeter properly
- unlike a hard logind TerminateSession/TerminateUser, which kills the
compositor abruptly and, on GDM + Wayland, can leave a black screen.

If the desktop can not be detected or its logout tool is missing, request_logout
returns False and the root daemon's TerminateSession fallback takes over.
"""

import shutil
import subprocess


def _run(args):
    subprocess.Popen(args)
    return True


def _logout_gnome():
    # Covers GNOME and Cinnamon
    if shutil.which("gnome-session-quit"):
        return _run(["gnome-session-quit", "--logout", "--no-prompt"])
    if shutil.which("cinnamon-session-quit"):
        return _run(["cinnamon-session-quit", "--logout", "--no-prompt"])
    return False


def _logout_cinnamon():
    if shutil.which("cinnamon-session-quit"):
        return _run(["cinnamon-session-quit", "--logout", "--no-prompt"])
    return _logout_gnome()


def _logout_xfce():
    if shutil.which("xfce4-session-logout"):
        return _run(["xfce4-session-logout", "--logout", "--fast"])
    return False


def _logout_kde():
    # Plasma 6 exposes org.kde.Shutdown, Plasma 5 org.kde.ksmserver.
    # The qdbus binary is named qdbus6 on Plasma 6, qdbus on Plasma 5.
    if shutil.which("qdbus6"):
        return _run(
            ["qdbus6", "org.kde.Shutdown", "/Shutdown", "org.kde.Shutdown.logout"]
        )
    if shutil.which("qdbus"):
        return _run(
            [
                "qdbus",
                "org.kde.ksmserver",
                "/KSMServer",
                "org.kde.KSMServerInterface.logout",
                "0",  # confirm: no
                "0",  # sdtype: logout
                "0",  # sdmode: now
            ]
        )
    return False


# XDG_CURRENT_DESKTOP token -> logout function
_HANDLERS = {
    "gnome": _logout_gnome,
    "cinnamon": _logout_cinnamon,
    "x-cinnamon": _logout_cinnamon,
    "xfce": _logout_xfce,
    "kde": _logout_kde,
    "plasma": _logout_kde,
}


def request_logout():
    """Trigger a clean DE logout. Returns True if a logout command was issued,
    False if the desktop is unknown or its logout tool is unavailable."""
    import os

    # XDG_CURRENT_DESKTOP may be e.g. "ubuntu:GNOME" or "KDE"
    desktops = (os.environ.get("XDG_CURRENT_DESKTOP") or "").lower().split(":")

    for desktop in desktops:
        handler = _HANDLERS.get(desktop)
        if handler is not None and handler():
            print(f"Clean logout requested for desktop '{desktop}'.")
            return True

    print(f"No clean logout handler for desktop {desktops!r}.")
    return False
