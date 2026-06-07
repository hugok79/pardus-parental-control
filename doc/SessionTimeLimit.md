# How does Session Time Limit work?

The parent defines, per weekday, a permitted time range (start–end) and an
optional daily usage limit in minutes.

## `PPCDaemon.py` (root, system service)

- Tracks logind sessions (`Class == "user"` only; greeter/manager sessions
  are ignored) on the system bus.
- Writes the usage minutes of restricted users to
  `/var/log/user-sessions/{username}.log` once per minute.
- Checks whether the session time is over:
  - **immediately** when a restricted user logs in,
  - **immediately** when the preferences change,
  - and once per minute.
- When the time is over:
  1. Emits the `SessionTimeExpired(uid, username, seconds_left)` signal on
     the system bus (`tr.org.pardus.ParentalControl`).
  2. 11 seconds later terminates the user via logind `TerminateUser`.

## `PPCAgent.py` (user, user service)

Listens for the `SessionTimeExpired` signal and shows the 10 second
countdown popup (`NotificationApp.py`).

The agent is unprivileged on purpose: it dies instantly on logout (it can
not block it), and killing it only hides the popup — the root daemon still
terminates the session.
