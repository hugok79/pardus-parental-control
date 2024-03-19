#!/usr/bin/python3
import gi
import sys

GTK_VERSION = "4.0"

if GTK_VERSION == "3.0":
    gi.require_version("Gtk", "3.0")
    from ui_gtk3.MainWindow import MainWindow
else:
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


app = Main()
app.run(sys.argv)
