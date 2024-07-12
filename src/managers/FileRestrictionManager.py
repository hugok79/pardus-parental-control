import os
import subprocess

PRIVILEGED_GROUP = "floppy"
PRIVILEGED_GROUP_ID = int(
    subprocess.check_output(["getent", "group", PRIVILEGED_GROUP])
    .decode()
    .split(":")[2]
)


def check_user_privileged():
    user_groups = os.getgroups()
    if 0 in user_groups:  # root user
        return True

    if PRIVILEGED_GROUP_ID in user_groups:  # not root but in the group
        return True

    return False


# Restrict
def restrict_bin_file(filepath):
    if filepath:
        os.chmod(filepath, 0o750)  # rwxr-xr--
        os.chown(filepath, 0, PRIVILEGED_GROUP_ID)  # root:floppy


def restrict_desktop_file(filepath):
    if filepath:
        os.chmod(filepath, 0o640)  # rw-r-----
        os.chown(filepath, 0, PRIVILEGED_GROUP_ID)  # root:floppy


def restrict_conf_file(filepath):
    if filepath:
        os.chmod(filepath, 0o655)  # rw-r--r--
        os.chown(filepath, 0, PRIVILEGED_GROUP_ID)  # root:floppy


# Unrestrict
def unrestrict_conf_file(filepath):
    unrestrict_desktop_file(filepath)  # same permission style


def unrestrict_desktop_file(filepath):
    if filepath:
        os.chmod(filepath, 0o644)  # rw-r--r--
        os.chown(filepath, 0, 0)  # root:root


def unrestrict_bin_file(filepath):
    if filepath:
        os.chmod(filepath, 0o755)  # rwxr-xr-x
        os.chown(filepath, 0, 0)  # root:root
