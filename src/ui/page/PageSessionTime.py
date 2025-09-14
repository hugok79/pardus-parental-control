from locale import gettext as _
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Adw  # noqa

from ui.widget.PTimeChooserRow import PTimeChooserRow
from ui.widget.PTimeEntry import PTimeEntry
from ui.widget.PTimeEntryRow import PTimeEntryRow


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
        self.remove(self.group)

        # Recreate UI
        self.setup_ui()

    def setup_ui(self):
        self.group = Adw.PreferencesGroup(
            title=_("Limit Session Time"),
            description=_(
                "Set start-end hours of a session.\nLimit maximum hours to use PC between start and end hours."
            ),
        )

        # Headers
        row = Adw.PreferencesRow()
        box = Gtk.Box(css_classes=["m-7"])
        box_items = Gtk.Box(homogeneous=True, hexpand=True)
        box_items.append(Gtk.Label(label=""))
        box_items.append(Gtk.Label(css_classes=["heading"], label=_("Start")))
        box_items.append(Gtk.Label(css_classes=["heading"], label=_("End")))
        box_items.append(Gtk.Label(css_classes=["heading"], label=_("Usage Limit")))

        box.append(box_items)
        box.append(
            Gtk.Label(
                css_classes=["heading"], label=_("Active"), width_request=56
            )  # todo, remove width_request, do better table view
        )
        row.set_child(box)
        self.group.add(row)

        # Days
        days = [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
        ]

        for i in range(len(days)):
            self.group.add(
                PTimeEntryRow(
                    days[i], 0, self.on_time_changed, self.on_day_activated, i, False
                )
            )

        self.add(self.group)

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

    def on_time_changed(self, minutes, user_data):
        print(minutes, user_data)

    def on_day_activated(self, switch, value, day_index):
        print(value, day_index)

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
