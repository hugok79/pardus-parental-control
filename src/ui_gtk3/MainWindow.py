# from ui.PreferencesWindow import PreferencesWindow
from ui_gtk3.ProfileChooserDialog import ProfileChooserDialog
import managers.ProfileManager as ProfileManager

import os
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk  # noqa

CWD = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{CWD}/../../data"


class MainWindow(Gtk.ApplicationWindow):
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

    def show_ui(self):
        self.show_all()

    # === Setups ===
    def setup_actions(self):
        pass

    def setup_dbus(self):
        pass

    def setup_variables(self):
        self.current_profile = ""
        self.profile_manager = ProfileManager.get_default()
        self.service_activated = False

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{DATA_DIR}/style_gtk3.css")

        style = self.get_style_context()
        style.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def setup_window(self):
        self.set_default_size(500, 580)

        self.connect("destroy", lambda x: self.get_application().quit())

    def setup_headerbar(self):
        self.set_title("Pardus Parental Control")

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
        box_top = Gtk.Box()
        box_top.set_valign(Gtk.Align.START)
        box_top.set_vexpand(False)

        # Profile Button
        btn_profiles = Gtk.Button(
            halign="center", hexpand=False, valign="center", vexpand=True
        )
        btn_profiles_box = Gtk.Box(spacing=7)
        btn_profiles_box.add(Gtk.Image(icon_name="system-users-symbolic"))
        btn_profiles_box.add(Gtk.Separator(orientation="vertical"))
        self.lbl_profile_btn = Gtk.Label(
            label=self.profile_manager.get_current_profile_name()
        )
        btn_profiles_box.add(self.lbl_profile_btn)
        btn_profiles.add(btn_profiles_box)
        btn_profiles.connect("clicked", self.on_btn_profiles_clicked)

        # Preferences Button
        btn_show_preferences = Gtk.Button.new_from_icon_name(
            "open-menu-symbolic", Gtk.IconSize.BUTTON
        )
        btn_show_preferences.set_halign(Gtk.Align.END)
        btn_show_preferences.set_valign(Gtk.Align.START)
        btn_show_preferences.set_hexpand(True)

        btn_show_preferences.connect("clicked", self.on_btn_show_preferences_clicked)
        box_top.add(btn_profiles)
        box_top.add(btn_show_preferences)

        box.add(box_top)

        # Logo
        img_logo = Gtk.Image.new_from_file(
            f"{DATA_DIR}/img/pardus-parental-control.svg"
        )
        img_logo.set_name("logo")  # css #logo id
        box.add(img_logo)

        # Logo Title
        box.add(Gtk.Label(label="Pardus Parental Control", name="logotitle"))

        # Service Activate Button
        self.btn_service_activate = Gtk.Button(
            halign="center", margin_top=7, margin_bottom=7, name="btn_service_deactive"
        )
        self.btn_service_activate.add(
            Gtk.Image(
                icon_name="system-shutdown-symbolic",
                pixel_size=32,
                margin_top=7,
                margin_bottom=7,
                margin_start=7,
                margin_end=7,
            )
        )
        self.btn_service_activate.connect(
            "clicked", self.on_btn_service_activate_clicked
        )
        box.add(self.btn_service_activate)

        # Switch Status
        self.lbl_status = Gtk.Label(
            label="Status: Inactive",
        )
        box.add(self.lbl_status)

        # Copyright
        box.add(
            Gtk.Label(
                label="TÜBİTAK ULAKBİM | 2024",
                valign="end",
                vexpand=True,
                margin_bottom=7,
            )
        )

        self.add(box)

    def setup_dialogs(self):
        # self.dialog_preferences = PreferencesWindow(self.profile_manager, self)
        self.dialog_profiles = ProfileChooserDialog(
            self.profile_manager, self, self.on_profile_selected
        )

    def setup_ui(self):
        self.setup_main_page()

    # === FUNCTIONS ===
    def start_service(self):
        if self.service_activated:
            return

        process = subprocess.run(
            [
                "pkexec",
                os.path.dirname(os.path.abspath(__file__)) + "/../Activator.py",
                "1",
            ]
        )

        if process.returncode == 0:
            self.service_activated = True
            self.lbl_status.set_label("Status: Active")

        self.set_widget_styles()

    def stop_service(self):
        if not self.service_activated:
            return

        process = subprocess.run(
            [
                "pkexec",
                os.path.dirname(os.path.abspath(__file__)) + "/../Activator.py",
                "0",
            ]
        )

        if process.returncode == 0:
            self.service_activated = False
            self.lbl_status.set_label("Status: Inactive")

        self.set_widget_styles()

    def set_widget_styles(self):
        self.btn_service_activate.set_name(
            "btn_service_active" if self.service_activated else "btn_service_deactive"
        )
        self.lbl_status.set_name("service_active" if self.service_activated else "")

    # === CALLBACKS ===
    # == Main Window
    def on_btn_profiles_clicked(self, btn):
        self.dialog_profiles.show_all()

    def on_destroy(self, b):
        self.window.get_application().quit()

    def on_btn_service_activate_clicked(self, button):
        if self.service_activated:
            self.stop_service()
        else:
            self.start_service()

    def on_btn_show_preferences_clicked(self, btn):
        self.dialog_preferences.present()

    def on_profile_selected(self, profile_name):
        self.current_profile = profile_name
        self.lbl_profile_btn.set_label(profile_name)

        # self.dialog_preferences.fill_lists_from_profile(
        #     self.profile_manager.get_current_profile()
        # )
