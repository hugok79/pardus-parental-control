#!/bin/bash

sleep 1

USER_ID=$(id -u)

/usr/bin/pkexec /usr/share/pardus/pardus-parental-control/src/session_logger.py $USER &
/usr/bin/pkexec /usr/share/pardus/pardus-parental-control/src/PPCActivator.py $USER_ID $USER &

sleep 2

exit 0


