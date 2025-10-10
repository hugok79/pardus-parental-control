#!/usr/bin/python3
import sys
import gi
import time
import subprocess
import managers.LinuxUserManager as LinuxUserManager

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GLib, Adw  # noqa


import locale  # noqa
from locale import gettext as _  # noqa

# Translation Constants:
APPNAME = "pardus-parental-control"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)


class NotificationApp(Adw.Application):
    def __init__(self, argv):
        super().__init__(
            application_id="tr.org.pardus.parental-control.notificationapp",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )

        self.logged_user_name = argv[1]
        self.seconds_left = 10

    def do_activate(self):
        self.setup_window()

        GLib.timeout_add_seconds(1, self.tick_logout_seconds)

    def tick_logout_seconds(self):
        self.seconds_left -= 1
        self.subtitle.set_text(
            _("Session will be closed in {} seconds.").format(self.seconds_left)
        )

        if self.seconds_left == 0:
            subprocess.Popen(["loginctl", "kill-user", self.logged_user_name])

            self.quit()

        return True

    def setup_window(self):
        window = Adw.Window(application=self)
        window.set_default_size(500, 200)
        window.set_icon_name("pardus-parental-control")
        window.set_hide_on_close(True)
        window.set_title(_("Pardus Parental Control"))

        # UI
        ui = self.setup_ui()

        window.set_content(ui)
        window.present()

    def setup_ui(self):
        user = LinuxUserManager.get_user_object(self.logged_user_name)
        real_name = user.get_real_name()

        session_avatar = Gtk.Box(
            spacing=7, halign=Gtk.Align.CENTER, css_classes=["card"]
        )
        session_avatar.append(
            Adw.Avatar(
                text=real_name,
                halign=Gtk.Align.START,
                size=32,
                margin_start=7,
                margin_top=7,
                margin_bottom=7,
            )
        )
        session_avatar.append(
            Gtk.Label(label=real_name, halign=Gtk.Align.START, margin_end=7)
        )

        title = Gtk.Label(
            label=_("Your session time is over."),
            css_classes=["title-2"],
            justify=Gtk.Justification.CENTER,
            margin_top=14,
        )
        self.subtitle = Gtk.Label(
            label=_("Session will be closed in {} seconds.").format(self.seconds_left),
            justify=Gtk.Justification.CENTER,
        )
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.CENTER,
            spacing=7,
        )
        box.append(session_avatar)
        box.append(title)
        box.append(self.subtitle)

        return box


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./NotificationApp.py logged_user_name_here")
        sys.exit(0)

    app = NotificationApp(sys.argv)
    app.run()
