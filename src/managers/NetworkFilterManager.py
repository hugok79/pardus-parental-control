import subprocess
import json
import copy
from pathlib import Path
import os

SMARTDNS_CONF_PATH = "/etc/smartdns/smartdns.conf"
RESOLV_CONF_PATH = "/etc/resolv.conf"

SMARTDNS_CONF_DEFAULT = """
# Listen on local port 53
bind [::]:53
bind-tcp [::]:53

# Certificated Listening
#bind-tls [::]:853 # DoT
#bind-https [::]:853 # DoH

tcp-idle-time 4

# Base DNS Server
server {BASE_DNS_SERVER}
server-tcp {BASE_DNS_SERVER}

# DNS over TLS (DoT)
#server-https https://cloudflare-dns.com/dns-query 
#server-tls {BASE_DNS_SERVER}

# Dns over Quic (DoQ)
#server-quic family.adguard-dns.com

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

CHROME_POLICY_PATH = Path("/etc/opt/chrome/policies/managed/policies.json")
BRAVE_POLICY_PATH = Path("/etc/brave/policies/managed/policies.json")
CHROMIUM_POLICY_PATH = Path("/etc/chromium/policies/managed/policies.json")
CHROMIUM2_POLICY_PATH = Path("/etc/chromium-browser/policies/managed/policies.json")
FIREFOX_POLICY_PATH = Path("/etc/firefox/policies/policies.json")

CHROME_POLICY_JSON = {
    "URLBlocklist": [],  # e.g. "google.com", "*" to block everything, "youtube.com"
    "URLAllowlist": [],
    "DnsOverHttpsMode": "off",
}
FIREFOX_POLICY_JSON = {
    "policies": {
        "WebsiteFilter": {
            # https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Match_patterns
            "Block": [],  # eg "<all_urls>"
            "Exceptions": [],  # eg "*://*.youtube.com/*", "*://*.pardus.org.tr/*"
        },
        "DNSOverHTTPS": {"Enabled": False, "Locked": True},
    }
}

RESOLV_CONF_CONTENT = """# This file is generated & locked by pardus-parental-control app. Please do not change.

nameserver 127.0.0.1

"""


def set_resolvconf_to_localhost():
    subprocess.run(["chattr", "-i", "/etc/resolv.conf"])  # unblock file

    with open(RESOLV_CONF_PATH, "w") as file1:
        file1.write(RESOLV_CONF_CONTENT)

    subprocess.run(["chattr", "+i", "/etc/resolv.conf"])  # block file


def reset_resolvconf_to_default():
    subprocess.run(["chattr", "-i", "/etc/resolv.conf"])  # unblock file
    subprocess.run(["rm", "/etc/resolv.conf"])  # delete file
    subprocess.run(
        ["systemctl", "restart", "NetworkManager.service"]
    )  # generate new resolvconf from network manager


def set_domain_filter_list(list, is_allowlist, base_dns_server):
    # example list = ["google.com", "youtube.com"]
    # don't add subdomains like www.google.com or mail.google.com

    _set_smartdns_filter_domain_list(list, is_allowlist, base_dns_server)
    _set_browser_policy_domain_list(list, is_allowlist)


def reset_domain_filter_list():
    _reset_smartdns_filter_domain_list()
    _reset_browser_policy_domain_list()


def _set_smartdns_filter_domain_list(list, is_allowlist, base_dns_server):
    # example list = ["google.com", "youtube.com"]

    if not os.path.isfile(SMARTDNS_CONF_PATH):
        Path(SMARTDNS_CONF_PATH).parent.mkdir(mode=0o775, parents=True, exist_ok=True)

    with open(SMARTDNS_CONF_PATH, "w") as file1:
        content = SMARTDNS_CONF_DEFAULT.format(BASE_DNS_SERVER=base_dns_server)
        if is_allowlist:
            for domain in list:
                allow_domain_content = SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE.format(
                    domain=domain
                )
                content += "\n" + allow_domain_content

            content += SMARTDNS_CONF_ALLOW_DOMAIN_TEMPLATE_END
        else:
            for domain in list:
                deny_domain_content = SMARTDNS_CONF_DENY_DOMAIN_TEMPLATE.format(
                    domain=domain
                )
                content += "\n" + deny_domain_content

        file1.write(content)

        print("Created smartdns config file: {}".format(SMARTDNS_CONF_PATH))


def _reset_smartdns_filter_domain_list():
    remove_file_if_exists(SMARTDNS_CONF_PATH)


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


# util
def remove_file_if_exists(path):
    if os.path.exists(path):
        os.remove(path)
        print("REMOVED: {}".format(path))


# Browser policies
def _set_browser_policy_domain_list(domainlist, is_allowlist):
    chromium_policy_object = copy.deepcopy(CHROME_POLICY_JSON)
    firefox_policy_object = copy.deepcopy(FIREFOX_POLICY_JSON)

    if is_allowlist:
        # Block everything except allowlist
        chromium_policy_object["URLBlocklist"] = ["*"]
        chromium_policy_object["URLAllowlist"] = domainlist

        # Block everything except allowlist
        # TODO: Firefox policy files not working properly. Comment this until firefox fix it.
        # firefox_policy_object["policies"]["WebsiteFilter"]["Block"] = ["<all_urls>"]
        # # convert e.g. "google.com" -> "*://*.google.com/*"
        # firefox_policy_object["policies"]["WebsiteFilter"]["Exceptions"] = list(
        #     map(lambda x: "*://{}/*".format(x), domainlist)
        # )
    else:
        chromium_policy_object["URLAllowlist"] = []
        chromium_policy_object["URLBlocklist"] = domainlist

        # convert e.g. "google.com" -> "*://*.google.com/*"
        # TODO: Firefox policy files not working properly. Comment this until firefox fix it.
        # firefox_policy_object["policies"]["WebsiteFilter"]["Block"] = list(
        #     map(lambda x: "*://{}/*".format(x), domainlist)
        # )
        # firefox_policy_object["policies"]["WebsiteFilter"]["Exceptions"] = []

    # Save for all browsers
    _save_browser_policy(CHROME_POLICY_PATH, chromium_policy_object)
    _save_browser_policy(BRAVE_POLICY_PATH, chromium_policy_object)
    _save_browser_policy(CHROMIUM_POLICY_PATH, chromium_policy_object)
    _save_browser_policy(CHROMIUM2_POLICY_PATH, chromium_policy_object)
    _save_browser_policy(FIREFOX_POLICY_PATH, firefox_policy_object)


def _reset_browser_policy_domain_list():
    remove_file_if_exists(CHROME_POLICY_PATH)
    remove_file_if_exists(BRAVE_POLICY_PATH)
    remove_file_if_exists(CHROMIUM_POLICY_PATH)
    remove_file_if_exists(CHROMIUM2_POLICY_PATH)
    remove_file_if_exists(FIREFOX_POLICY_PATH)


def _save_browser_policy(browser_config_path: Path, policy_json_object):
    if not browser_config_path.exists():
        browser_config_path.parent.mkdir(parents=True, exist_ok=True)
        browser_config_path.touch()

    with open(browser_config_path, "w") as file1:
        json_text = json.dumps(
            policy_json_object,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

        json_text += "\n"
        file1.write(json_text)

    print("BROWSER POLICY:{}".format(browser_config_path))


def _read_browser_policy(browser_config_path):
    with open(browser_config_path, "r") as file1:
        return json.load(file1)
