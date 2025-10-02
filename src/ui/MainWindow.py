import managers.PreferencesManager as PreferencesManager
import managers.LinuxUserManager as LinuxUserManager

# Widgets
from ui.widget.ListRowAvatar import ListRowAvatar

# Pages
from ui.page.PageApplications import PageApplications
from ui.page.PageWebsites import PageWebsites
from ui.page.PageSessionTime import PageSessionTime
from ui.page.PageEmpty import PageEmpty

import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("AccountsService", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gio, GObject, Adw, AccountsService  # noqa


CWD = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = f"{CWD}/../../assets"

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

        # Setup UI
        self.setup_ui()

    def show_ui(self):
        self.present()

    # === Setups ===
    def setup_about(self):
        self.about_dialog = Adw.AboutWindow(
            application_name=_("Pardus Parental Control"),
            application_icon="pardus-parental-control",
            version="0.4.1",
            website="https://github.com/pardus/pardus-parental-control",
            copyright="© TÜBİTAK BİLGEM",
            comments=_(
                "Restrict user access to internet and applications. Manage session times."
            ),
            developer_name=_("Pardus Developers"),
            developers=["Emin Fedar"],
            license_type=Gtk.License.GPL_3_0,
            translator_credits=_("translator_credits"),
            hide_on_close=True,
            modal=True,
            transient_for=self,
        )

    def setup_variables(self):
        self.preferences_manager = PreferencesManager.get_default()
        self.selected_user = None

        # Setup AccountsService UserManager for monitoring user changes
        self.user_manager = AccountsService.UserManager.get_default()
        self.user_manager.connect("user-added", self.refresh_users_listbox)
        self.user_manager.connect("user-removed", self.on_user_removed)
        self.user_manager.connect("user-changed", self.refresh_users_listbox)

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{ASSETS_DIR}/style.css")

        style = self.get_style_context()
        style.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def setup_window(self):
        self.set_default_size(1000, 600)
        self.set_icon_name("pardus-parental-control")
        self.set_title(_("Pardus Parental Control"))
        self.connect("close-request", lambda x: self.get_application().quit())

    def setup_sidebar(self):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, vexpand=True, css_classes=["view"]
        )

        side_headerbar = Adw.HeaderBar(
            title_widget=Gtk.Label(label=_("Users")),
            decoration_layout="",
            css_classes=["flat"],
        )
        btn_about_dialog = Gtk.Button.new_from_icon_name("help-about-symbolic")
        btn_about_dialog.connect("clicked", self.on_btn_about_dialog_clicked)
        side_headerbar.pack_start(btn_about_dialog)
        box.append(side_headerbar)

        # Scrolled Sidebar Window
        self.users_listbox = Gtk.ListBox(css_classes=["user-sidebar"])
        self.users_listbox.connect("row-selected", self.on_sidebar_row_selected)
        self.users_listbox.connect("row-activated", self.on_sidebar_row_activated)

        self.refresh_users_listbox(None, None)  # Initial load
        scrolledwindow = Gtk.ScrolledWindow(
            child=self.users_listbox,
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vexpand=True,
            width_request=220,
        )
        box.append(Gtk.Separator(margin_start=7, margin_end=7))
        box.append(scrolledwindow)

        # New User
        box_new_user = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=7,
        )
        box_new_user.append(Gtk.Image.new_from_icon_name("list-add-symbolic"))
        box_new_user.append(Gtk.Label(label=_("New User")))
        btn_new_user = Gtk.Button(
            child=box_new_user,
            css_classes=["sidebar-button"],
        )
        btn_new_user.connect("clicked", self.on_btn_new_user_clicked)
        box.append(Gtk.Separator(margin_start=7, margin_end=7))
        box.append(btn_new_user)

        return box

    def refresh_users_listbox(self, user_manager, user):
        # Remove all existing rows in the listbox
        while self.users_listbox.get_first_child():
            self.users_listbox.remove(self.users_listbox.get_first_child())

        users = LinuxUserManager.get_standard_users()
        for u in users:
            username = u.get_user_name()
            fullname = u.get_real_name() if u.get_real_name() else username

            self.users_listbox.append(ListRowAvatar(fullname, username))

        # Select first user on startup
        first_row = self.users_listbox.get_row_at_index(0)
        if first_row:
            self.users_listbox.select_row(first_row)

    def on_user_removed(self, user_manager, user):
        # Handle user removal by removing from preferences and refreshing UI
        if user is not None:
            username = user.get_user_name()
            if self.preferences_manager.has_user(username):
                self.preferences_manager.remove_user(username)

        # Refresh the UI
        self.refresh_users_listbox(user_manager, user)

    def setup_main(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Headerbar
        self.view_stack = Adw.ViewStack(hexpand=True, vexpand=True)
        self.view_switcher = Adw.ViewSwitcher(
            stack=self.view_stack, policy="wide", visible=False
        )

        # Avatar on headerbar
        # self.selected_avatar = ListRowAvatar(None, None)
        # self.selected_avatar.set_visible(False)

        headerbar = Adw.HeaderBar(title_widget=self.view_switcher, css_classes=["flat"])

        box_headerbar = Gtk.Box()
        box_headerbar.append(self.btn_open_sidebar)
        # box_headerbar.append(self.selected_avatar)

        headerbar.pack_start(box_headerbar)
        box.append(headerbar)

        # Stack for different settings

        # Stack Pages:
        # 0) Empty (Select User)
        self.page_empty = PageEmpty()
        self.view_stack.add_named(self.page_empty, "empty")

        # 1) Applications
        self.page_applications = PageApplications(self, self.preferences_manager)
        self.view_stack.add_titled_with_icon(
            self.page_applications,
            "applications",
            _("Applications"),
            "application-x-executable-symbolic",
        )

        # 2) Websites
        self.page_websites = PageWebsites(self.preferences_manager)
        self.view_stack.add_titled_with_icon(
            self.page_websites, "websites", _("Websites"), "web-browser-symbolic"
        )

        # 3) Session Time
        self.page_session_time = PageSessionTime(self.preferences_manager)
        self.view_stack.add_titled_with_icon(
            self.page_session_time,
            "session_time",
            _("Session Time"),
            "document-open-recent-symbolic",
        )

        box.append(self.view_stack)
        return box

    def setup_ui(self):
        self.leaflet = Adw.Leaflet.new()

        # Open Sidebar Button
        self.btn_open_sidebar = Gtk.Button.new_from_icon_name("open-menu-symbolic")
        self.btn_open_sidebar.connect("clicked", self.on_btn_open_sidebar_clicked)
        self.leaflet.bind_property(
            "folded", self.btn_open_sidebar, "visible", GObject.BindingFlags.SYNC_CREATE
        )

        # Contents
        main_content = self.setup_main()
        sidebar = self.setup_sidebar()
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        # Add to leaflet
        self.leaflet.append(sidebar)
        self.leaflet.append(separator).set_navigatable(False)
        self.leaflet.append(main_content)

        self.set_content(self.leaflet)

    # === FUNCTIONS ===

    # === CALLBACKS ===
    def on_sidebar_row_selected(self, listbox, row):
        if self.selected_user is None:
            self.view_stack.set_visible_child_name("applications")
            self.view_switcher.set_visible(True)

        # If no row is selected or the row is None, do nothing
        if row is None or not isinstance(row, Gtk.ListBoxRow):
            return
        selected_username = row.get_child().get_username()

        if self.selected_user != selected_username:
            # new username selected
            self.selected_user = selected_username
            # selected_fullname = row.get_child().get_fullname()

            # Change headerbar avatar
            # self.selected_avatar.set_user(selected_fullname, selected_username)
            # self.selected_avatar.set_visible(True)

            if not self.preferences_manager.has_user(selected_username):
                self.preferences_manager.insert_new_user(selected_username)

            self.page_applications.set_username(selected_username)
            self.page_websites.set_username(selected_username)
            self.page_session_time.set_username(selected_username)

        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)

    def on_sidebar_row_activated(self, _listbox, _row):
        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)

    def on_btn_open_sidebar_clicked(self, _btn):
        self.leaflet.navigate(Adw.NavigationDirection.BACK)

    def on_destroy(self, b):
        self.get_application().quit()

    def on_btn_about_dialog_clicked(self, _btn):
        self.about_dialog.present()

    def on_btn_new_user_clicked(self, _btn):
        current_de = os.environ.get("XDG_CURRENT_DESKTOP")

        if current_de == "GNOME":
            GLib.spawn_async(
                argv=["gnome-control-center", "user-accounts"],
                flags=GLib.SpawnFlags.SEARCH_PATH,
            )
        elif current_de == "XFCE":
            GLib.spawn_async(
                argv=["users-admin"],
                flags=GLib.SpawnFlags.SEARCH_PATH,
            )
