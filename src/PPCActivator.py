#!/usr/bin/python3

import sys
import subprocess
import os
import managers.FileRestrictionManager as FileRestrictionManager
import managers.LinuxUserManager as LinuxUserManager
import managers.ProfileManager as ProfileManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.ApplicationManager as ApplicationManager

CWD = os.path.dirname(os.path.abspath(__file__))


def run_activator(activate):
    process = subprocess.run(
        [
            "pkexec",
            CWD + "/PPCActivator.py",
            "1" if activate else "0",
        ]
    )

    return process


class PPCActivator:
    def __init__(self, is_activated):
        self.is_activated = is_activated

        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

    def run(self, is_activated=None):
        print("== PPCActivator STARTED ==")

        if is_activated is not None:
            self.is_activated = is_activated

        if self.is_activated:
            self.read_profile()
        else:
            self.read_applied_profile()

        self.set_application_filter()
        self.set_network_filter()
        self.set_user_groups()
        self.copy_session_time_checker()

        if self.is_activated:
            self.save_applied_profile()
        else:
            self.remove_applied_profile()

        print("== PPCActivator FINISHED ==")

    def read_profile(self):
        self.profile = ProfileManager.get_default().get_current_profile()

    def read_applied_profile(self):
        self.applied_profile = ProfileManager.Profile(
            ProfileManager.get_default().load_json_from_file(
                ProfileManager.APPLIED_PROFILE_PATH
            )
        )

    def save_applied_profile(self):
        profile_manager = ProfileManager.get_default()
        current_profile = profile_manager.get_current_profile()

        profile_manager.save_as_json_file(
            ProfileManager.APPLIED_PROFILE_PATH, current_profile
        )

    def remove_applied_profile(self):
        if os.path.isfile(ProfileManager.APPLIED_PROFILE_PATH):
            os.remove(ProfileManager.APPLIED_PROFILE_PATH)

    def set_application_filter(self):
        if self.is_activated:
            profile = self.profile

            is_allowlist = profile.get_is_application_list_allowlist()
            list_length = len(profile.get_application_list())

            if list_length == 0:
                return

            if is_allowlist:
                all_applications = ApplicationManager.get_all_applications()

                for app in all_applications:
                    if app.get_id() not in profile.get_application_list():
                        ApplicationManager.restrict_application(app.get_id())

            else:
                for app_id in profile.get_application_list():
                    ApplicationManager.restrict_application(app_id)

        else:
            profile = self.applied_profile

            is_allowlist = profile.get_is_application_list_allowlist()
            list_length = len(profile.get_application_list())

            if list_length == 0:
                return

            if is_allowlist:
                all_applications = ApplicationManager.get_all_applications()
                for app in all_applications:
                    # Remove All app restrictions
                    ApplicationManager.unrestrict_application(app.get_id())
            else:
                for app_id in profile.get_application_list():
                    ApplicationManager.unrestrict_application(app_id)

    def set_network_filter(self):
        profile_manager = ProfileManager.get_default()

        if self.is_activated:
            profile = self.profile
            is_allowlist = profile.get_is_website_list_allowlist()
            list_length = len(profile.get_website_list())

            if list_length == 0:
                return

            website_list = profile.get_website_list()

            # browser + domain configs
            if is_allowlist:
                NetworkFilterManager.set_domain_filter_list(
                    website_list, True, profile_manager.get_base_dns_server()
                )
            else:
                NetworkFilterManager.set_domain_filter_list(
                    website_list, False, profile_manager.get_base_dns_server()
                )

            # smartdns-rs
            is_run_smartdns = profile.get_run_smartdns()
            if is_run_smartdns:
                # resolvconf
                NetworkFilterManager.set_resolvconf_to_localhost()
                NetworkFilterManager.enable_smartdns_service()
                NetworkFilterManager.restart_smartdns_service()
        else:
            profile = self.applied_profile

            is_allowlist = profile.get_is_website_list_allowlist()
            list_length = len(profile.get_website_list())

            if list_length == 0:
                return

            # browser + domain configs
            NetworkFilterManager.reset_domain_filter_list()

            # smartdns-rs
            is_run_smartdns = profile.get_run_smartdns()
            if is_run_smartdns:
                NetworkFilterManager.reset_resolvconf_to_default()

                NetworkFilterManager.stop_smartdns_service()
                NetworkFilterManager.disable_smartdns_service()

    def set_user_groups(self):
        standard_users = LinuxUserManager.get_standard_users()

        if self.is_activated:
            profile = self.profile
            for user in standard_users:
                username = user.get_user_name()

                if username not in profile.get_user_list():
                    LinuxUserManager.add_user_to_privileged_group(username)
        else:
            profile = self.applied_profile
            for user in standard_users:
                username = user.get_user_name()

                if username not in profile.get_user_list():
                    LinuxUserManager.remove_user_from_privileged_group(username)

    def copy_session_time_checker(self):
        user_check_desktop_file = "tr.org.pardus.parental-control.user-check.desktop"
        autostart_user_check_desktop_path = CWD + "/../data/" + user_check_desktop_file
        autostart_dir = "/etc/xdg/autostart/"

        if self.is_activated:
            subprocess.run(["cp", autostart_user_check_desktop_path, autostart_dir])
        else:
            os.remove(autostart_dir + "/" + user_check_desktop_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(
            "Usage: {} [ 1(activate) or 0(deactivate) ]. e.g. {} 1\n".format(
                sys.argv[0], sys.argv[0]
            )
        )
        exit(1)

    is_activated = int(sys.argv[1])
    activator = PPCActivator(is_activated)
    activator.run()
