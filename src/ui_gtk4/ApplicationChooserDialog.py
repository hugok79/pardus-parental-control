import ui_gtk4.PActionRow as PActionRow
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib  # noqa

import locale  # noqa
from locale import gettext as _  # noqa


class ApplicationChooserDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window, application_selected_callback):
        super().__init__(
            application=parent_window.get_application(), transient_for=parent_window
        )

        self.setup_window()

        self.setup_ui()

        self.on_application_selected_callback = application_selected_callback

    # == SETUP ==
    def setup_window(self):
        self.set_default_size(450, 600)
        self.set_search_enabled(True)
        self.set_title(_("Select Application..."))
        self.set_hide_on_close(True)

    def setup_ui(self):
        group = Adw.PreferencesGroup(description=_("Loading..."))

        page = Adw.PreferencesPage()
        page.add(group)

        self.add(page)

        GLib.timeout_add(10, self.add_all_applications_to_group, group)

    # == FUNCTIONS ==
    def get_all_applications(self):
        apps = Gio.AppInfo.get_all()
        # Filter only visible applications
        apps = filter(lambda a: a.should_show(), apps)
        apps = sorted(apps, key=lambda a: a.get_name())  # Sort alphabetically

        return list(apps)

    def add_all_applications_to_group(self, group):
        for app in self.get_all_applications():
            action_row = PActionRow.new(
                title=app.get_name(),
                subtitle=app.get_id(),
                gicon=app.get_icon(),
                on_activated=self.on_action_application_selected,
                user_data=app,
            )

            group.add(action_row)

        group.set_description("")

    # == CALLBACKS ==
    def on_action_application_selected(self, action, app):
        self.on_application_selected_callback(app)

        self.close()
