import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa


class PTimeChooser(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        # From:
        self.append(Gtk.Label(label="From: "))

        # Time Selection
        self.btn_from_hour = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.btn_from_hour.set_orientation(Gtk.Orientation.VERTICAL)
        self.btn_from_hour.connect("output", self.on_output_changed)
        self.append(self.btn_from_hour)

        self.append(Gtk.Label(label=":"))

        self.btn_from_minute = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.btn_from_minute.set_orientation(Gtk.Orientation.VERTICAL)
        self.btn_from_minute.connect("output", self.on_output_changed)
        self.append(self.btn_from_minute)

        # To:
        self.append(Gtk.Label(label="To: "))

        # Time Selection
        self.btn_to_hour = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.btn_to_hour.set_orientation(Gtk.Orientation.VERTICAL)
        self.btn_to_hour.connect("output", self.on_output_changed)
        self.append(self.btn_to_hour)

        self.append(Gtk.Label(label=":"))

        self.btn_to_minute = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.btn_to_minute.set_orientation(Gtk.Orientation.VERTICAL)
        self.btn_to_minute.connect("output", self.on_output_changed)
        self.append(self.btn_to_minute)

    def get_start_time_seconds(self):
        return (
            self.btn_from_hour.get_value_as_int() * 3600
            + self.btn_from_minute.get_value_as_int() * 60
        )

    def get_end_time_seconds(self):
        return self.btn_to_hour.get_value_as_int() * 3600 + self.btn_to_minute * 60

    def on_output_changed(self, button):
        v = int(button.get_value())

        print(f"{v:02d}")
        button.set_text(f"{v:02d}")

        return True
