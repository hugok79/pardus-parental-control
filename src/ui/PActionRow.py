import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # noqa

import cgi


def new(
    title,
    subtitle="",
    icon_name="",
    gicon=None,
    on_activated=None,
    on_deleted=None,
    on_edited=None,
    user_data=None,
    activatable_widget=None,
):
    action_row = None
    if on_edited:
        action_row = Adw.EntryRow(
            title=title,
            text=title,
            show_apply_button=True,
            activates_default=True,
            use_markup=False,
        )
        action_row.set_input_purpose(Gtk.InputPurpose.ALPHA)
        action_row.connect("entry_activated", on_edited)
        action_row.connect("apply", on_edited)
    else:
        action_row = Adw.ActionRow(title=title, use_markup=False)

    if subtitle:
        action_row.set_subtitle(subtitle)

    if icon_name:
        action_row.add_prefix(Gtk.Image(icon_name=icon_name, pixel_size=32))
    elif gicon:
        action_row.add_prefix(Gtk.Image(gicon=gicon, pixel_size=32))

    if on_activated:
        action_row.set_activatable(True)
        action_row.connect("activated", on_activated, user_data)

    if activatable_widget:
        action_row.add_prefix(activatable_widget)
        action_row.set_activatable_widget(activatable_widget)

    if on_deleted:
        box_suffix = Gtk.Box(spacing=7, vexpand=False, valign="center")
        btn_delete = Gtk.Button(
            icon_name="user-trash-symbolic", css_classes=["flat", "error"]
        )
        btn_delete.connect("clicked", on_deleted, action_row, user_data)

        box_suffix.append(btn_delete)
        action_row.add_suffix(box_suffix)

        action_row.hide_delete_button = lambda: btn_delete.hide()
        action_row.show_delete_button = lambda: btn_delete.show()

    return action_row
