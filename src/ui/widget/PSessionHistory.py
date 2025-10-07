import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa

from locale import gettext as _  # noqa


class PSessionHistory(Gtk.Box):
    def __init__(self, today_minutes, weekly_minutes):
        super().__init__(
            spacing=7,
            orientation="vertical",
            css_classes=["card", "p-14"],
            hexpand=True,
            halign="fill",
        )

        # Titles
        box_titles = Gtk.Box(spacing=7, homogeneous=True, hexpand=True)
        box_titles.append(
            Gtk.Label(label=_("Today"), halign="start", css_classes=["title-2"])
        )
        box_titles.append(
            Gtk.Label(label=_("This Week"), halign="start", css_classes=["title-2"])
        )

        # Values
        box_values = Gtk.Box(spacing=7, homogeneous=True, hexpand=True)
        self.today_lbl = Gtk.Label(halign="start")
        self.weekly_lbl = Gtk.Label(halign="start")
        box_values.append(self.today_lbl)
        box_values.append(self.weekly_lbl)

        self.set_values(today_minutes, weekly_minutes)

        self.append(box_titles)
        self.append(box_values)

    def set_values(self, today_minutes, weekly_minutes):
        today_usage = ""
        if today_minutes >= 60:
            hours = int(today_minutes / 60)
            mins = today_minutes % 60
            today_usage = _("{} Hours {} Minutes").format(hours, mins)
        else:
            today_usage = _("{} Minutes").format(today_minutes)

        weekly_usage = ""
        if weekly_minutes >= 60:
            hours = int(weekly_minutes / 60)
            mins = weekly_minutes % 60
            weekly_usage = _("{} Hours {} Minutes").format(hours, mins)
        else:
            weekly_usage = _("{} Minutes").format(weekly_minutes)

        self.today_lbl.set_text(today_usage)
        self.weekly_lbl.set_text(weekly_usage)
