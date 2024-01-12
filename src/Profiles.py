import os
import json
from pathlib import Path
import copy

PROFILES_DIR = Path("/var/lib/pardus/pardus-parental-control/")
PROFILES_PATH = os.path.join(PROFILES_DIR, "profiles.json")

_DEFAULT_PROFILES = {
    "profiles": {
        "Profile-1": {
            "application_list": [],
            "website_list": [],
            "user_list": [],
            "is_application_list_allowed": True,
            "is_website_list_allowed": True
        },
    },
    "current_profile": "Profile-1"
}


def _save_all_profiles_file(content):
    # Create the profiles.json if not exists
    try:
        # First create the directories
        PROFILES_DIR.mkdir(mode=0o600, parents=True, exist_ok=True)

        # Then create the file
        # print("Saving content:")
        # print(json.dumps(content, indent=4, sort_keys=True))

        with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False,
                      indent=4, sort_keys=True)
    except PermissionError:
        print("Not enough permissions to create the file")


def _read_profiles_file():
    # Read the profiles.json
    try:
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            obj = json.load(f)

            return obj
    except FileNotFoundError:
        print("Profiles file not found, returning the default profiles file.")
        return _DEFAULT_PROFILES
    except json.JSONDecodeError:
        print(f"{PROFILES_PATH} is corrupted. Using default profiles.")
        _save_all_profiles_file(_DEFAULT_PROFILES)
        return _DEFAULT_PROFILES


# Create profiles file if not exists:
if not os.path.isfile(PROFILES_PATH):
    _save_all_profiles_file(_DEFAULT_PROFILES)

# Read profiles.json file
PROFILES = _read_profiles_file()


# === public user functions ===

# GETTERs
def get_all_profiles():
    return PROFILES["profiles"]


def get_current_profile_name():
    return PROFILES["current_profile"]


def get_current_profile():
    return PROFILES["profiles"][PROFILES["current_profile"]]


def get_current_profile_property(property_name):
    profile = get_current_profile()
    return profile[property_name]


def has_profile_name(profile_name):
    return profile_name in PROFILES["profiles"]


# SETTERs
def save_all_profiles():
    _save_all_profiles_file(PROFILES)


def set_current_profile_name(profile_name):
    PROFILES["current_profile"] = profile_name
    save_all_profiles()

# INSERTs


def add_new_profile(profile_name):
    if has_profile_name(profile_name):
        return False

    PROFILES["profiles"][profile_name] = copy.deepcopy(
        _DEFAULT_PROFILES["profiles"]["Profile-1"])

    save_all_profiles()

# UPDATEs


def update_profile_name(old_name, new_name):
    PROFILES["profiles"][new_name] = PROFILES["profiles"][old_name]
    del PROFILES["profiles"][old_name]

    save_all_profiles()


def update_current_profile_property(property_name, value):
    profile = get_current_profile()
    profile[property_name] = value

    save_all_profiles()

# DELETEs


def delete_profile(profile_name):
    del PROFILES["profiles"][profile_name]

    save_all_profiles()


# Application Settings


def add_application_to_current_profile(app_id):
    profile = get_current_profile()

    if app_id in profile["application_list"]:
        return False

    profile["application_list"].append(app_id)

    save_all_profiles()
    return True


def delete_application_from_current_profile(app_id):
    profile = get_current_profile()

    if app_id in profile["application_list"]:
        profile["application_list"].remove(app_id)

        save_all_profiles()
        return True

    return False

# Website Settings


def add_website_to_current_profile(domain):
    profile = get_current_profile()

    if domain in profile["website_list"]:
        return False

    profile["website_list"].append(domain)

    save_all_profiles()
    return True


def delete_website_from_current_profile(domain):
    profile = get_current_profile()

    if domain in profile["website_list"]:
        profile["website_list"].remove(domain)

        save_all_profiles()
        return True

    return False

# User Settings


def add_user_to_current_profile(user_id):
    profile = get_current_profile()

    if user_id in profile["user_list"]:
        return False

    profile["user_list"].append(user_id)

    save_all_profiles()
    return True


def delete_user_from_current_profile(user_id):
    profile = get_current_profile()

    if user_id in profile["user_list"]:
        profile["user_list"].remove(user_id)

        save_all_profiles()
        return True

    return False
