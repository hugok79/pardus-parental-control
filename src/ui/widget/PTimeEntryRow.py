import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa

from locale import gettext as _  # noqa

from ui.widget.PTimeEntry import PTimeEntry  # noqa


class PTimeEntryRow(Adw.PreferencesRow):
    def __init__(
        self,
        title,
        minutes,
        on_time_changed_callback,
        on_activated_callback,
        day_index,
        is_active,
    ):
        super().__init__(height_request=50)

        box = Gtk.Box(hexpand=True)
        box_items = Gtk.Box(homogeneous=True, hexpand=True)
        box_items.append(Gtk.Label(halign="start", label=title, margin_start=12))
        box_items.append(
            PTimeEntry(minutes, on_time_changed_callback, "hours", day_index)
        )
        box_items.append(
            PTimeEntry(minutes, on_time_changed_callback, "minutes", day_index)
        )
        box_items.append(PTimeEntry(0, on_time_changed_callback, "limit", day_index))
        switch = Gtk.Switch(
            halign="center",
            valign="center",
            margin_end=12,
            active=is_active,
        )
        switch.connect("state-set", on_activated_callback, day_index)
        switch.bind_property("active", box_items, "sensitive")

        box.append(box_items)
        box.append(switch)
        self.set_child(box)
