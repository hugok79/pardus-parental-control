#!/bin/bash

USER_ID=$(id -u)

if [[ "$USER" != "Debian-gdm" ]]; then

    /usr/bin/pkexec /usr/share/pardus/pardus-parental-control/src/PPCActivator.py "$USER_ID" "$USER"

    # 188 is the exit code of PPCActivator.py when session time is over.
    if [[ $? == 188 ]]; then
        /usr/share/pardus/pardus-parental-control/src/NotificationApp.py "$USER" &
    fi

fi

exit 0
