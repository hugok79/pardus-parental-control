import subprocess

SMARTDNS_CONF_PATH = "/etc/smartdns/smartdns.conf"

SMARTDNS_CONF_DEFAULT = """
# Listen on local port 53
bind [::]:53
bind-tcp [::]:53

tcp-idle-time 5

# Cache
cache-size 32768

# DNS servers, 1.1.1.3 is basically: "1.1.1.1 + No Malware + No Adult Content"
server 1.1.1.3
server-tls 1.1.1.3

"""

SMARTDNS_CONF_DENY_DOMAIN_TEMPLATE = """
address /{}/#
address /*.{}/#
"""
SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE = """
address /{}/-
"""

SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE_END = """
address /*/#
"""


def reset_dns_config():
    with open(SMARTDNS_CONF_PATH, "w") as file1:
        # Writing data to a file
        file1.write(SMARTDNS_CONF_DEFAULT)


def set_deny_domain_list(list):
    # example list = ["google.com", "youtube.com"]

    with open(SMARTDNS_CONF_PATH, "w") as file1:
        content = SMARTDNS_CONF_DEFAULT
        for domain in list:
            deny_domain_content = SMARTDNS_CONF_DENY_DOMAIN_TEMPLATE.format(
                domain, domain
            )
            content += "\n" + deny_domain_content

        file1.write(content)


def set_allow_domain_list(list):
    # example list = ["google.com", "youtube.com"]

    with open(SMARTDNS_CONF_PATH, "w") as file1:
        content = SMARTDNS_CONF_DEFAULT
        for domain in list:
            allow_domain_content = SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE.format(domain)
            content += "\n" + allow_domain_content

        content += SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE_END

        file1.write(content)


def stop_smartdns_service():
    return subprocess.run(["systemctl", "stop", "smartdns-rs"])


def start_smartdns_service():
    return subprocess.run(["systemctl", "start", "smartdns-rs"])


def restart_smartdns_service():
    return subprocess.run(["systemctl", "restart", "smartdns-rs"])
