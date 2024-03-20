#!/usr/bin/python3

import os
import sys

if os.geteuid() != 0:
    sys.stderr.write("The Pardus Parental Control Service must be run as root\n")
    exit(1)


import managers.ProfileManager as ProfileManager

# import managers.MalcontentManager as MalcontentManager
import managers.NetworkFilterManager as NetworkFilterManager


class PPCService:
    def __init__(self, is_active):
        self.is_active = is_active
        print("active:", is_active)

    def run(self):
        self.read_profile()

        # self.set_malcontent_filter()

        self.set_network_filter()

    def read_profile(self):
        self.profile = ProfileManager.get_default().get_current_profile()

    # def set_malcontent_filter(self):
    #     if self.is_active:
    #         MalcontentManager.set_application_list_from_profile(self.profile)
    #         MalcontentManager.set_session_times_from_profile(self.profile)
    #     else:
    #         MalcontentManager.reset_app_filter_for_all_users()
    #         MalcontentManager.reset_session_times_for_all_users()

    def set_network_filter(self):
        if self.is_active:
            website_list = self.profile.get_website_list()
            if len(website_list) == 0:
                print("No website list found in profile")
                return

            is_allowlist = self.profile.get_is_website_list_allowlist()

            if is_allowlist:
                NetworkFilterManager.set_allow_domain_list(website_list)
            else:
                NetworkFilterManager.set_deny_domain_list(website_list)

            NetworkFilterManager.set_resolvconf_to_localhost()

            NetworkFilterManager.enable_smartdns_service()
            NetworkFilterManager.start_smartdns_service()
        else:
            NetworkFilterManager.reset_resolvconf_to_default()

            NetworkFilterManager.stop_smartdns_service()
            NetworkFilterManager.disable_smartdns_service()


if len(sys.argv) < 2:
    sys.stderr.write(
        f"Usage: {sys.argv[0]} [ 1(activate) or 0(deactivate) ]. e.g. {sys.argv[0]} 1\n"
    )
    exit(1)

is_active = int(sys.argv[1])
ppc_service = PPCService(is_active)
ppc_service.run()
