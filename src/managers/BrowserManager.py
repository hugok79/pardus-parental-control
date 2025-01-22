import copy
import json
import os
from pathlib import Path


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
        # This is disabled because it doesn't work properly.
        # "WebsiteFilter": {
        # https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Match_patterns
        #    "Block": [],  # eg "<all_urls>"
        #    "Exceptions": [],  # eg "*://*.youtube.com/*", "*://*.pardus.org.tr/*"
        # },
        "DNSOverHTTPS": {"Enabled": False, "Locked": True},
    }
}


def _generate_chromium_policy(domain_list, is_allowlist):
    chromium_policy_object = copy.deepcopy(CHROME_POLICY_JSON)

    if is_allowlist:
        # Block everything except allowlist
        chromium_policy_object["URLBlocklist"] = ["*"]
        chromium_policy_object["URLAllowlist"] = domain_list
    else:
        chromium_policy_object["URLAllowlist"] = []
        chromium_policy_object["URLBlocklist"] = domain_list

    return chromium_policy_object


def _generate_firefox_policy(domain_list, is_allowlist):
    firefox_policy_object = copy.deepcopy(FIREFOX_POLICY_JSON)

    # Firefox browser policy doesn't work properly, it is commented for now:
    """
    if is_allowlist:
        # Block everything except allowlist
        firefox_policy_object["policies"]["WebsiteFilter"]["Block"] = ["<all_urls>"]

        # convert e.g. "google.com" -> "*://*.google.com/*"
        firefox_policy_object["policies"]["WebsiteFilter"]["Exceptions"] = list(
            map(lambda x: "*://{}/*".format(x), domain_list)
        )
    else:
        # convert e.g. "google.com" -> "*://*.google.com/*"
        firefox_policy_object["policies"]["WebsiteFilter"]["Block"] = list(
            map(lambda x: "*://{}/*".format(x), domain_list)
        )
        firefox_policy_object["policies"]["WebsiteFilter"]["Exceptions"] = []
    """

    return firefox_policy_object


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

    print("Browser Policy Saved:{}".format(browser_config_path))


def create_browser_config(domain_list, is_allowlist):
    chromium_policy = _generate_chromium_policy(domain_list, is_allowlist)
    firefox_policy = _generate_firefox_policy(domain_list, is_allowlist)

    # Save for all browsers
    _save_browser_policy(CHROME_POLICY_PATH, chromium_policy)
    _save_browser_policy(BRAVE_POLICY_PATH, chromium_policy)
    _save_browser_policy(CHROMIUM_POLICY_PATH, chromium_policy)
    _save_browser_policy(CHROMIUM2_POLICY_PATH, chromium_policy)
    _save_browser_policy(FIREFOX_POLICY_PATH, firefox_policy)


def remove_browser_config():
    _remove_file_if_exists(CHROME_POLICY_PATH)
    _remove_file_if_exists(BRAVE_POLICY_PATH)
    _remove_file_if_exists(CHROMIUM_POLICY_PATH)
    _remove_file_if_exists(CHROMIUM2_POLICY_PATH)
    _remove_file_if_exists(FIREFOX_POLICY_PATH)


def _remove_file_if_exists(path):
    if os.path.exists(path):
        os.remove(path)
        print("Removed: {}".format(path))
