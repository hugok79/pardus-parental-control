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
