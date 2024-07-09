# How does Application Filtering work?

1. The .desktop file list in the `/var/lib/pardus/pardus-parental-control/profiles.json` file is read.
2. The .desktop file list in `/var/lib/pardus/pardus-parental-control/applied_profile.lock.json` file is read (to undo previously set constraints, if any).
3. Restore all permissions to original states.
3. The **group** of executable and .desktop files of the applications in the restricted list are transferred to the `sudo` user group.
4. Writing and execution permissions are disabled for those outside the group, containing authorized users.