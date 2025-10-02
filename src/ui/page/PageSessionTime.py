from locale import gettext as _
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Adw  # noqa

from ui.widget.PTimeEntryRow import PTimeEntryRow


class PageSessionTime(Adw.PreferencesPage):
    def __init__(self, preferences_manager):
        super().__init__()

        self.preferences_manager = preferences_manager
        self.username = None
        self.preferences = None
        self.group = None

    def set_username(self, username):
        if username is None:
            return

        self.preferences = self.preferences_manager.get_user(username)
        self.username = username

        # Remove UI
        if self.group:
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
        day_titles = [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
        ]
        prefs = self.preferences.get_daily_usage()

        for i in range(len(day_titles)):
            print(f"Day - {i}:", prefs.get_start(i), prefs.get_end(i), prefs.get_limit(i), prefs.get_active(i))
            self.group.add(
                PTimeEntryRow(
                    title=day_titles[i],
                    start_minutes=prefs.get_start(i),
                    end_minutes=prefs.get_end(i),
                    limit_minutes=prefs.get_limit(i),
                    is_active=prefs.get_active(i),
                    day_index=i,
                    on_start_time_changed=self.on_start_time_changed,
                    on_end_time_changed=self.on_end_time_changed,
                    on_limit_changed=self.on_limit_changed,
                    on_activated=self.on_day_activated,
                )
            )

        self.add(self.group)

    # == CALLBACKS ==
    def on_start_time_changed(self, minutes, user_data):
        day_index = user_data[0]
        print("start_time:", minutes, user_data, day_index)

        if not self.preferences:
            return

        self.preferences.get_daily_usage().set_start(day_index, minutes)
        self.preferences_manager.save()


    def on_end_time_changed(self, minutes, user_data):
        day_index = user_data[0]
        print("end_time:", minutes, user_data, day_index)

        if not self.preferences:
            return

        self.preferences.get_daily_usage().set_end(day_index, minutes)
        self.preferences_manager.save()


    def on_limit_changed(self, minutes, user_data):
        day_index = user_data[0]
        print("limit:", minutes, user_data, day_index)

        if not self.preferences:
            return

        self.preferences.get_daily_usage().set_limit(day_index, minutes)
        self.preferences_manager.save()


    def on_day_activated(self, switch, value, day_index):
        if not self.preferences:
            return

        self.preferences.get_daily_usage().set_active(day_index, value)
        self.preferences_manager.save()
