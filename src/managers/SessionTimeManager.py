from datetime import datetime
import os

USER_SESSIONS_LOGS_PATH = "/var/log/user-sessions"


def now():
    return datetime.now()


def now_minutes():
    _now = now()
    return _now.hour * 60 + _now.minute


def get_all_user_sessions(username):
    # Example Data: [(datetime object), 12] ([start_time, elapsed_mins])
    sessions = []

    user_session = os.path.join(USER_SESSIONS_LOGS_PATH, f"{username}.log")

    if os.path.exists(user_session):
        with open(user_session, "r") as f:
            for line in f.readlines():
                if not line or len(line.split("|")) != 2:
                    continue

                # Example line: "2025-10-07T13:37:06.265743|0000"
                # date|minutes_elapsed
                (date, minutes_elapsed) = line.split("|")

                date = datetime.fromisoformat(date).replace(tzinfo=None)

                sessions.append([date, int(minutes_elapsed)])
    else:
        print(f"{user_session} doesn't exist!")

    return sessions


def get_today_session_usage_minutes(username):
    user_sessions = get_all_user_sessions(username)

    _now = now()

    elapsed_mins = 0
    for s in user_sessions:
        if s[0].day == _now.day and s[0].month == _now.month and s[0].year == _now.year:
            elapsed_mins += s[1]

    return elapsed_mins


def get_weekly_session_usage_minutes(username):
    user_sessions = get_all_user_sessions(username)

    _now = now()

    today_weekday = _now.weekday()  # Monday = 0, ...,  Sunday = 6

    elapsed_mins = 0
    for s in user_sessions:
        time_diff = _now - s[0]

        # Current week check
        if (
            time_diff.days <= today_weekday
            and time_diff.days <= 6
            and time_diff.days >= 0
        ):
            print("This session added to elapsed mins:", s[0], s[1])
            elapsed_mins += s[1]

    return elapsed_mins
