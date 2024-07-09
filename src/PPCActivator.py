#!/usr/bin/python3

import sys
import os
import time
import managers.FileRestrictionManager as FileRestrictionManager


import managers.ProfileManager as ProfileManager
import managers.NetworkFilterManager as NetworkFilterManager
import managers.ApplicationManager as ApplicationManager


class PPCActivator:
    def __init__(self, is_activated):
        self.is_activated = is_activated
        print("active:", is_activated)

        # Privileged run check
        if not FileRestrictionManager.check_user_privileged():
            sys.stderr.write("You are not privileged to run this script.\n")
            sys.exit(1)

    def run(self, is_activated=None):
        print("== PPCActivator STARTED ==")
        print("uid:", os.getuid())
        print("gid:", os.getgid())

        if is_activated is not None:
            self.is_activated = is_activated

        if self.is_activated:
            self.read_profile()
        else:
            self.read_applied_profile()

        self.set_application_filter()
        self.set_network_filter()

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
            restriction_type = profile.get_application_restriction_type()

            if restriction_type == "allowlist":
                all_applications = ApplicationManager.get_all_applications()

                for app in all_applications:
                    if app.get_id() not in profile.get_application_allowlist():
                        ApplicationManager.restrict_application(app.get_id())
            elif restriction_type == "denylist":
                for app_id in profile.get_application_denylist():
                    ApplicationManager.restrict_application(app_id)
            else:
                # restriction_type = "none"
                pass

        else:
            profile = self.applied_profile
            restriction_type = profile.get_application_restriction_type()

            if restriction_type == "allowlist":
                all_applications = ApplicationManager.get_all_applications()
                for app in all_applications:
                    # Remove All app restrictions
                    ApplicationManager.unrestrict_application(app.get_id())
            elif restriction_type == "denylist":
                for app_id in profile.get_application_denylist():
                    ApplicationManager.unrestrict_application(app_id)
            else:
                # restriction_type = "none"
                pass

    def set_network_filter(self):
        profile_manager = ProfileManager.get_default()

        if self.is_activated:
            profile = self.profile
            restriction_type = profile.get_website_restriction_type()

            if restriction_type == "none":
                return

            # browser + domain configs
            if restriction_type == "allowlist":
                website_list = profile.get_website_allowlist()

                NetworkFilterManager.set_domain_filter_list(
                    website_list, True, profile_manager.get_base_dns_server()
                )
            elif restriction_type == "denylist":
                website_list = profile.get_website_denylist()
                if len(website_list) == 0:
                    return

                NetworkFilterManager.set_domain_filter_list(
                    website_list, False, profile_manager.get_base_dns_server()
                )

            # resolvconf
            NetworkFilterManager.set_resolvconf_to_localhost()

            # smartdns-rs
            NetworkFilterManager.enable_smartdns_service()
            time.sleep(1)
            NetworkFilterManager.restart_smartdns_service()
        else:
            profile = self.applied_profile
            restriction_type = profile.get_website_restriction_type()

            if restriction_type == "none":
                return

            # browser + domain configs
            NetworkFilterManager.reset_domain_filter_list()

            # resolvconf
            NetworkFilterManager.reset_resolvconf_to_default()

            # smartdns-rs
            NetworkFilterManager.stop_smartdns_service()
            NetworkFilterManager.disable_smartdns_service()


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
