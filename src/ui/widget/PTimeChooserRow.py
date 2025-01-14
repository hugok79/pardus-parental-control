import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa

import locale  # noqa
from locale import gettext as _  # noqa


class PTimeChooserRow(Adw.PreferencesRow):
    def __init__(self, on_time_changed_callback, minutes=0):
        super().__init__()
        self.on_time_changed_callback = on_time_changed_callback

        self.set_activatable(False)

        # Time Selection
        adj = Gtk.Adjustment.new(minutes / 15, 0, 96, 1, 1, 0)
        self.scale_from_time = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=adj,
            margin_start=14,
            margin_end=14,
        )
        self.scale_from_time.set_digits(0)
        self.scale_from_time.set_draw_value(True)
        self.scale_from_time.set_format_value_func(self.on_format_value)
        self.scale_from_time.connect("value-changed", self.on_value_changed)

        for i in range(25):
            if i % 4 == 0:
                self.scale_from_time.add_mark(
                    i * 4, Gtk.PositionType.BOTTOM, self.on_format_value(None, i * 4)
                )
            else:
                self.scale_from_time.add_mark(i * 4, Gtk.PositionType.BOTTOM)

        self.set_child(self.scale_from_time)

    def set_minutes(self, value):
        self.scale_from_time.set_value(int(value / 15))

    def get_minutes(self):
        return int(self.scale_from_time.get_value() * 15)

    # Callbacks
    def on_value_changed(self, r):
        minutes = int(r.get_value() * 15)
        self.on_time_changed_callback(minutes)

    def on_format_value(self, scale, value):
        hours = int(value / 4)
        minutes = int(value % 4) * 15
        return f"{hours:02d}:{minutes:02d}"
