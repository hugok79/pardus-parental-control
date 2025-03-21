from locale import gettext as _
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Adw  # noqa

from ui.widget.PTimeChooserRow import PTimeChooserRow


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
        self.remove(self.group_weekday)
        self.remove(self.group_weekend)

        # Recreate UI
        self.setup_ui()

    def setup_ui(self):
        self.group_weekday = self.setup_group_times(False)
        self.group_weekend = self.setup_group_times(True)

        self.add(self.group_weekday)
        self.add(self.group_weekend)

    def setup_group_times(self, is_weekend):
        is_active = False
        if self.preferences:
            if is_weekend:
                is_active = (
                    self.preferences.get_session_time().get_weekend().get_active()
                )
            else:
                is_active = (
                    self.preferences.get_session_time().get_weekday().get_active()
                )

        title = _("Weekends") if is_weekend else _("Weekdays")
        subtitle = _("Select the time range of the computer can be used on {}.").format(
            title
        )

        # Expander Row
        expander = Adw.ExpanderRow(
            title=_("Active") if is_active else _("Activate"),
            show_enable_switch=True,
            enable_expansion=is_active,
        )
        expander.connect("notify::enable-expansion", self.on_switch_changed, is_weekend)

        min_start = 0
        min_end = 0
        if self.preferences:
            if is_weekend:
                week = self.preferences.get_session_time().get_weekend()
            else:
                week = self.preferences.get_session_time().get_weekday()

            min_start = week.get_start()
            min_end = week.get_end()

        # Time Choosers
        time_chooser_start = PTimeChooserRow(
            self.on_start_time_changed, min_start, is_weekend
        )
        time_chooser_end = PTimeChooserRow(
            self.on_end_time_changed, min_end, is_weekend
        )
        # Use later to balance values
        time_chooser_start.set_grouped_widget(time_chooser_end)
        time_chooser_end.set_grouped_widget(time_chooser_start)
        time_chooser_start.add_css_class("view")
        time_chooser_end.add_css_class("view")

        expander.add_row(
            Gtk.Label(
                label=_("Start Time"),
                # margin_start=12,
                margin_top=7,
                margin_bottom=7,
            ),
        )
        expander.add_row(time_chooser_start)
        expander.add_row(
            Gtk.Label(
                label=_("End Time"),
                # margin_start=12,
                margin_top=7,
                margin_bottom=7,
            ),
        )
        expander.add_row(time_chooser_end)

        # Group
        group = Adw.PreferencesGroup(title=title, description=subtitle)
        group.add(expander)

        return group

    # == CALLBACKS ==
    def on_switch_changed(self, expander_row, param, is_weekend):
        if not self.preferences:
            return

        value = expander_row.get_property(param.name)

        pref = self.preferences.get_session_time()
        week = pref.get_weekend() if is_weekend else pref.get_weekday()

        week.set_active(value)
        expander_row.set_title(_("Active") if value else _("Activate"))
        self.preferences_manager.save()

    def on_start_time_changed(self, time_chooser, minutes, is_weekend):
        if not self.preferences:
            return

        pref = self.preferences.get_session_time()
        week = pref.get_weekend() if is_weekend else pref.get_weekday()

        if minutes > week.get_end():
            time_chooser.get_grouped_widget().set_minutes(minutes)

        week.set_start(minutes)
        self.preferences_manager.save()

    def on_end_time_changed(self, time_chooser, minutes, is_weekend):
        if not self.preferences:
            return

        pref = self.preferences.get_session_time()
        week = pref.get_weekend() if is_weekend else pref.get_weekday()

        if minutes < week.get_start():
            time_chooser.get_grouped_widget().set_minutes(minutes)

        week.set_end(minutes)
        self.preferences_manager.save()
