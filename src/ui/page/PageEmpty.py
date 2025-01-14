from locale import gettext as _


import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa


class PageEmpty(Gtk.Box):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        lbl = Gtk.Label(
            label=_("Select a user to start"),
            css_classes=["title-1"],
            hexpand=True,
            margin_bottom=60,
        )
        self.append(lbl)
