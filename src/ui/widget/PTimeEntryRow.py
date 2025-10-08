import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject  # noqa

from locale import gettext as _  # noqa

from ui.widget.PTimeEntry import PTimeEntry  # noqa


class PTimeEntryRow(Adw.PreferencesRow):
    def __init__(
        self,
        title,
        start_minutes,
        end_minutes,
        limit_minutes,
        day_index,
        is_active,
        on_start_time_changed,
        on_end_time_changed,
        on_limit_changed,
        on_activated,
    ):
        super().__init__(height_request=50)

        box = Gtk.Box(hexpand=True)
        box_items = Gtk.Box(homogeneous=True, hexpand=True)
        box_items.append(Gtk.Label(halign="start", label=title, margin_start=12))

        # Start
        ptime_start = PTimeEntry(start_minutes, on_start_time_changed, day_index)
        # End
        ptime_end = PTimeEntry(end_minutes, on_end_time_changed, day_index)
        # Usage Limit
        ptime_limit = PTimeEntry(limit_minutes, on_limit_changed, day_index)

        box_items.append(ptime_start)
        box_items.append(ptime_end)
        box_items.append(ptime_limit)

        # Active Switch
        switch = Gtk.Switch(
            halign="center",
            valign="center",
            margin_end=12,
            active=is_active,
        )
        switch.connect("state-set", on_activated, day_index)
        switch.bind_property(
            "active", box_items, "sensitive", GObject.BindingFlags.SYNC_CREATE
        )

        box.append(box_items)
        box.append(switch)
        self.set_child(box)
