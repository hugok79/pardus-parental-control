#!/usr/bin/python3
"""Pardus Parental Control - Session Agent

Runs INSIDE the user session as the logged in user (systemd user service:
ppc-agent.service). It is unprivileged on purpose: the user's systemd manager
can stop it instantly on logout, so it never blocks the logout process.

When the session time is over:
 1. It shows the countdown popup (NotificationApp).
 2. When the countdown ends, it triggers a clean desktop-environment logout
    (LogoutManager) so the display manager returns to the greeter properly,
    instead of being hard-killed by the daemon (which can leave a black
    screen on GDM + Wayland).

The expiry is learned in two ways:
 - the "SessionTimeExpired" signal emitted by PPCDaemon on the system bus,
 - and, on startup, by asking the daemon (GetExpiryInfo) - when the user logs
   in outside of the permitted hours the daemon starts the expiry at login,
   before this agent is up, so the signal would be missed.

Killing this agent only skips the clean logout and the popup; the root daemon
still terminates the session as a fallback.
"""

import os
import pwd
import subprocess
import sys

from gi.repository import Gio, GLib  # noqa

import managers.LogoutManager as LogoutManager

BUS_NAME = "tr.org.pardus.ParentalControl"
OBJECT_PATH = "/tr/org/pardus/ParentalControl"
INTERFACE_NAME = "tr.org.pardus.ParentalControl"

CWD = os.path.dirname(os.path.abspath(__file__))


class PPCAgent:
    def __init__(self):
        self.logout_scheduled = False

    def run(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        if self.bus is None:
            sys.stderr.write("Could not connect to the system bus.\n")
            sys.exit(1)

        # Match only signals coming from the daemon's well known name.
        # Only root can own it (see dbus/tr.org.pardus.parental-control.conf),
        # so the signal can not be spoofed by other users.
        self.bus.signal_subscribe(
            BUS_NAME,
            INTERFACE_NAME,
            "SessionTimeExpired",
            OBJECT_PATH,
            None,
            Gio.DBusSignalFlags.NONE,
            self.on_session_time_expired,
        )

        self.check_already_expired()

        GLib.MainLoop().run()

    def on_session_time_expired(self, _conn, _sender, _path, _iface, _signal, params):
        (uid, username, seconds_left) = params.unpack()

        # The signal is broadcast to all sessions; only react to our own user
        if uid != os.getuid():
            return

        self.start_logout_countdown(username, seconds_left)

    def check_already_expired(self):
        """The expiry countdown may have started at login, before this agent.
        Ask the daemon and resume the countdown with the remaining seconds."""
        try:
            result = self.bus.call_sync(
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
        if expired:
            username = pwd.getpwuid(os.getuid()).pw_name
            self.start_logout_countdown(username, seconds_left)

    def start_logout_countdown(self, username, seconds_left):
        # The signal and GetExpiryInfo can both arrive; only act once.
        if self.logout_scheduled:
            return
        self.logout_scheduled = True

        print(f"Session time of '{username}' is over. Logout in {seconds_left} seconds.")

        # Visual countdown popup
        subprocess.Popen([f"{CWD}/NotificationApp.py", username, str(seconds_left)])

        # Clean DE logout when the countdown ends
        GLib.timeout_add_seconds(max(seconds_left, 1), self.do_clean_logout)

    def do_clean_logout(self):
        # If this fails (unknown desktop / killed agent), the daemon still
        # terminates the session as a fallback shortly after.
        LogoutManager.request_logout()
        return GLib.SOURCE_REMOVE


if __name__ == "__main__":
    PPCAgent().run()
