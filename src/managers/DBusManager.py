from gi.repository import Gio, GLib  # noqa

# UNUSED RIGHT NOW


def _on_running_applications_changed_signal(
    connection, sender, object, interface, signal, parameters, on_applications_changed
):
    print("RunningApplicationsChanges signal is emitted")
    on_applications_changed()


def _message_filter_func(connection, message, incoming, user_data):
    if message.get_interface() == "org.gnome.Shell.Introspect":
        print(message.get_member())
        print(message.get_sender())
        print(message.get_destination())
        print(message.get_path())
        print(message.get_body())
        print(message.get_serial())
        print("---")
        if message.get_member() == "GetRunningApplications":
            print("RUNNING APPLICATIONS GET EDILDI:")
            print(message.get_body())

    return message


def listen_application_changes(on_applications_changed):
    try:
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        if connection is None:
            print("DBus connection error!")
            return

        connection.set_exit_on_close(True)

        # Message filter to listen messages and filtering them
        connection.add_filter(_message_filter_func, None)

        # Subscribe signal to watch application changes
        connection.signal_subscribe(
            sender="org.gnome.Shell.Introspect",
            interface_name="org.gnome.Shell.Introspect",
            member="RunningApplicationsChanged",
            object_path="/org/gnome/Shell/Introspect",
            arg0=None,
            flags=Gio.DBusSignalFlags.NONE,
            callback=_on_running_applications_changed_signal,
            user_data=on_applications_changed,
        )

    except GLib.Error as e:
        print("GLib.Error: ", e)
