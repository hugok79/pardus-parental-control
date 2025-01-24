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
            "src/managers/BrowserManager.py",
            "src/managers/FileRestrictionManager.py",
            "src/managers/LinuxUserManager.py",
            "src/managers/NetworkFilterManager.py",
            "src/managers/PreferencesManager.py",
            "src/managers/SmartdnsManager.py",
        ],
    ),
    # UI
    (f"/usr/share/pardus/{APP_NAME}/src/ui", ["src/ui/MainWindow.py"]),
    (
        f"/usr/share/pardus/{APP_NAME}/src/ui/page",
        [
            "src/ui/page/PageApplications.py",
            "src/ui/page/PageEmpty.py",
            "src/ui/page/PageSessionTime.py",
            "src/ui/page/PageWebsites.py",
        ],
    ),
    (
        f"/usr/share/pardus/{APP_NAME}/src/ui/widget",
        [
            "src/ui/widget/DialogAppChooser.py",
            "src/ui/widget/ListRowAvatar.py",
            "src/ui/widget/PActionRow.py",
            "src/ui/widget/PTimeChooserRow.py",
        ],
    ),
    # Executable
    ("/usr/bin/", [f"{APP_NAME}"]),
    # Data
    (f"/usr/share/pardus/{APP_NAME}/data", ["data/style.css"]),
    ("/usr/share/icons/hicolor/scalable/apps/", [f"data/{APP_NAME}.svg"]),
    (f"/usr/share/pardus/{APP_NAME}/data", [f"data/{APP_NAME}.svg"]),
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
