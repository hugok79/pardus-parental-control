import os
import subprocess
import shutil

PRIVILEGED_GROUP = "sudo"
PRIVILEGED_GROUP_ID = int(
    subprocess.check_output(["getent", "group", PRIVILEGED_GROUP])
    .decode()
    .split(":")[2]
)


def check_user_privileged():
    if os.getuid() == 0:  # root user
        return True

    user_groups = os.getgroups()
    if PRIVILEGED_GROUP_ID in user_groups:  # not root but in the group
        return True

    return False


# Restrict
def restrict_bin_file(filepath):
    if filepath:
        os.chmod(filepath, 0o750)  # rwxr-x---
        os.chown(filepath, 0, PRIVILEGED_GROUP_ID)  # root:sudo


def restrict_desktop_file(filepath):
    if filepath:
        if "flatpak/" in filepath:
            # flatpak .desktop files are symlinks, so chmod doesn't work on them.
            if os.path.islink(filepath):
                restricted_name = "{}.RESTRICTED".format(filepath)
                os.rename(filepath, restricted_name)

                shutil.copyfile(restricted_name, filepath, follow_symlinks=True)

        os.chmod(filepath, 0o640)  # rw-r-----
        os.chown(filepath, 0, PRIVILEGED_GROUP_ID)


def restrict_conf_file(filepath):
    restrict_desktop_file(filepath)


# Unrestrict
def unrestrict_conf_file(filepath):
    unrestrict_desktop_file(filepath)  # same permission style


def unrestrict_desktop_file(filepath):
    if filepath:
        if "flatpak/" in filepath:
            # flatpak .desktop files are symlinks, so chmod doesn't work on them.
            if not os.path.islink(filepath):
                restricted_name = "{}.RESTRICTED".format(filepath)
                os.remove(filepath)
                os.rename(restricted_name, filepath)
        else:
            os.chmod(filepath, 0o644)  # rw-r--r--
            os.chown(filepath, 0, 0)  # root:root


def unrestrict_bin_file(filepath):
    if filepath:
        os.chmod(filepath, 0o755)  # rwxr-xr-x
        os.chown(filepath, 0, 0)  # root:root
