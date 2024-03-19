import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa


class PTimePeriodChooser(Gtk.Box):
    def __init__(self, on_time_changed_callback, start_seconds=0, end_seconds=86399):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.on_time_changed_callback = on_time_changed_callback

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

        # Set values:
        self.set_start_time_seconds(start_seconds)
        self.set_end_time_seconds(end_seconds)

        # Connect callbacks
        self.btn_from_hour.connect("value-changed", self.on_value_changed)
        self.btn_from_minute.connect("value-changed", self.on_value_changed)
        self.btn_to_hour.connect("value-changed", self.on_value_changed)
        self.btn_to_minute.connect("value-changed", self.on_value_changed)

    def get_start_time_seconds(self):
        return (
            self.btn_from_hour.get_value_as_int() * 3600
            + self.btn_from_minute.get_value_as_int() * 60
        )

    def get_end_time_seconds(self):
        return (
            self.btn_to_hour.get_value_as_int() * 3600
            + self.btn_to_minute.get_value_as_int() * 60
        )

    def set_start_time_seconds(self, seconds):
        self.btn_from_hour.set_value(seconds // 3600)
        self.btn_from_minute.set_value((seconds // 60) % 60)

    def set_end_time_seconds(self, seconds):
        self.btn_to_hour.set_value(seconds // 3600)
        self.btn_to_minute.set_value((seconds // 60) % 60)

    # Callbacks
    def on_value_changed(self, button):
        self.on_time_changed_callback(
            self.get_start_time_seconds(), self.get_end_time_seconds()
        )

    def on_output_changed(self, button):
        v = int(button.get_value())

        button.set_text(f"{v:02d}")

        return True
