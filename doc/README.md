# Architecture Overview

Pardus Parental Control restricts **applications**, **websites** and
**session time** for non-privileged (child) users. Users in the `sudo`
group are parents; only they can change the settings.

## Components

| Component | Runs as | Purpose |
|---|---|---|
| GUI (`src/Main.py`) | parent | Edits `/var/lib/pardus/pardus-parental-control/preferences.json` |
| `src/PPCDaemon.py` | root, **system** service (`ppc-daemon.service`) | Enforces all restrictions. Watches logind over the system bus |
| `src/PPCAgent.py` | user, **user** service (`ppc-agent.service`) | Shows the "session time is over" popup when the daemon signals it |
| `src/NotificationApp.py` | user | The 10 second countdown popup itself |

## Flow

1. The parent configures restrictions per user in the GUI; they are saved to
   `preferences.json`. A user listed in that file is "restricted".
2. `PPCDaemon` watches logind: on every login/logout/user-switch it applies
   the filters of the active restricted user (or clears them), and checks
   the session time limits (see the other documents for details).
3. The daemon runs as root **outside** of user sessions, so a child can
   neither kill it nor delay logout because of it. The only in-session piece
   is the unprivileged `PPCAgent`, which merely shows the warning popup.

## Documents

- [ApplicationFiltering.md](ApplicationFiltering.md)
- [WebsiteFiltering.md](WebsiteFiltering.md)
- [SessionTimeLimit.md](SessionTimeLimit.md)
