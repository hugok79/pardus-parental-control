#!/usr/bin/python3
"""Pardus Parental Control - Session Agent

Runs INSIDE the user session as the logged in user (systemd user service:
ppc-agent.service). It is unprivileged on purpose: the user's systemd manager
can stop it instantly on logout, so it never blocks the logout process.

It shows the countdown popup (NotificationApp) when the session time is over:
 - It listens for the "SessionTimeExpired" signal emitted by PPCDaemon on
   the system bus.
 - On startup it also asks the daemon (GetExpiryInfo) whether the expiry
   countdown has already started: when the user logs in outside of the
   permitted hours, the daemon starts the expiry at login, before this agent
   is up, so the signal is missed.

Killing this agent only hides the warning popup; the session is still
terminated by the root daemon.
"""

import os
import pwd
import subprocess
import sys

from gi.repository import Gio, GLib  # noqa

BUS_NAME = "tr.org.pardus.ParentalControl"
OBJECT_PATH = "/tr/org/pardus/ParentalControl"
INTERFACE_NAME = "tr.org.pardus.ParentalControl"

CWD = os.path.dirname(os.path.abspath(__file__))


def show_notification(username, seconds_left):
    print(f"Session time of '{username}' is over. Showing notification popup.")
    subprocess.Popen([f"{CWD}/NotificationApp.py", username, str(seconds_left)])


def on_session_time_expired(_conn, _sender, _path, _iface, _signal, params):
    (uid, username, seconds_left) = params.unpack()

    # The signal is broadcast to all sessions; only react to our own user
    if uid != os.getuid():
        return

    show_notification(username, seconds_left)


def check_already_expired(bus):
    """The expiry countdown may have started at login, before this agent.
    Ask the daemon and show the popup with the remaining seconds."""
    try:
        result = bus.call_sync(
            BUS_NAME,
            OBJECT_PATH,
            INTERFACE_NAME,
            "GetExpiryInfo",
            None,
            GLib.VariantType("(bu)"),
            Gio.DBusCallFlags.NONE,
            -1,
            None,
        )
    except GLib.Error as e:
        # The daemon may not be running (e.g. package removed)
        print(f"GetExpiryInfo failed: {e.message}")
        return

    (expired, seconds_left) = result.unpack()
    if expired and seconds_left > 0:
        show_notification(pwd.getpwuid(os.getuid()).pw_name, seconds_left)


def main():
    bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
    if bus is None:
        sys.stderr.write("Could not connect to the system bus.\n")
        sys.exit(1)

    # Match only signals coming from the daemon's well known name.
    # Only root can own it (see dbus/tr.org.pardus.parental-control.conf),
    # so the signal can not be spoofed by other users.
    bus.signal_subscribe(
        BUS_NAME,
        INTERFACE_NAME,
        "SessionTimeExpired",
        OBJECT_PATH,
        None,
        Gio.DBusSignalFlags.NONE,
        on_session_time_expired,
    )

    check_already_expired(bus)

    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
