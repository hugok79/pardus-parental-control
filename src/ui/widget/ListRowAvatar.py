import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa


class ListRowAvatar(Gtk.Box):
    def __init__(self, fullname="", username=""):
        super().__init__(hexpand=True, spacing=7)

        self.fullname = fullname
        self.username = username

        self.avatar = Adw.Avatar(text=fullname, halign=Gtk.Align.START, size=32)
        self.label = Gtk.Label(label=fullname, halign=Gtk.Align.START)

        self.append(self.avatar)
        self.append(self.label)

    def get_fullname(self):
        return self.fullname

    def get_username(self):
        return self.username

    def set_user(self, fullname, username):
        self.fullname = fullname
        self.username = username

        self.label.set_label(fullname)
        self.avatar.set_text(fullname)
