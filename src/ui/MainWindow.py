from ui.PreferencesWindow import PreferencesWindow
from ui.ProfileChooserDialog import ProfileChooserDialog
import managers.ProfileManager as ProfileManager

import os
import subprocess
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw  # noqa

CWD = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{CWD}/../../data"


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        # Setup Variables
        self.setup_variables()

        # Setup Actions
        self.setup_actions()

        # Setup DBus
        self.setup_dbus()

        # Setup Window
        self.setup_window()

        # Setup CSS
        self.setup_css()

        # Setup Headerbar
        self.setup_headerbar()

        # Setup UI
        self.setup_ui()

        # Setup Dialogs
        self.setup_dialogs()

    # === Setups ===
    def setup_actions(self):
        pass

    def setup_dbus(self):
        pass

    def setup_variables(self):
        self.current_profile = ""
        self.profile_manager = ProfileManager.get_default()

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{DATA_DIR}/style.css")

        style = self.get_style_context()
        style.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def setup_window(self):
        self.set_default_size(500, 580)
        self.set_content(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))
        self.content = self.get_content()

        self.connect("close-request", lambda x: self.get_application().quit())

    def setup_headerbar(self):
        title = Adw.WindowTitle(title="Pardus Parental Control")
        headerbar = Adw.HeaderBar(title_widget=title, css_classes=["flat"])
        self.content.append(headerbar)

    def setup_main_page(self):
        # Main Page
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            vexpand=True,
            spacing=7,
            margin_top=7,
            margin_start=7,
            margin_end=7,
        )

        # Profile and Preferences buttons
        box_top = Gtk.CenterBox()

        # Profile Button
        btn_profiles = Gtk.Button(
            halign="center",
            hexpand=False,
            valign="center",
            vexpand=True,
            css_classes=["success", "flat"],
        )
        btn_profiles_box = Gtk.Box(spacing=7)
        btn_profiles_box.append(Gtk.Image(icon_name="system-users-symbolic"))
        btn_profiles_box.append(Gtk.Separator(orientation="vertical"))
        self.lbl_profile_btn = Gtk.Label(
            label=self.profile_manager.get_current_profile_name()
        )
        btn_profiles_box.append(self.lbl_profile_btn)
        btn_profiles.set_child(btn_profiles_box)
        btn_profiles.connect("clicked", self.on_btn_profiles_clicked)

        # Preferences Button
        btn_show_preferences = Gtk.Button(
            icon_name="open-menu-symbolic",
            halign="end",
            valign="start",
            css_classes=["flat"],
        )

        btn_show_preferences.connect("clicked", self.on_btn_show_preferences_clicked)
        box_top.set_end_widget(btn_show_preferences)
        box_top.set_start_widget(btn_profiles)

        box.append(box_top)

        # Logo
        box.append(
            Gtk.Image(
                file=f"{DATA_DIR}/img/pardus-parental-control.svg",
                pixel_size=256,
                css_classes=["floating"],
            )
        )
        box.append(Gtk.Label(label="Pardus Parental Control", css_classes=["title-2"]))

        # Switch
        # switch = Gtk.Switch(
        #     halign="center", margin_top=14, margin_bottom=14, css_classes=["bigswitch"]
        # )
        # switch.connect("state-set", self.on_switch_activation_state_changed)
        btn_switch = Gtk.ToggleButton(
            icon_name="system-shutdown-symbolic",
            halign="center",
            css_classes=["bigswitch"],
        )
        btn_switch.connect("toggled", self.on_btn_switch_toggled)
        box.append(btn_switch)

        # Switch Status
        self.lbl_status = Gtk.Label(
            label="Parental Protection is Disabled", css_classes=["title-5"]
        )
        box.append(self.lbl_status)

        self.content.append(box)

    def setup_dialogs(self):
        self.dialog_preferences = PreferencesWindow(self.profile_manager, self)
        self.dialog_profiles = ProfileChooserDialog(
            self.profile_manager, self, self.on_profile_selected
        )

    def setup_ui(self):
        self.setup_main_page()

        # Copyright
        self.content.append(
            Gtk.Label(
                label="TÜBİTAK ULAKBİM | 2024",
                valign="end",
                margin_bottom=7,
                css_classes=["dim-label"],
            )
        )

    # === CALLBACKS ===
    # == Main Window
    def on_btn_profiles_clicked(self, btn):
        self.dialog_profiles.present()

    def on_destroy(self, b):
        self.window.get_application().quit()

    def on_btn_switch_toggled(self, button):
        state = button.get_active()

        self.lbl_status.set_label(
            "Parental Protection Active" if state else "Parental Protection Disabled"
        )
        self.lbl_status.set_css_classes(
            ["title-5", "success"] if state else ["title-5"]
        )

        subprocess.run(
            [
                "pkexec",
                os.path.dirname(os.path.abspath(__file__)) + "/../Activator.py",
                "1" if state else "0",
            ]
        )

    def on_btn_show_preferences_clicked(self, btn):
        self.dialog_preferences.present()

    def on_profile_selected(self, profile_name):
        self.current_profile = profile_name
        self.lbl_profile_btn.set_label(profile_name)

        self.dialog_preferences.fill_lists_from_profile(
            self.profile_manager.get_current_profile()
        )
