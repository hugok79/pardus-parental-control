from gi.repository import Gio, GLib  # noqa
import os


def _on_running_applications_changed_signal(connection, sender, object, interface, signal, parameters, on_applications_changed):
    print("SIGNAL GELDI:")
    print(connection)
    print(sender, interface)
    print(object)
    print(signal, parameters)

    running_app_list = connection.call_sync(
        bus_name="org.gnome.Shell.Introspect",
        object_path="/org/gnome/Shell/Introspect",
        interface_name="org.gnome.Shell.Introspect",
        method_name="GetRunningApplications",
        parameters=None,
        reply_type=None,
        flags=Gio.DBusCallFlags.NONE,
        timeout_msec=-1,
        cancellable=None
    )
    print(running_app_list)


"""
def _on_dbus_connected(object, result, on_applications_changed):
    connection = Gio.bus_get_finish(result)
    if connection is None:
        print("DBus connection error!")
        return

    connection.set_exit_on_close(True)

    connection.signal_subscribe(
        sender="org.gnome.Shell.Introspect",
        interface_name="org.gnome.Shell.Introspect",
        member="RunningApplicationsChanged",
        object_path="/org/gnome/Shell/Introspect",
        arg0=None,
        flags=Gio.DBusSignalFlags.NONE,
        callback=_on_running_applications_changed_signal,
        user_data=on_applications_changed
    )
"""


def listen_applications_changed(on_applications_changed):

    # set the dbus address
    # os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{uid}/bus"

    # session_bus = dbus.SessionBus(mainloop=GLib.MainLoop.ref())
    # obj = session_bus.get_object(
    #     'org.gnome.Shell.Introspect', '/org/gnome/Shell/Introspect')
    # obj.connect_to_signal('RunningApplicationsChanged',
    #                       _on_running_applications_changed_signal)

    # didn't use Gio.bus_get because we are root.
    # Gio.DBusConnection.new_for_address(
    #    address=f"unix:path=/run/user/{uid}/bus",
    #    flags=Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
    #    callback=_on_dbus_connected,
    #    user_data=on_applications_changed
    # )

    try:
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        # connection = Gio.DBusConnection.new_for_address_sync(
        #     address=f"unix:path=/run/user/{uid}/bus",
        #     flags=Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION
        # )
        if connection is None:
            print("DBus connection error!")
            return

        connection.set_exit_on_close(True)

        running_app_list = connection.call_sync(
            bus_name="org.gnome.Shell.Introspect",
            object_path="/org/gnome/Shell/Introspect",
            interface_name="org.gnome.Shell.Introspect",
            method_name="GetRunningApplications",
            parameters=None,
            reply_type=None,
            flags=Gio.DBusCallFlags.NONE,
            timeout_msec=-1,
            cancellable=None
        )
        print(running_app_list)

        connection.signal_subscribe(
            sender="org.gnome.Shell.Introspect",
            interface_name="org.gnome.Shell.Introspect",
            member="RunningApplicationsChanged",
            object_path="/org/gnome/Shell/Introspect",
            arg0=None,
            flags=Gio.DBusSignalFlags.NONE,
            callback=_on_running_applications_changed_signal,
            user_data=on_applications_changed
        )

    except GLib.Error as e:
        print("GLib.Error: ", e)
