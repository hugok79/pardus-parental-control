import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa

from locale import gettext as _  # noqa


class PTimeEntry(Gtk.Box):
    def __init__(self, total_minutes, on_changed, day_index):
        super().__init__(spacing=3, halign="center")
        self.on_changed = on_changed
        self.day_index = day_index

        hours = int(total_minutes / 60)
        minutes = int(total_minutes % 60)

        # Hours
        self.entry = Gtk.Entry(
            text=f"{hours:02d}:{minutes:02d}",
            input_purpose=Gtk.InputPurpose.DIGITS,
            max_length=5,
            max_width_chars=5,
            valign="center",
        )

        self.entry.connect("activate", self.on_entry_activated)
        self.entry.connect("notify::has-focus", self.on_entry_move_focus)
        self.entry.connect("changed", self.on_entry_changed)
        self.append(self.entry)

    def set_total_minutes(self, value):
        hours = int(value / 60)
        mins = int(value % 60)

        self.hours_entry.set_text(str(hours))
        self.minutes_entry.set_text(str(mins))

    def get_total_minutes(self):
        # Split hours and minutes text
        splitted = self.entry.get_text().split(":")
        if len(splitted) != 2 or not (splitted[0] and splitted[1]):
            return 0

        hours = int(splitted[0]) * 60
        mins = int(splitted[1])

        return hours + mins

    # Callbacks
    def on_entry_activated(self, entry):
        txt = "00:00" if not entry.get_text() else entry.get_text()

        # Split hours and minutes text
        splitted = txt.split(":")

        if len(splitted) == 1 and splitted[0]:
            # e.g. User only wrote "12" and we will convert it to "12:00"
            hours = int(splitted[0])
            if hours > 23:
                hours = 23
            elif hours < 0:
                hours = 0

            entry.set_text(f"{hours:02d}:00")
            self.on_changed(hours * 60, self.day_index)
            return

        if len(splitted) != 2 or not (splitted[0] and splitted[1]):
            # User entered an invalid time like '12:456:1234', '12:', ':12', ':'
            entry.set_text("00:00")
            self.on_changed(0, self.day_index)
            return

        # User entered valid time like '12:34', '1:0', '0:5', '00:5', '5:00'
        hours = int(splitted[0])
        if hours > 23:
            hours = 23
        elif hours < 0:
            hours = 0

        minutes = int(splitted[1])
        if minutes > 59:
            minutes = 59
        elif minutes < 0:
            minutes = 0

        total_minutes = (hours * 60) + minutes

        entry.set_text(f"{hours:02d}:{minutes:02d}")
        self.on_changed(total_minutes, self.day_index)

    def on_entry_move_focus(self, entry, param):
        self.on_entry_activated(entry)

    def on_entry_changed(self, entry):
        # Filter unwanted chars
        text = entry.get_text()
        filtered_text = "".join(ch for ch in text if ch.isdigit() or ch == ":")

        if text != filtered_text:
            entry.set_text(filtered_text)
