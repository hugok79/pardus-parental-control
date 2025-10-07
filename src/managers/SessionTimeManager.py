import subprocess
from datetime import datetime


def now():
    return datetime.now()


def now_minutes():
    _now = now()
    return _now.hour * 60 + _now.minute


def get_all_user_sessions(username):
    p = subprocess.run(
        ["last", "-R", "--time-format", "iso"], capture_output=True, text=True
    )

    if p.returncode != 0:
        return None

    sessions = []
    for line in p.stdout.splitlines():
        if username in line:
            fields = line.split(" ")

            # Remove empty fields
            fields = list(filter(lambda e: e, fields))
            # Raw Fields:
            # username, tty, start-time, status, endtime (or 'down'), elapsed time '(00:13)' = 13 mins
            # Example still logged in:
            # ['ef', ':1', '2025-10-06T12:34:18+03:00', 'still', 'logged', 'in']
            # Example older sessions:
            # ['ef', ':1', '2025-10-06T11:12:13+03:00', '-',     '2025-10-06T11:42:43+03:00', '(00:30)']
            # ['ef', ':1', '2025-10-03T16:34:56+03:00', '-',     'down', '(00:13)']

            # Map fields:
            # From:
            # ['ef', ':1', '2025-10-03T16:34:56+03:00', '-',     'down', '(00:13)']
            # To:
            # ['2025-10-03T16:34:56+03:00', 13]
            # [start, elapsed time]

            now = datetime.now()
            start_time = datetime.fromisoformat(fields[2]).replace(tzinfo=None)
            elapsed_mins = 0

            # Convert elapsed time to raw minutes
            if fields[5] == "in":
                # Current session, calculate difference between now and start time
                elapsed_mins = int((now - start_time).total_seconds() / 60)
            else:
                # Old Sessions
                hours = int(fields[5][1:3]) * 60
                mins = int(fields[5][4:6])

                elapsed_mins = hours + mins

            fields = [start_time, elapsed_mins]

            sessions.append(fields)

    return sessions


def get_today_session_usage_of_user(username):
    user_sessions = get_all_user_sessions(username)

    _now = now()

    elapsed_mins = 0
    for s in user_sessions:
        if s[0].day == _now.day and s[0].month == _now.month and s[0].year == _now.year:
            elapsed_mins += s[1]

    return elapsed_mins


def get_weekly_session_usage_of_user(username):
    user_sessions = get_all_user_sessions(username)

    _now = now()

    today_weekday = _now.weekday()  # Monday = 0, ...,  Sunday = 6

    elapsed_mins = 0
    for s in user_sessions:
        time_diff = _now - s[0]
        if time_diff.days <= today_weekday and time_diff.days <= 6:
            print("This session added to elapsed mins:", s[0], s[1])
            elapsed_mins += s[1]

    return elapsed_mins
