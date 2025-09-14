import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa

from locale import gettext as _  # noqa


class PTimeEntry(Gtk.Box):
    def __init__(self, minutes, on_time_changed_callback, *user_data):
        super().__init__(spacing=3, halign="center")
        self.on_time_changed_callback = on_time_changed_callback
        self.user_data = user_data

        # Hours
        self.hours_entry = Gtk.Entry(
            input_purpose=Gtk.InputPurpose.DIGITS,
            max_length=2,
            max_width_chars=2,
            valign="center",
        )
        self.hours_entry.set_text(str(int(minutes / 60)))
        self.hours_entry.connect("activate", self.on_entry_activated, "hours")
        self.hours_entry.connect("notify::has-focus", self.on_entry_move_focus, "hours")
        self.hours_entry.connect("changed", self.on_entry_changed, "hours")
        self.append(self.hours_entry)

        self.append(Gtk.Label(label=":"))

        # Minutes
        self.minutes_entry = Gtk.Entry(
            input_purpose=Gtk.InputPurpose.DIGITS,
            max_length=2,
            max_width_chars=2,
            valign="center",
        )
        self.minutes_entry.set_text(str(int(minutes % 60)))
        self.minutes_entry.connect("activate", self.on_entry_activated, "minutes")
        self.minutes_entry.connect(
            "notify::has-focus", self.on_entry_move_focus, "minutes"
        )
        self.minutes_entry.connect("changed", self.on_entry_changed, "minutes")
        self.append(self.minutes_entry)

    def set_total_minutes(self, value):
        hours = int(value / 60)
        mins = int(value % 60)

        self.hours_entry.set_text(str(hours))
        self.minutes_entry.set_text(str(mins))

    def get_total_minutes(self):
        hours = int(self.hours_entry.get_text()) * 60
        mins = int(self.minutes_entry.get_text())

        return hours + mins

    # Callbacks
    def on_entry_activated(self, entry, time_type):
        txt = "0" if not entry.get_text() else entry.get_text()
        number = int(txt)

        if time_type == "hours":
            if number > 23:
                number = 23
            elif number < 0:
                number = 0
        elif time_type == "minutes":
            if number > 59:
                number = 59
            elif number < 0:
                number = 0

        new_text = str(number)
        entry.set_text(new_text)
        self.on_time_changed_callback(self.get_total_minutes(), self.user_data)

    def on_entry_move_focus(self, entry, param, time_type):
        self.on_entry_activated(entry, time_type)

    def on_entry_changed(self, entry, time_type):
        old_value = entry.get_text()
        new_value = "".join(i for i in entry.get_text() if i.isdigit())

        if old_value != new_value:
            if new_value:
                entry.set_text(new_value)
            else:
                entry.set_text("0")
