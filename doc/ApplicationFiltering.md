# How does Application Filtering work?

The list works either as a **denylist** (block listed apps) or an
**allowlist** (block everything except listed apps).

When a restricted user's session becomes the active session, `PPCDaemon`:

1. Reads the user's application list from `preferences.json`.
2. For each blocked application, changes the group of its `.desktop` file
   and executable to `root:sudo` and removes the permissions of others
   (`.desktop`: 640, executable: 750). So only `sudo` group members can
   run them.
3. Blocks flatpak applications via **malcontent** (per-uid blocklist).

When the active session changes to a non-restricted user (or the greeter),
all permissions are restored to their defaults (644/755, `root:root`) and
the malcontent blocklist is cleared.
