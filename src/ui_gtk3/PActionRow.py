import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa


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
    row = Gtk.ListBoxRow(activatable=True if on_activated else False, selectable=False)
    box = Gtk.Box()
    box.get_style_context().add_class("linked")

    if on_edited:
        entry = Gtk.Entry(hexpand=True)
        entry.set_input_purpose(Gtk.InputPurpose.ALPHA)
        entry.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
        entry.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, "document-edit-symbolic"
        )
        entry.connect("activate", on_edited)
        entry.set_text(title)
        entry.title = title

        box.add(entry)
    else:
        label = Gtk.Label(label=title, use_markup=False)

        box.add(label)
        # listboxrow.set_selectable(True)

    # if subtitle:
    #     action_row.set_subtitle(subtitle)

    if icon_name:
        box.add(Gtk.Image(icon_name=icon_name, pixel_size=32))
    elif gicon:
        box.add(Gtk.Image(gicon=gicon, pixel_size=32))

    if on_activated:
        row.connect("activated", on_activated, user_data)

    # if activatable_widget:
    #     listboxrow.add_prefix(activatable_widget)
    #     listboxrow.set_activatable_widget(activatable_widget)

    if on_deleted:
        btn_delete = Gtk.Button()
        btn_delete.add(Gtk.Image(icon_name="user-trash-symbolic"))
        btn_delete.get_style_context().add_class("destructive-action")
        btn_delete.connect("clicked", on_deleted, row, user_data)

        box.add(btn_delete)

        row.hide_delete_button = lambda: btn_delete.hide()
        row.show_delete_button = lambda: btn_delete.show()

    row.add(box)

    return row
