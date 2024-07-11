import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa


class InputDialog(Adw.Window):
    def __init__(self, parent_window, title, subtitle, entry_callback):
        super().__init__(transient_for=parent_window)

        self.setup_window()

        self.setup_ui(title, subtitle)

        self.entry_callback = entry_callback

    # UI
    def setup_window(self):
        self.set_default_size(300, 100)
        self.set_hide_on_close(True)

    def setup_ui(self, title, subtitle):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=7,
            margin_top=11,
            margin_bottom=11,
            margin_start=11,
            margin_end=11,
        )

        lbl_title = Gtk.Label(label=title, css_classes=["title-3"])
        box.append(lbl_title)

        if subtitle:
            lbl_subtitle = Gtk.Label(label=subtitle)
            box.append(lbl_subtitle)

        entry_input = Gtk.Entry(
            placeholder_text=_("example.com"), activates_default=True
        )
        entry_input.connect("activate", self.on_entry_input_activated)

        box.append(entry_input)

        self.set_content(box)

        entry_input.grab_focus_without_selecting()

    # == CALLBACKS ==
    def on_entry_input_activated(self, entry):
        self.entry_callback(entry.get_text())
        entry.set_text("")

        self.hide()
