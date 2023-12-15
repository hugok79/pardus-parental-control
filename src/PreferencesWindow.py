import PActionRow
import Profiles
from InputDialog import InputDialog
from ApplicationChooserDialog import ApplicationChooserDialog
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib  # noqa


class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, parent_window):
        super().__init__(transient_for=parent_window)

        self.setup_window()

        self.setup_ui()

        self.setup_dialogs()

    # Setups

    def setup_window(self):
        self.set_default_size(800, 600)
        self.set_title("Preferences")
        self.set_hide_on_close(True)

    def setup_dialogs(self):
        self.dialog_app_chooser = ApplicationChooserDialog(
            self, self.on_application_selected_in_dialog)

    def setup_ui(self):
        # Applications
        self.page_applications = Adw.PreferencesPage(
            title="Applications",
            icon_name="application-x-executable-symbolic"
        )
        self.group_applications = None
        self.setup_applications_group()

        # Allow / Deny toggle button
        is_application_list_allowed = Profiles.get_current_profile_property(
            "is_application_list_allowed")

        group_allow_deny_application = Adw.PreferencesGroup(
            title="Filter Choice", description='Change the choice of "Allowing" or "Denying" access to applications')

        btn_application_allow_toggle = Gtk.CheckButton(
            active=is_application_list_allowed)
        btn_application_deny_toggle = Gtk.CheckButton(active=(not is_application_list_allowed),
                                                      group=btn_application_allow_toggle)

        row_allow_application = PActionRow.new(
            title="Allow Only",
            subtitle="Allow only the selected applications to run. Deny others.",
            activatable_widget=btn_application_allow_toggle,
        )

        row_deny_application = PActionRow.new(
            title="Deny Only",
            subtitle="Deny only the selected applications to run. Allow others.",
            activatable_widget=btn_application_deny_toggle,
        )
        group_allow_deny_application.add(row_allow_application)
        group_allow_deny_application.add(row_deny_application)
        self.page_applications.add(group_allow_deny_application)

        btn_application_allow_toggle.connect(
            "toggled", self.on_toggle_application_allow)
        btn_application_deny_toggle.connect(
            "toggled", self.on_toggle_application_deny)

        # Websites
        self.page_websites = Adw.PreferencesPage(
            title="Websites",
            icon_name="web-browser-symbolic"
        )

        self.group_websites = None
        self.setup_websites_group()

        # Allow / Deny toggle button
        is_website_list_allowed = Profiles.get_current_profile_property(
            "is_website_list_allowed")

        group_allow_deny_website = Adw.PreferencesGroup(
            title="Filter Choice", description='Change the choice of "Allowing" or "Denying" access to websites')

        btn_website_allow_toggle = Gtk.CheckButton(
            active=is_website_list_allowed)
        btn_website_deny_toggle = Gtk.CheckButton(active=(not is_website_list_allowed),
                                                  group=btn_website_allow_toggle)

        row_allow_website = PActionRow.new(
            title="Allow Only",
            subtitle="Allow only the selected websites to access. Deny others.",
            activatable_widget=btn_website_allow_toggle,
        )

        row_deny_website = PActionRow.new(
            title="Deny Only",
            subtitle="Deny only the selected websites to access. Allow others.",
            activatable_widget=btn_website_deny_toggle,
        )
        group_allow_deny_website.add(row_allow_website)
        group_allow_deny_website.add(row_deny_website)
        self.page_websites.add(group_allow_deny_website)

        btn_website_allow_toggle.connect(
            "toggled", self.on_toggle_website_allow)
        btn_website_deny_toggle.connect(
            "toggled", self.on_toggle_website_deny)

        # Add Pages
        self.add(self.page_applications)
        self.add(self.page_websites)

        # Fill groups
        self.fill_lists_from_profile(Profiles.get_current_profile())

    def setup_applications_group(self):
        if self.group_applications:
            self.page_applications.remove(self.group_applications)
            self.group_applications = None

        self.group_applications = Adw.PreferencesGroup(
            title="Applications",
            description="Select applications the restricted user can or can't open.",
        )

        btn_add_application = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"])
        btn_add_application.connect(
            "clicked", self.on_btn_add_application_clicked)
        self.group_applications.set_header_suffix(btn_add_application)

        self.page_applications.add(self.group_applications)

    def setup_websites_group(self):
        if self.group_websites:
            self.page_websites.remove(self.group_websites)
            self.group_websites = None

        self.group_websites = Adw.PreferencesGroup(
            title="Websites",
            description="Select websites the restricted user can or can't open.",
        )

        # "New website" row
        self.row_new_website = Adw.EntryRow(
            title="example.com", activates_default=True, show_apply_button=True)
        self.row_new_website.set_input_purpose(Gtk.InputPurpose.ALPHA)
        self.row_new_website.set_visible(False)
        self.row_new_website.connect(
            "entry_activated", self.on_new_website_entered)
        self.row_new_website.connect("apply", self.on_new_website_entered)
        self.group_websites.add(self.row_new_website)

        btn_add_website = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"])
        btn_add_website.connect("clicked", self.on_btn_add_website_clicked)
        self.group_websites.set_header_suffix(btn_add_website)

        self.page_websites.add(self.group_websites)

    # Functions
    def fill_lists_from_profile(self, profile):
        # Clear the application list:
        self.setup_applications_group()

        # Applications
        for app_id in profile["application_list"]:
            app_info = Gio.DesktopAppInfo.new(app_id)

            self.insert_application_row_to_group(app_info)

        # Clear the application list:
        self.setup_websites_group()

        # Websites
        for domain in profile["website_list"]:
            self.insert_website_row_to_group(domain)

    def insert_application_row_to_group(self, app):
        app_name = GLib.markup_escape_text(app.get_name(), len(app.get_name()))
        action_row = PActionRow.new(
            title=app_name,
            subtitle=app.get_id(),
            gicon=app.get_icon(),
            on_deleted=self.on_btn_delete_row_clicked,
            user_data=app
        )

        self.group_applications.add(action_row)

    def insert_website_row_to_group(self, website_domain):
        action_row = PActionRow.new(
            title=website_domain,
            on_deleted=self.on_btn_delete_row_clicked,
        )

        self.group_websites.add(action_row)

    # == CALLBACKS ==
    def on_btn_add_application_clicked(self, btn):
        self.dialog_app_chooser.present()

    def on_btn_add_website_clicked(self, btn):
        self.row_new_website.set_visible(True)
        self.row_new_website.grab_focus()

    def on_btn_delete_row_clicked(self, btn, action_row):
        try:
            # Applications
            app = action_row._app

            if Profiles.remove_application_to_current_profile(app.get_id()):
                self.group_applications.remove(action_row)
        except AttributeError:
            # Website domains
            if Profiles.remove_website_to_current_profile(action_row.get_title()):
                self.group_websites.remove(action_row)

        print(Profiles.get_current_profile())

    def on_application_selected_in_dialog(self, app):
        if Profiles.add_application_to_current_profile(app.get_id()):
            self.insert_application_row_to_group(app)

        print(Profiles.get_current_profile())

    def on_new_website_entered(self, entry_row):
        if Profiles.add_website_to_current_profile(entry_row.get_text()):
            self.insert_website_row_to_group(entry_row.get_text())

        self.row_new_website.set_visible(False)
        self.row_new_website.set_text("")

        print(Profiles.get_current_profile())

    def on_toggle_application_allow(self, btn):
        if btn.get_active():
            Profiles.change_current_profile_property(
                "is_application_list_allowed", True)

    def on_toggle_application_deny(self, btn):
        if btn.get_active():
            Profiles.change_current_profile_property(
                "is_application_list_allowed", False)

    def on_toggle_website_allow(self, btn):
        if btn.get_active():
            Profiles.change_current_profile_property(
                "is_website_list_allowed", True)

    def on_toggle_website_deny(self, btn):
        if btn.get_active():
            Profiles.change_current_profile_property(
                "is_website_list_allowed", False)
