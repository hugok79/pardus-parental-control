import PActionRow
import Profiles
from InputDialog import InputDialog
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib  # noqa


class ProfileChooserDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window, profile_selected_callback):
        super().__init__(application=parent_window.get_application(), transient_for=parent_window)

        self.setup_window()

        self.setup_ui()

        self.selected_profile = Profiles.get_current_profile_name()

        self.on_profile_selected_callback = profile_selected_callback

    # == SETUP ==
    def setup_window(self):
        self.set_default_size(300, 400)
        self.set_search_enabled(True)
        self.set_title("Select Profile...")
        self.set_hide_on_close(True)

    def setup_ui(self):
        self.group_profiles = Adw.PreferencesGroup(
            title="Profiles",
            description="Select a profile to load its settings."
        )

        # Fill the List of Profiles
        self.list_profiles = Gtk.StringList()
        current_profile_index = 0
        i = 0
        for profile_name in Profiles.get_all_profiles():
            self.list_profiles.append(profile_name)

            if profile_name == Profiles.get_current_profile_name():
                current_profile_index = i

            i += 1

        # Current Profile ComboRow
        self.comborow_current_profile = Adw.ComboRow(
            title="Current Profile", model=self.list_profiles)
        self.comborow_current_profile.set_selected(current_profile_index)
        self.comborow_current_profile.connect(
            "notify::selected", self.on_current_profile_changed)
        current_profile_group = Adw.PreferencesGroup()
        current_profile_group.add(self.comborow_current_profile)

        # New Profile button
        btn_add = Gtk.Button(
            icon_name="list-add-symbolic", valign="center", css_classes=["accent"])
        btn_add.connect(
            "clicked", self.on_btn_add_clicked)
        self.group_profiles.set_header_suffix(btn_add)

        # New Profile Hidden EntryRow
        self.row_new_profile = Adw.EntryRow(
            title="New Profile Name", activates_default=True, show_apply_button=True)
        self.row_new_profile.set_input_purpose(Gtk.InputPurpose.ALPHA)
        self.row_new_profile.set_visible(False)
        self.row_new_profile.connect(
            "entry_activated", self.on_new_profile_entered)
        self.row_new_profile.connect("apply", self.on_new_profile_entered)
        self.group_profiles.add(self.row_new_profile)

        # Pages
        page = Adw.PreferencesPage()
        page.add(current_profile_group)
        page.add(self.group_profiles)

        self.add(page)

        self.fill_profiles_group()

    # == FUNCTIONS ==
    def add_profile_entry_row(self, profile_name):
        action_row = PActionRow.new(
            title=profile_name,
            on_deleted=self.on_btn_delete_row_clicked,
            on_edited=self.on_profile_name_changed,
        )

        self.group_profiles.add(action_row)

    def fill_profiles_group(self):
        for key, value in Profiles.get_all_profiles().items():
            self.add_profile_entry_row(key)

    def show_toast(self, msg):
        self.add_toast(
            Adw.Toast(
                title=msg,
                timeout=1
            )
        )

    # == CALLBACKS ==
    def on_btn_add_clicked(self, btn):
        self.row_new_profile.set_visible(True)
        self.row_new_profile.grab_focus()

    def on_new_profile_entered(self, entry_row):
        new_profile_name = entry_row.get_text()

        if Profiles.has_profile_name(new_profile_name):
            self.row_new_profile.set_css_classes(
                ["entry", "activatable", "error"])

            self.show_toast(f"Error: '{new_profile_name}' exists!")

        else:
            # New profile created
            Profiles.create_new_profile(new_profile_name)

            # Update profiles Gtk.StringList
            self.list_profiles.append(new_profile_name)
            self.comborow_current_profile.set_model(self.list_profiles)

            # Add Row
            self.add_profile_entry_row(new_profile_name)

            self.show_toast(f"New profile created: '{new_profile_name}'")

            self.row_new_profile.set_css_classes(["entry", "activatable"])
            self.row_new_profile.set_visible(False)
            self.row_new_profile.set_text("")

    def on_btn_delete_row_clicked(self, btn, action_row, user_data):
        if len(Profiles.get_all_profiles()) == 1:
            self.show_toast("At least one profile required.")
            return False

        profile_name = action_row.get_title()
        current_profile = Profiles.get_current_profile_name()

        if profile_name == current_profile:
            self.show_toast("You can't remove the current profile.")
            return False

        # Remove from group
        self.group_profiles.remove(action_row)

        # Remove from Gtk.StringList
        for i in range(self.list_profiles.get_n_items()):
            if self.list_profiles.get_item(i).get_string() == profile_name:
                self.list_profiles.remove(i)
                break

        self.comborow_current_profile.set_model(self.list_profiles)

        # Remove from profiles.json
        Profiles.delete_profile(profile_name)

    def on_current_profile_changed(self, comborow, selected_index):
        self.selected_profile = comborow.get_selected_item().get_string()

        Profiles.set_current_profile_name(self.selected_profile)

        self.on_profile_selected_callback(self.selected_profile)

    def on_profile_name_changed(self, entry_row):
        new_profile_name = entry_row.get_text()

        if Profiles.has_profile_name(new_profile_name):
            self.show_toast(f"Error: '{new_profile_name}' exists!")

            entry_row.set_css_classes(["entry", "activatable", "error"])

            return False

        old_name = entry_row.get_title()

        # Update profiles.json
        Profiles.change_profile_name(old_name, new_profile_name)

        # Update Gtk.StringList
        for i in range(self.list_profiles.get_n_items()):
            if self.list_profiles.get_item(i).get_string() == old_name:
                self.list_profiles.remove(i)
                self.list_profiles.append(new_profile_name)

                previous_current_profile = self.comborow_current_profile.get_selected_item().get_string()
                self.comborow_current_profile.set_model(self.list_profiles)

                if previous_current_profile == old_name:
                    self.comborow_current_profile.set_selected(
                        self.list_profiles.get_n_items())
                break

        self.show_toast(f"Profile name changed: '{new_profile_name}'")
        entry_row.set_css_classes(["entry", "activatable"])

        entry_row.set_title(new_profile_name)
