#!/usr/bin/python3

import os
import subprocess
import sys

import managers.SystemPreferencesManager as SystemPreferencesManager


def run(args=[], capture_output=False):
    return subprocess.run(
        ["pkexec", os.path.abspath(__file__)] + args,
        capture_output=capture_output,
    )


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]

        manager = SystemPreferencesManager.get_default()

        if cmd == "dns":
            dns_servers = sys.argv[2]
            dns_server_list = manager.extract_dns_list(dns_servers)
            manager.set_base_dns_servers(dns_server_list)

            manager.save()
