from locale import gettext as _

import gi

import managers.SystemPreferencesManager as SystemPreferencesManager
import system_preferences_changer
import ui.widget.PActionRow as PActionRow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw  # noqa


class SystemPreferencesDialog(Adw.PreferencesWindow):
    def __init__(self):
        super().__init__()

        self.preferences = SystemPreferencesManager.get_default()

        self.setup_window()

        self.setup_ui()

    # == SETUP ==
    def setup_window(self):
        self.set_default_size(450, 600)
        self.set_search_enabled(True)
        self.set_title(_("System Preferences"))
        self.set_hide_on_close(True)

    def setup_ui(self):
        group = Adw.PreferencesGroup(
            description=_('DNS Servers (default: "1.1.1.1, 1.0.0.1")')
        )

        dns_servers = ", ".join(self.preferences.get_base_dns_servers())
        action_row = Adw.EntryRow(
            title=_("DNS Servers:"),
            text=dns_servers,
            show_apply_button=True,
            activates_default=True,
            use_markup=False,
        )
        action_row.connect("entry_activated", self.on_dns_edited)
        action_row.connect("apply", self.on_dns_edited)

        group.add(action_row)

        page = Adw.PreferencesPage()
        page.add(group)

        self.add(page)

    # == FUNCTIONS ==

    # == CALLBACKS ==
    def on_dns_edited(self, row):
        value = row.get_text().strip()
        dns_servers = self.preferences.extract_dns_list(value)

        if dns_servers:
            p = system_preferences_changer.run(["dns", value])
            if p.returncode == 0:
                # Update our local cache
                self.preferences.set_base_dns_servers(dns_servers)
                row.remove_css_class("error")
            else:
                print("DNS Editing failed")
        else:
            row.add_css_class("error")
