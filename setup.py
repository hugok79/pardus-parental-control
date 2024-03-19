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

            msgfmt_cmd = f'msgfmt "{TRANSLATIONS_FOLDER}/{po}" -o "{TRANSLATIONS_FOLDER}/{mo_file}"'
            subprocess.call(msgfmt_cmd, shell=True)

            mo.append((f"/usr/share/locale/{language}/LC_MESSAGES", [mo_file]))
    return mo


data_files = [
    ("/usr/share/applications/", [f"{APP_ID}.desktop"]),
    (f"/usr/share/pardus/{APP_NAME}/", [f"{APP_NAME}.svg"]),
    (
        f"/usr/share/pardus/{APP_NAME}/src",
        [
            "src/Main.py",
        ],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/src/managers",
        [
            "src/managers/LinuxUserManager.py",
            "src/managers/NetworkFilterManager.py",
            "src/managers/ProfileManager.py",
        ],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/src/ui_gtk3",
        [
            "src/ui_gtk3/ApplicationChooserDialog.py",
            "src/ui_gtk3/InputDialog.py",
            "src/ui_gtk3/MainWindow.py",
            "src/ui_gtk3/PActionRow.py",
            "src/ui_gtk3/PreferencesWindow.py",
            "src/ui_gtk3/ProfileChooserDialog.py",
            "src/ui_gtk3/PTimePeriodChooser.py",
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
    ("/usr/bin/", [f"{APP_NAME}"]),
    ("/usr/share/icons/hicolor/scalable/apps/", [f"{APP_NAME}.svg"]),
]  # + compile_translations()

setup(
    name=f"{APP_NAME}",
    version="0.1.0",
    packages=find_packages(),
    scripts=[f"{APP_NAME}"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Emin Fedar",
    author_email="emin.fedar@pardus.org.tr",
    description="Parental Control and Restriction application for Pardus",
    license="GPLv3",
    keywords="",
    url="https://github.com/pardus/pardus-parental-control",
)
