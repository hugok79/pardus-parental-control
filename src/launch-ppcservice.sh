#!/bin/bash

USER_ID=$(id -u)

if [[ "$USER" != "Debian-gdm" ]]; then

    /usr/bin/pkexec /usr/share/pardus/pardus-parental-control/src/session_logger.py "$USER" &

    /usr/bin/pkexec /usr/share/pardus/pardus-parental-control/src/PPCActivator.py "$USER_ID" "$USER"

fi

exit 0
