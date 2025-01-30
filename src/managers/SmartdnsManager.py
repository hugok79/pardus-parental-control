import os
import subprocess
from pathlib import Path

SMARTDNS_CONF_PATH = "/etc/smartdns/smartdns.conf"

SMARTDNS_CONF_HEADER = """# Listen on local port 53
bind [::]:53
bind-tcp [::]:53

tcp-idle-time 5
"""

SMARTDNS_CONF_DENY_ADULT_PREPEND = """
domain-set -name adult -type list -file /usr/share/pardus/pardus-parental-control/data/anti-adult.list
address /domain-set:adult/#
"""

SMARTDNS_CONF_DNS_SERVER_TEMPLATE = """
server {DNS_SERVER}
server-tcp {DNS_SERVER}
"""

SMARTDNS_CONF_DENY_DOMAIN_TEMPLATE = """
address /{domain}/#
address /*.{domain}/#
"""
SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE = """
address /{domain}/-
address /*.{domain}/-
"""

SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE_END = """
address /./#
"""


def _generate_dns_server_config(dns_servers):
    # Base DNS Servers
    content = "# Remote DNS Servers"
    for server in dns_servers:
        content += SMARTDNS_CONF_DNS_SERVER_TEMPLATE.format(DNS_SERVER=server)

    return content


def _generate_domain_list_config(domain_list, is_allowlist):
    content = "# Address Filters"
    if is_allowlist:
        for d in domain_list:
            content += SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE.format(domain=d)

        content += SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE_END
    else:
        for d in domain_list:
            content += SMARTDNS_CONF_DENY_DOMAIN_TEMPLATE.format(domain=d)

        content += SMARTDNS_CONF_DENY_ADULT_PREPEND

    return content


def generate_smartdns_config(domain_list, is_allowlist, dns_servers):
    dns_server_config = _generate_dns_server_config(dns_servers)
    domain_list_config = _generate_domain_list_config(domain_list, is_allowlist)

    full_content = (
        SMARTDNS_CONF_HEADER + "\n" + dns_server_config + "\n" + domain_list_config
    )

    return full_content


def create_smartdns_config(domain_list, is_allowlist, dns_servers):
    # example list = ["google.com", "youtube.com"]

    # Create folders
    if not os.path.isfile(SMARTDNS_CONF_PATH):
        Path(SMARTDNS_CONF_PATH).parent.mkdir(mode=0o775, parents=True, exist_ok=True)

    # Create file
    with open(SMARTDNS_CONF_PATH, "w") as file1:
        content = generate_smartdns_config(domain_list, is_allowlist, dns_servers)
        file1.write(content)

        print("Created smartdns config file: {}".format(SMARTDNS_CONF_PATH))


def remove_smartdns_config():
    if os.path.exists(SMARTDNS_CONF_PATH):
        os.remove(SMARTDNS_CONF_PATH)
        print("Removed: {}".format(SMARTDNS_CONF_PATH))


def stop_smartdns_service():
    return subprocess.run(["systemctl", "stop", "smartdns-rs.service"])


def start_smartdns_service():
    return subprocess.run(["systemctl", "start", "smartdns-rs.service"])


def restart_smartdns_service():
    return subprocess.run(["systemctl", "restart", "smartdns-rs.service"])


def disable_smartdns_service():
    return subprocess.run(["systemctl", "disable", "smartdns-rs.service"])


def enable_smartdns_service():
    return subprocess.run(["systemctl", "enable", "smartdns-rs.service"])


def install_smartdns_service():
    return subprocess.run(["smartdns", "service", "install"])
