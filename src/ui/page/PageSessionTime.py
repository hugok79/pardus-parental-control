import ui.widget.PActionRow as PActionRow
from ui.widget.PTimeChooserRow import PTimeChooserRow
from locale import gettext as _


import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Gio, GObject, Adw  # noqa


class PageSessionTime(Adw.PreferencesPage):
    def __init__(self, preferences_manager):
        super().__init__()

        self.preferences_manager = preferences_manager
        self.username = None
        self.preferences = None

        self.setup_ui()

    def set_username(self, username):
        if username is None:
            return

        self.preferences = self.preferences_manager.get_user(username)
        self.username = username

        # Remove UI
        self.remove(self.group_switch)
        self.remove(self.group_start)
        self.remove(self.group_end)

        # Recreate UI
        self.setup_ui()

    def setup_ui(self):
        (self.group_switch, switch) = self.setup_group_switch()

        self.group_start = self.setup_group_start()
        self.group_end = self.setup_group_end()

        # Bind Active Switch
        switch.bind_property(
            "state", self.group_start, "sensitive", GObject.BindingFlags.SYNC_CREATE
        )
        switch.bind_property(
            "state", self.group_end, "sensitive", GObject.BindingFlags.SYNC_CREATE
        )

        self.add(self.group_switch)
        self.add(self.group_start)
        self.add(self.group_end)

    def setup_group_switch(self):
        group_switch = Adw.PreferencesGroup()

        switch = Gtk.Switch(
            valign=Gtk.Align.CENTER,
            active=self.preferences.get_is_session_time_filter_active()
            if self.preferences
            else False,
        )
        switch.connect("state-set", self.on_switch_changed)

        row = Adw.ActionRow(title=_("Activate"), use_markup=False)
        row.add_suffix(switch)
        row.set_activatable_widget(switch)

        group_switch.add(row)

        return (group_switch, switch)

    def setup_group_start(self):
        group = Adw.PreferencesGroup(
            title=_("Start Time"),
            description=_("Select the start time of user can use the computer."),
        )

        minutes = self.preferences.get_session_time_start() if self.preferences else 0
        self.time_chooser_start = PTimeChooserRow(self.on_start_time_changed, minutes)
        group.add(self.time_chooser_start)

        return group

    def setup_group_end(self):
        # End Time:
        group = Adw.PreferencesGroup(
            title=_("End Time"),
            description=_(
                "Select the time of the user can't use the computer anymore."
            ),
        )

        minutes = self.preferences.get_session_time_end() if self.preferences else 0
        self.time_chooser_end = PTimeChooserRow(self.on_end_time_changed, minutes)
        group.add(self.time_chooser_end)

        return group

    # == CALLBACKS ==
    def on_switch_changed(self, btn, value):
        if not self.preferences:
            return

        self.preferences.set_is_session_time_filter_active(value)
        self.preferences_manager.save()

    def on_start_time_changed(self, minutes):
        # print("Session start time changed", minutes / 60)

        if minutes > self.time_chooser_end.get_minutes():
            self.time_chooser_end.set_minutes(minutes)

        if not self.preferences:
            return

        self.preferences.set_session_time_start(minutes)
        self.preferences_manager.save()

    def on_end_time_changed(self, minutes):
        # print("Session end time changed", minutes / 60)

        if minutes < self.time_chooser_start.get_minutes():
            self.time_chooser_start.set_minutes(minutes)

        if not self.preferences:
            return

        self.preferences.set_session_time_end(minutes)
        self.preferences_manager.save()
