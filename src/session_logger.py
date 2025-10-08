#!/usr/bin/python3
import os
import sys
import time

import managers.SessionTimeManager as SessionTimeManager


def save_login_timestamp(user):
    # Create logs directory if not exist
    os.makedirs(SessionTimeManager.USER_SESSIONS_LOGS_PATH, exist_ok=True)

    # User's log file
    user_session = f"{SessionTimeManager.USER_SESSIONS_LOGS_PATH}/{user}.log"

    # Create if not exists
    if not os.path.exists(user_session):
        create_file(user_session)

    # Calculate login time
    now_isoformat = SessionTimeManager.now().isoformat(timespec="seconds")
    msg = f"{now_isoformat}|0000"

    # Add new login log to the beginning of the file
    with open(user_session, "r+") as f:
        content = f.read()

        f.seek(0, 0)
        f.write(msg + "\n" + content)


def create_file(file):
    with open(file, "w") as f:
        pass


def set_minutes_of_last_session(user, new_minute):
    user_session = f"{SessionTimeManager.USER_SESSIONS_LOGS_PATH}/{user}.log"

    # Create if not exists
    if not os.path.exists(user_session):
        create_file(user_session)

    # Add new login log to the beginning of the file
    with open(user_session, "r+") as f:
        # Read first line
        f.seek(0)
        first_line = f.readline().split("|")
        first_line[1] = f"{new_minute:04d}"

        first_line = "|".join(first_line)

        # Update the first line
        f.seek(0)
        f.write(first_line)


# Get args
user = sys.argv[1]

# add login to log at startup
save_login_timestamp(user)

# Add 1 on every minute user logged in.
elapsed_minutes = 0
while True:
    time.sleep(60)

    elapsed_minutes += 1

    set_minutes_of_last_session(user, elapsed_minutes)
