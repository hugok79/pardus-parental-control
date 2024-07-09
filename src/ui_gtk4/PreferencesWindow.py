import ui_gtk4.PActionRow as PActionRow
from managers.ProfileManager import ProfileManager, Profile
import managers.LinuxUserManager as LinuxUserManager
from ui_gtk4.PTimePeriodChooser import PTimePeriodChooser
from ui_gtk4.ApplicationChooserDialog import ApplicationChooserDialog
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib  # noqa


class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, profile_manager: ProfileManager, parent_window):
        super().__init__(transient_for=parent_window)

        self.profile_manager = profile_manager

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
            self, self.on_application_selected_in_dialog
        )

    def setup_applications_page(self):
        self.page_applications = Adw.PreferencesPage(
            title="Applications", icon_name="application-x-executable-symbolic"
        )
        self.group_applications = None
        self.setup_applications_group()

        # Allow / Deny toggle button
        current_profile = self.profile_manager.get_current_profile()
        is_application_list_allowlist = (
            current_profile.get_is_application_list_allowlist()
        )

        group_allow_deny_application = Adw.PreferencesGroup(
            title="Filter Type",
            description="Change the type of filtering for applications",
        )

        btn_application_allow_toggle = Gtk.CheckButton(
            active=is_application_list_allowlist
        )
        btn_application_deny_toggle = Gtk.CheckButton(
            active=(not is_application_list_allowlist),
            group=btn_application_allow_toggle,
        )

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
            "toggled", self.on_toggle_application_allow
        )
        btn_application_deny_toggle.connect("toggled", self.on_toggle_application_deny)

    def setup_websites_page(self):
        self.page_websites = Adw.PreferencesPage(
            title="Websites", icon_name="web-browser-symbolic"
        )

        self.group_websites = None
        self.setup_websites_group()

        # Allow / Deny toggle button
        current_profile = self.profile_manager.get_current_profile()
        is_website_list_allowlist = current_profile.get_is_website_list_allowlist()

        group_allow_deny_website = Adw.PreferencesGroup(
            title="Filter Type",
            description="Change the type of filtering for applications",
        )

        btn_website_allow_toggle = Gtk.CheckButton(active=is_website_list_allowlist)
        btn_website_deny_toggle = Gtk.CheckButton(
            active=(not is_website_list_allowlist), group=btn_website_allow_toggle
        )

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

        btn_website_allow_toggle.connect("toggled", self.on_toggle_website_allow)
        btn_website_deny_toggle.connect("toggled", self.on_toggle_website_deny)

    def setup_users_page(self):
        self.page_users = Adw.PreferencesPage(
            title="Users", icon_name="system-users-symbolic"
        )

        self.group_users = None
        self.setup_users_group()

    def setup_session_time_page(self):
        self.page_session_time = Adw.PreferencesPage(
            title="Session Time", icon_name="document-open-recent-symbolic"
        )

        self.group_session_time = None
        self.setup_session_time_group()

    def setup_ui(self):
        # Applications
        self.setup_applications_page()

        # Websites
        self.setup_websites_page()

        # Users
        self.setup_users_page()

        # Users
        # self.setup_session_time_page()

        # Add Pages
        self.add(self.page_applications)
        self.add(self.page_websites)
        self.add(self.page_users)
        # self.add(self.page_session_time)

        # Fill groups
        self.fill_lists_from_profile(self.profile_manager.get_current_profile())

    def setup_applications_group(self):
        if self.group_applications:
            self.page_applications.remove(self.group_applications)
            self.group_applications = None

        self.group_applications = Adw.PreferencesGroup(
            title="Applications",
            description="Select applications the restricted user can or can't open.",
        )

        btn_new_application = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"]
        )
        btn_new_application.connect("clicked", self.on_btn_new_application_clicked)
        self.group_applications.set_header_suffix(btn_new_application)

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
            title="example.com", activates_default=True, show_apply_button=True
        )
        self.row_new_website.set_input_purpose(Gtk.InputPurpose.ALPHA)
        self.row_new_website.set_visible(False)
        self.row_new_website.connect("entry_activated", self.on_new_website_entered)
        self.row_new_website.connect("apply", self.on_new_website_entered)
        self.group_websites.add(self.row_new_website)

        btn_add_website = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"]
        )
        btn_add_website.connect("clicked", self.on_btn_add_website_clicked)
        self.group_websites.set_header_suffix(btn_add_website)

        self.page_websites.add(self.group_websites)

    def setup_users_group(self):
        if self.group_users:
            self.page_users.remove(self.group_users)
            self.group_users = None

        self.group_users = Adw.PreferencesGroup(
            title="Users",
            description="Select users will be restricted.",
        )

        self.page_users.add(self.group_users)

    def setup_session_time_group(self):
        if self.group_session_time:
            self.page_session_time.remove(self.group_session_time)
            self.group_session_time = None

        self.group_session_time = Adw.PreferencesGroup(
            title="Session Time",
            description="Select the time period user can use the computer.",
        )

        current_profile = self.profile_manager.get_current_profile()

        # Time selection Row
        self.session_time_chooser = PTimePeriodChooser(
            self.on_session_time_period_changed,
            current_profile.get_session_time_start(),
            current_profile.get_session_time_end(),
        )
        row_time_selection = Adw.ActionRow(title="Select Time")
        row_time_selection.add_suffix(self.session_time_chooser)

        self.group_session_time.add(row_time_selection)

        self.page_session_time.add(self.group_session_time)

    # Functions

    def fill_lists_from_profile(self, profile: Profile):
        # Clear the application list:
        self.setup_applications_group()

        # Applications
        for app_id in profile.get_application_list():
            app_info = Gio.DesktopAppInfo.new(app_id)

            self.insert_application_row_to_group(app_info)

        # Clear the website list:
        self.setup_websites_group()

        # Websites
        for domain in profile.get_website_list():
            self.insert_website_row_to_group(domain)

        # Clear the user list:
        self.setup_users_group()

        # Add Users
        for user in LinuxUserManager.get_standard_users():
            is_checked = user.get_uid() in profile.get_user_list()
            self.insert_user_row_to_group(user, is_checked)

    def insert_application_row_to_group(self, app):
        app_name = GLib.markup_escape_text(app.get_name(), len(app.get_name()))
        action_row = PActionRow.new(
            title=app_name,
            subtitle=app.get_id(),
            gicon=app.get_icon(),
            on_deleted=self.on_btn_delete_row_clicked,
            user_data=app,
        )

        self.group_applications.add(action_row)

    def insert_website_row_to_group(self, website_domain):
        action_row = PActionRow.new(
            title=website_domain,
            on_deleted=self.on_btn_delete_row_clicked,
        )

        self.group_websites.add(action_row)

    def insert_user_row_to_group(self, user, is_checked):
        avatar = Adw.Avatar(
            size=32,
            text=user.get_user_name(),
            show_initials=True,
        )

        btn_check = Gtk.CheckButton(active=is_checked, css_classes=["selection-mode"])
        btn_check.connect("toggled", self.on_btn_user_select_clicked, user.get_uid())

        action_row = Adw.ActionRow(title=user.get_user_name())
        action_row.add_prefix(avatar)
        action_row.add_suffix(btn_check)
        action_row.set_activatable_widget(btn_check)

        self.group_users.add(action_row)

    # == CALLBACKS ==
    def on_btn_user_select_clicked(self, btn, user_id):
        current_profile = self.profile_manager.get_current_profile()

        if btn.get_active():
            current_profile.insert_user(user_id)
        else:
            current_profile.remove_user(user_id)

        self.profile_manager.save_as_json_file()

    def on_btn_new_application_clicked(self, btn):
        self.dialog_app_chooser.present()

    def on_btn_add_website_clicked(self, btn):
        self.row_new_website.set_visible(True)
        self.row_new_website.grab_focus()

    def on_btn_delete_row_clicked(self, btn, action_row, user_data):
        current_profile = self.profile_manager.get_current_profile()

        if isinstance(user_data, Gio.DesktopAppInfo):
            app_id = user_data.get_id()

            if current_profile.remove_application(app_id):
                self.group_applications.remove(action_row)
        else:
            # Website domains
            domain = action_row.get_title()

            if current_profile.remove_website(domain):
                self.group_websites.remove(action_row)

        self.profile_manager.save_as_json_file()

    def on_application_selected_in_dialog(self, app):
        current_profile = self.profile_manager.get_current_profile()

        if current_profile.insert_application(app.get_id()):
            self.insert_application_row_to_group(app)

        self.profile_manager.save_as_json_file()

    def on_new_website_entered(self, entry_row):
        current_profile = self.profile_manager.get_current_profile()

        if current_profile.insert_website(entry_row.get_text()):
            self.insert_website_row_to_group(entry_row.get_text())

        self.row_new_website.set_visible(False)
        self.row_new_website.set_text("")

        self.profile_manager.save_as_json_file()

    def on_toggle_application_allow(self, btn):
        current_profile = self.profile_manager.get_current_profile()

        if btn.get_active():
            current_profile.set_is_application_list_allowlist(True)
            self.profile_manager.save_as_json_file()

    def on_toggle_application_deny(self, btn):
        current_profile = self.profile_manager.get_current_profile()

        if btn.get_active():
            current_profile.set_is_application_list_allowlist(False)
            self.profile_manager.save_as_json_file()

    def on_toggle_website_allow(self, btn):
        current_profile = self.profile_manager.get_current_profile()

        if btn.get_active():
            current_profile.set_is_website_list_allowlist(True)
            self.profile_manager.save_as_json_file()

    def on_toggle_website_deny(self, btn):
        current_profile = self.profile_manager.get_current_profile()

        if btn.get_active():
            current_profile.set_is_website_list_allowlist(False)
            self.profile_manager.save_as_json_file()

    def on_session_time_period_changed(self, start_seconds, end_seconds):
        current_profile = self.profile_manager.get_current_profile()

        current_profile.set_session_time_start(start_seconds)
        current_profile.set_session_time_end(end_seconds)

        self.profile_manager.save_as_json_file()
