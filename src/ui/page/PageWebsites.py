import ui.widget.PActionRow as PActionRow
from locale import gettext as _


import re
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Gio, GObject, Adw  # noqa


class PageWebsites(Adw.PreferencesPage):
    def __init__(self, preferences_manager):
        super().__init__()

        self.preferences_manager = preferences_manager
        self.username = None
        self.preferences = None
        self.regex = r"^([\w-]+)\.(\w[\w.-]*[a-zA-Z])$"  # Valid Domain Check Regex

        self.setup_ui()

    def set_username(self, username):
        if username is None:
            return

        self.preferences = self.preferences_manager.get_user(username)
        self.username = username

        # Remove UI
        self.remove(self.group_switch)
        self.remove(self.group_filter_type)
        self.remove(self.group_websites)

        # Recreate UI
        self.setup_ui()

    def setup_ui(self):
        (self.group_switch, switch) = self.setup_group_switch()

        self.group_filter_type = self.setup_group_filter_type()

        self.group_websites = self.setup_group_websites()

        # Bind Active Switch
        switch.bind_property(
            "state",
            self.group_websites,
            "sensitive",
            GObject.BindingFlags.SYNC_CREATE,
        )
        switch.bind_property(
            "state",
            self.group_filter_type,
            "sensitive",
            GObject.BindingFlags.SYNC_CREATE,
        )

        self.add(self.group_switch)
        self.add(self.group_filter_type)
        self.add(self.group_websites)

    def setup_group_switch(self):
        group_switch = Adw.PreferencesGroup()

        switch = Gtk.Switch(
            valign=Gtk.Align.CENTER,
            active=self.preferences.get_is_website_filter_active()
            if self.preferences
            else False,
        )
        switch.connect("state-set", self.on_switch_changed)

        row = Adw.ActionRow(title=_("Activate"), use_markup=False)
        row.add_suffix(switch)
        row.set_activatable_widget(switch)

        group_switch.add(row)

        return (group_switch, switch)

    def setup_group_filter_type(self):
        is_allowlist = (
            self.preferences.get_is_website_list_allowlist()
            if self.preferences
            else False
        )

        group = Adw.PreferencesGroup(
            title=_("Filter Type"),
            description=_("Change the type of filtering for websites"),
        )

        btn_allow = Gtk.CheckButton(active=is_allowlist)
        btn_deny = Gtk.CheckButton(
            active=(not is_allowlist),
            group=btn_allow,
        )
        btn_allow.connect("toggled", self.on_btn_allow_clicked)
        btn_deny.connect("toggled", self.on_btn_deny_clicked)

        row_allow = PActionRow.new(
            title=_("Allow List"),
            subtitle=_("Allow only the websites in list. Deny others."),
            activatable_widget=btn_allow,
        )

        row_deny = PActionRow.new(
            title=_("Deny List"),
            subtitle=_("Deny only the websites in list. Allow others."),
            activatable_widget=btn_deny,
        )

        group.add(row_allow)
        group.add(row_deny)

        return group

    def setup_group_websites(self):
        group = Adw.PreferencesGroup(
            title=_("Websites"),
            description=_("Enter websites the restricted user can or can't open."),
        )

        # "New website" row
        self.row_new_website = Adw.EntryRow(
            title=_("example.com"), activates_default=True
        )
        self.row_new_website.set_input_purpose(Gtk.InputPurpose.ALPHA)
        self.row_new_website.set_visible(False)
        self.row_new_website.connect("entry_activated", self.on_new_website_entered)
        self.row_new_website.connect("apply", self.on_new_website_entered)

        group.add(self.row_new_website)

        # Add New Website Button
        btn_add = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"]
        )
        btn_add.connect("clicked", self.on_btn_add_clicked)
        group.set_header_suffix(btn_add)

        # Websites
        domains = self.preferences.get_website_list() if self.preferences else []
        for domain in domains:
            self.insert_website_row(group, domain)

        return group

    def insert_website_row(self, group, domain):
        row = PActionRow.new(
            title=domain,
            on_deleted=self.on_row_delete_clicked,
        )

        group.add(row)

    def is_regex_valid(self, text):
        if self.regex is not None:
            return re.search(self.regex, text) is not None
        else:
            return True

    # == CALLBACKS ==
    def on_switch_changed(self, btn, value):
        if not self.preferences:
            return

        self.preferences.set_is_website_filter_active(value)
        self.preferences_manager.save()

    def on_btn_add_clicked(self, btn):
        self.row_new_website.set_visible(True)
        self.row_new_website.grab_focus()

    def on_btn_allow_clicked(self, btn):
        if not self.preferences:
            return

        if btn.get_active():
            self.preferences.set_is_website_list_allowlist(True)
            self.preferences_manager.save()

    def on_btn_deny_clicked(self, btn):
        if not self.preferences:
            return

        if btn.get_active():
            self.preferences.set_is_website_list_allowlist(False)
            self.preferences_manager.save()

    def on_new_website_entered(self, entry_row):
        if not self.preferences:
            return

        domain = entry_row.get_text()

        if not self.is_regex_valid(domain):
            entry_row.add_css_class("error")
            return
        else:
            entry_row.remove_css_class("error")

        if self.preferences.insert_website(domain):
            self.insert_website_row(self.group_websites, domain)
        else:
            entry_row.add_css_class("error")
            return

        self.row_new_website.set_visible(False)
        self.row_new_website.set_text("")

        self.preferences_manager.save()

    def on_row_delete_clicked(self, btn, action_row, user_data):
        if not self.preferences:
            return

        domain = action_row.get_title()

        if self.preferences.remove_website(domain):
            self.group_websites.remove(action_row)

            self.preferences_manager.save()
