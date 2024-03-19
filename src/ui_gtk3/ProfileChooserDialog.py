import ui_gtk3.PActionRow as PActionRow
from ui_gtk3.InputDialog import InputDialog
from managers.ProfileManager import ProfileManager
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib  # noqa


class ProfileChooserDialog(Gtk.Window):
    def __init__(
        self,
        profile_manager: ProfileManager,
        parent_window,
        profile_selected_callback,
    ):
        super().__init__(
            application=parent_window.get_application(), transient_for=parent_window
        )

        self.profile_manager = profile_manager

        self.setup_window()

        self.setup_ui()

        self.selected_profile = self.profile_manager.get_current_profile_name()

        self.on_profile_selected_callback = profile_selected_callback

    # == SETUP ==
    def setup_window(self):
        self.set_default_size(300, 400)
        self.set_title("Select Profile...")
        self.connect("delete-event", self.on_window_delete)

    def setup_ui(self):
        box = Gtk.Box(spacing=7, orientation="vertical", margin=14)

        # Fill the List of Profiles
        self.cmb_current_profile = Gtk.ComboBoxText()

        current_profile_index = 0
        i = 0
        for profile_name in self.profile_manager.get_profile_list():
            self.cmb_current_profile.append_text(profile_name)

            if profile_name == self.profile_manager.get_current_profile_name():
                current_profile_index = i

            i += 1

        # Current Profile ComboRow
        self.cmb_current_profile.set_active(current_profile_index)
        self.cmb_current_profile.connect("changed", self.on_current_profile_changed)
        box.add(Gtk.Label(label="Current Profile:", halign="start"))
        box.add(self.cmb_current_profile)
        box.add(Gtk.Separator())

        # New Profile button
        btn_new = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        btn_new.set_always_show_image(True)
        btn_new.connect("clicked", self.on_btn_new_clicked)
        box.add(btn_new)

        """
        # New Profile Hidden EntryRow
        self.row_new_profile = Adw.EntryRow(
            title="New Profile Name", activates_default=True, show_apply_button=True
        )
        self.row_new_profile.set_input_purpose(Gtk.InputPurpose.ALPHA)
        self.row_new_profile.set_visible(False)
        self.row_new_profile.connect("entry_activated", self.on_new_profile_entered)
        self.row_new_profile.connect("apply", self.on_new_profile_entered)
        self.group_profiles.add(self.row_new_profile)

        # Pages
        page = Adw.PreferencesPage()
        page.add(current_profile_group)
        page.add(self.group_profiles)

        self.add(page)
        """

        # Profiles ListBox
        self.listbox_profiles = Gtk.ListBox()
        box.add(self.listbox_profiles)

        # Finish
        self.add(box)

        self.fill_profiles_group()

    # == FUNCTIONS ==
    def add_profile_entry_row(self, profile_name):
        action_row = PActionRow.new(
            title=profile_name,
            on_deleted=self.on_btn_delete_row_clicked,
            on_edited=self.on_profile_name_changed,
        )

        self.listbox_profiles.add(action_row)

    def fill_profiles_group(self):
        for key, value in self.profile_manager.get_profile_list().items():
            self.add_profile_entry_row(key)

    def show_dialog(self, msg, msg_type=Gtk.MessageType.INFO):
        dialog = Gtk.MessageDialog(
            text=msg, message_type=msg_type, buttons=Gtk.ButtonsType.OK
        )

        dialog.run()
        dialog.destroy()

    # == CALLBACKS ==
    def on_window_delete(self, win, event):
        # Don't delete window on close, just hide.
        self.hide()
        return True

    def on_btn_new_clicked(self, btn):
        input_dialog = InputDialog(
            self, "Enter Profile Name", "", self.on_new_profile_entered
        )

    def on_new_profile_entered(self, text):
        new_profile_name = text

        if self.profile_manager.has_profile_name(new_profile_name):
            self.row_new_profile.set_css_classes(["entry", "activatable", "error"])

            self.show_dialog(
                f"Error: '{new_profile_name}' exists!", Gtk.MessageType.ERROR
            )

        else:
            # New profile created
            self.profile_manager.insert_default_profile(new_profile_name)

            # Update profiles in Gtk.ComboBoxText
            self.cmb_current_profile.append_text(new_profile_name)

            # Add Row
            self.add_profile_entry_row(new_profile_name)

            self.show_dialog(f"New profile created: '{new_profile_name}'")

            # self.row_new_profile.set_css_classes(["entry", "activatable"])
            self.row_new_profile.set_visible(False)
            self.row_new_profile.set_text("")

    def on_btn_delete_row_clicked(self, btn, action_row, user_data):
        # Checks
        if len(self.profile_manager.get_profile_list()) == 1:
            self.show_dialog("At least one profile required.")
            return False

        profile_name = action_row.title
        current_profile = self.profile_manager.get_current_profile_name()

        if profile_name == current_profile:
            self.show_dialog("You can't remove the current profile.")
            return False

        # Remove from ListBox
        self.listbox_profiles.remove(action_row)

        # Remove from Gtk.ComboBoxText
        for row_widget in self.cmb_current_profile.get_children():
            if row_widget.get_text() == profile_name:
                self.cmb_current_profile.remove(row_widget)
                break

        # Remove from profiles.json
        self.profile_manager.remove_profile(profile_name)

    def on_current_profile_changed(self, combobox):
        self.selected_profile = combobox.get_active_text()

        self.profile_manager.set_current_profile(self.selected_profile)

        self.on_profile_selected_callback(self.selected_profile)

    def on_profile_name_changed(self, entry_row):
        new_name = entry_row.get_text()

        if self.profile_manager.has_profile_name(new_name):
            self.show_dialog(f"Error: '{new_name}' exists!", Gtk.MessageType.ERROR)

            return False

        old_name = entry_row.title

        # Update profiles.json
        self.profile_manager.update_profile_name(old_name, new_name)

        # Update Gtk.ComboBoxText
        for modelrow in self.cmb_current_profile.get_model():
            if modelrow[0] == old_name:
                modelrow[0] = new_name
                break

        self.show_dialog(f"Profile name changed: '{new_name}'")
        # entry_row.set_css_classes(["entry", "activatable"])

        entry_row.title = new_name
