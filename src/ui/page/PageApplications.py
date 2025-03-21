import ui.widget.PActionRow as PActionRow
from ui.widget.DialogAppChooser import DialogAppChooser
from locale import gettext as _


import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, Adw  # noqa


class PageApplications(Adw.PreferencesPage):
    def __init__(self, parent_window, preferences_manager):
        super().__init__()

        self.preferences_manager = preferences_manager
        self.username = None
        self.preferences = None
        self.dialog_app_chooser = DialogAppChooser(self.on_application_selected)
        self.dialog_app_chooser.set_transient_for(parent_window)

        self.setup_ui()

    def set_username(self, username):
        if username is None:
            return

        self.preferences = self.preferences_manager.get_user(username)
        self.username = username

        # Remove UI
        self.remove(self.group_switch)
        self.remove(self.group_filter_type)
        self.remove(self.group_applications)

        # Recreate UI
        self.setup_ui()

    def setup_ui(self):
        (self.group_switch, switch) = self.setup_group_switch()

        self.group_filter_type = self.setup_group_filter_type()

        self.group_applications = self.setup_group_applications()

        # Bind Active Switch
        switch.bind_property(
            "state",
            self.group_applications,
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
        self.add(self.group_applications)

    def setup_group_switch(self):
        group_switch = Adw.PreferencesGroup()

        switch = Gtk.Switch(
            valign=Gtk.Align.CENTER,
            active=self.preferences.get_application().get_active()
            if self.preferences
            else False,
        )

        row = Adw.ActionRow(
            title=_("Active") if switch.get_active() else _("Activate"),
            use_markup=False,
        )
        row.add_suffix(switch)
        row.set_activatable_widget(switch)

        switch.connect("state-set", self.on_switch_changed, row)
        group_switch.add(row)

        return (group_switch, switch)

    def setup_group_filter_type(self):
        is_allowlist = (
            self.preferences.get_application().get_allowlist()
            if self.preferences
            else False
        )

        group = Adw.PreferencesGroup(
            title=_("Filter Type"),
            description=_("Change the type of filtering for applications"),
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
            subtitle=_("Allow only the selected applications to run. Deny others."),
            activatable_widget=btn_allow,
        )

        row_deny = PActionRow.new(
            title=_("Deny List"),
            subtitle=_("Deny only the selected applications to run. Allow others."),
            activatable_widget=btn_deny,
        )
        group.add(row_allow)
        group.add(row_deny)

        return group

    def setup_group_applications(self):
        group = Adw.PreferencesGroup(
            title=_("Applications"),
            description=_("Select applications the restricted user can or can't open."),
        )

        # Add New Application Button
        btn_add = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"]
        )
        btn_add.connect("clicked", self.on_btn_add_clicked)
        group.set_header_suffix(btn_add)

        # Fill the applications:
        app_list = (
            self.preferences.get_application().get_list() if self.preferences else []
        )
        for desktop_file in app_list:
            app_info = Gio.DesktopAppInfo.new_from_filename(desktop_file)

            self.insert_app_row(group, app_info)

        return group

    def insert_app_row(self, group, app):
        row = PActionRow.new(
            title=app.get_name(),
            subtitle=app.get_id(),
            gicon=app.get_icon(),
            on_deleted=self.on_row_delete_clicked,
            user_data=app,
        )

        group.add(row)

    # == CALLBACKS ==
    def on_switch_changed(self, btn, value, row):
        if not self.preferences:
            return

        row.set_title(_("Active") if value else _("Activate"))
        self.preferences.get_application().set_active(value)
        self.preferences_manager.save()

    def on_btn_add_clicked(self, _btn):
        self.dialog_app_chooser.present()

    def on_btn_allow_clicked(self, btn):
        if not self.preferences:
            return

        if btn.get_active():
            self.preferences.get_application().set_allowlist(True)
            self.preferences_manager.save()

    def on_btn_deny_clicked(self, btn):
        if not self.preferences:
            return

        if btn.get_active():
            self.preferences.get_application().set_allowlist(False)
            self.preferences_manager.save()

    def on_row_delete_clicked(self, _btn, action_row, user_data):
        if not self.preferences:
            return

        if isinstance(user_data, Gio.DesktopAppInfo):
            if self.preferences.get_application().list_remove(user_data.get_filename()):
                self.group_applications.remove(action_row)
                self.preferences_manager.save()

    def on_application_selected(self, app):
        if not self.preferences:
            return

        if self.preferences.get_application().list_insert(app.get_filename()):
            self.insert_app_row(self.group_applications, app)
            self.preferences_manager.save()
