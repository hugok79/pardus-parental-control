#!/usr/bin/python3
import gi
import sys


gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio  # noqa
from MainWindow import MainWindow  # noqa


class Main(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="tr.org.pardus.parental-control",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.window = None

    def do_activate(self):
        if self.window is None:
            self.window = MainWindow(self)

        self.window.present()


app = Main()
app.run(sys.argv)
