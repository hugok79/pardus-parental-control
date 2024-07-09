from ui_gtk4.PreferencesWindow import PreferencesWindow
from ui_gtk4.ProfileChooserDialog import ProfileChooserDialog
import managers.ProfileManager as ProfileManager

import os
import subprocess
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw  # noqa

CWD = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{CWD}/../../data"

import locale  # noqa
from locale import gettext as _  # noqa

# Translation Constants:
APPNAME = "pardus-parental-control"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        # Setup Variables
        self.setup_variables()

        # Setup About Window
        self.setup_about()

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
        self.present()

    # === Setups ===
    def setup_about(self):
        self.about_dialog = Adw.AboutWindow(
            application_name=_("Pardus Parental Control"),
            version="0.5.0",
            website="https://pardus.org.tr",
            copyright="© 2024 Pardus",
            comments=_(
                "Restrict user access to internet and applications. Manage session times."
            ),
            application_icon="pardus-parental-control",
            developer_name="Pardus Developers <gelistirici@pardus.org.tr>",
            license_type=Gtk.License.GPL_3_0,
            translator_credits=_("translator_credits"),
            hide_on_close=True,
            modal=True,
            transient_for=self,
        )

    def setup_variables(self):
        self.current_profile = ""
        self.profile_manager = ProfileManager.get_default()
        self.service_activated = False

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{DATA_DIR}/style_gtk4.css")

        style = self.get_style_context()
        style.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def setup_window(self):
        self.set_default_size(400, 600)
        self.set_content(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))
        self.set_resizable(False)
        self.content = self.get_content()

        self.connect("close-request", lambda x: self.get_application().quit())

    def setup_headerbar(self):
        title = Adw.WindowTitle(title=_("Pardus Parental Control"))
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

        # About Dialog
        btn_about_dialog = Gtk.Button(halign="start", icon_name="help-about-symbolic")
        btn_about_dialog.connect("clicked", self.on_btn_about_dialog_clicked)

        # Profile Button
        btn_profiles = Gtk.Button(
            halign="center",
            hexpand=False,
            valign="center",
            vexpand=True,
            css_classes=["success"],
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
        )

        btn_show_preferences.connect("clicked", self.on_btn_show_preferences_clicked)
        box_top.set_start_widget(btn_about_dialog)
        box_top.set_center_widget(btn_profiles)
        box_top.set_end_widget(btn_show_preferences)

        box.append(box_top)

        # Logo
        self.img_logo = Gtk.Image(
            file=f"{DATA_DIR}/img/pardus-parental-control.svg",
            pixel_size=256,
        )
        box.append(self.img_logo)
        box.append(
            Gtk.Label(label=_("Pardus Parental Control"), css_classes=["title-2"])
        )

        # Service Activate Button
        self.btn_service_activate = Gtk.Button(
            halign="center", css_classes=["circular"], margin_top=7, margin_bottom=7
        )
        self.btn_service_activate.set_child(
            Gtk.Image(
                icon_name="system-shutdown-symbolic",
                pixel_size=32,
                margin_top=14,
                margin_bottom=14,
                margin_start=14,
                margin_end=14,
            )
        )
        self.btn_service_activate.connect(
            "clicked", self.on_btn_service_activate_clicked
        )
        box.append(self.btn_service_activate)

        # Switch Status
        self.lbl_status = Gtk.Label(
            label=_("Status: Inactive"), css_classes=["title-5"]
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

    # === FUNCTIONS ===
    def start_service(self):
        if self.service_activated:
            return

        process = subprocess.run(
            [
                "pkexec",
                CWD + "/../PPCActivator.py",
                "1",
            ]
        )

        if process.returncode == 0:
            self.service_activated = True
            self.lbl_status.set_label(_("Status: Active"))

        self.set_widget_styles()

    def stop_service(self):
        if not self.service_activated:
            return

        process = subprocess.run(
            [
                "pkexec",
                CWD + "/../PPCActivator.py",
                "0",
            ]
        )

        if process.returncode == 0:
            self.service_activated = False
            self.lbl_status.set_label(_("Status: Inactive"))

        self.set_widget_styles()

    def set_widget_styles(self):
        self.btn_service_activate.set_css_classes(
            ["circular", "success"] if self.service_activated else ["circular"]
        )
        self.lbl_status.set_css_classes(
            ["title-5", "success"] if self.service_activated else ["title-5"]
        )

    # === CALLBACKS ===
    # == Main Window
    def on_btn_profiles_clicked(self, btn):
        self.dialog_profiles.present()

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

        self.dialog_preferences.fill_lists_from_profile(
            self.profile_manager.get_current_profile()
        )

    def on_btn_about_dialog_clicked(self, btn):
        self.about_dialog.present()
