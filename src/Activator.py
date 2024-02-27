#!/usr/bin/python3

import os
import sys

if os.geteuid() != 0:
    print("The Pardus Parental Control Activator must be run as root")
    exit(1)


import managers.ProfileManager as ProfileManager
import managers.MalcontentManager as MalcontentManager
import managers.NetworkFilterManager as NetworkFilterManager


class Activator:
    def __init__(self, is_active):
        self.is_active = is_active
        print("active:", is_active)

    def run(self):
        self.read_profile()

        self.set_malcontent_filter()

        self.set_network_filter()

    def read_profile(self):
        self.profile = ProfileManager.get_default().get_current_profile()

    def set_malcontent_filter(self):
        if self.is_active:
            MalcontentManager.set_application_list_from_profile(self.profile)
            MalcontentManager.set_session_times_from_profile(self.profile)
        else:
            MalcontentManager.reset_app_filter_for_all_users()
            MalcontentManager.reset_session_times_for_all_users()

    def set_network_filter(self):
        if self.is_active:
            NetworkFilterManager.stop_smartdns_service()

            website_list = self.profile.get_website_list()
            is_allowlist = self.profile.get_is_website_list_allowlist()

            if is_allowlist:
                NetworkFilterManager.set_allow_domain_list(website_list)
            else:
                NetworkFilterManager.set_deny_domain_list(website_list)

            NetworkFilterManager.start_smartdns_service()
        else:
            NetworkFilterManager.stop_smartdns_service()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(
            "Usage: ./Activator.py [ 1(activate) or 0(deactivate) ]. e.g. ./Activator.py 1\n"
        )
        exit(1)

    is_active = int(sys.argv[1])
    activator = Activator(is_active)
    activator.run()
