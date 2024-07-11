#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import subprocess

APP_NAME = "pardus-parental-control"
APP_ID = "tr.org.pardus.parental-control"
TRANSLATIONS_FOLDER = "po"


def compile_translations():
    mo = []
    for po in os.listdir(TRANSLATIONS_FOLDER):
        if po.endswith(".po"):
            language = po.split(".po")[0]

            os.makedirs(f"{TRANSLATIONS_FOLDER}/{language}/LC_MESSAGES", exist_ok=True)

            mo_file = f"{TRANSLATIONS_FOLDER}/{language}/LC_MESSAGES/{APP_NAME}.mo"

            msgfmt_cmd = f'msgfmt "{TRANSLATIONS_FOLDER}/{po}" -o "{mo_file}"'
            subprocess.call(msgfmt_cmd, shell=True)

            mo.append((f"/usr/share/locale/{language}/LC_MESSAGES", [mo_file]))
    return mo


data_files = [
    # Source Code
    (
        f"/usr/share/pardus/{APP_NAME}/src",
        ["src/Main.py", "src/PPCActivator.py"],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/src/managers",
        [
            "src/managers/ApplicationManager.py",
            "src/managers/FileRestrictionManager.py",
            "src/managers/LinuxUserManager.py",
            "src/managers/NetworkFilterManager.py",
            "src/managers/ProfileManager.py",
        ],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/src/ui_gtk4",
        [
            "src/ui_gtk4/ApplicationChooserDialog.py",
            "src/ui_gtk4/InputDialog.py",
            "src/ui_gtk4/MainWindow.py",
            "src/ui_gtk4/PActionRow.py",
            "src/ui_gtk4/PreferencesWindow.py",
            "src/ui_gtk4/ProfileChooserDialog.py",
            "src/ui_gtk4/PTimePeriodChooser.py",
        ],
    ),
    # Binary
    ("/usr/bin/", [f"{APP_NAME}"]),
    # Data
    (
        f"/var/lib/pardus/{APP_NAME}/",
        [f"data/img/{APP_NAME}.svg"],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/data",
        [
            "data/profiles.json",
            "data/style_gtk4.css",
            "data/tr.org.pardus.parental-control.user-check.desktop",
        ],
    ),
    ("/usr/share/icons/hicolor/scalable/apps/", [f"data/img/{APP_NAME}.svg"]),
    # Desktop file
    ("/usr/share/applications/", [f"{APP_ID}.desktop"]),
    # Polkit
    (
        "/usr/share/polkit-1/actions",
        ["polkit/tr.org.pardus.pkexec.parental-control.policy"],
    ),
] + compile_translations()

setup(
    name=f"{APP_NAME}",
    version="0.3.0",
    packages=find_packages(),
    scripts=[f"{APP_NAME}"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Pardus Developers",
    author_email="gelistirici@pardus.org.tr",
    description="Parental Control and Restriction application for Pardus",
    license="GPLv3",
    keywords="",
    url="https://github.com/pardus/pardus-parental-control",
)
