import os
import json
from pathlib import Path
import copy

CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
PROFILES_PATH = os.path.join(CONFIG_DIR, "profiles.json")
APPLIED_PROFILE_PATH = os.path.join(CONFIG_DIR, "applied_profile.lock.json")

_DEFAULT_PROFILES = {
    "profile_list": {
        "Profile-1": {
            "application_list": [],
            "website_list": [],
            "user_list": [],
            "is_application_list_allowlist": False,
            "is_website_list_allowlist": False,
        },
    },
    "current_profile": "Profile-1",
    "base_dns_server": "1.1.1.3"
}


class Profile(object):
    def __init__(self, json):
        self.__dict__ = json  # deserialize json object to the profile struct

    # Getters
    def get_application_list(self):
        return self.application_list

    def get_website_list(self):
        return self.website_list

    def get_user_list(self):
        return self.user_list

    def get_is_application_list_allowlist(self):
        return self.is_application_list_allowlist

    def get_is_website_list_allowlist(self):
        return self.is_website_list_allowlist

    # Setters
    def set_application_list(self, value):
        if isinstance(value, list):
            self.application_list = value

    def set_website_list(self, value):
        if isinstance(value, list):
            self.website_list = value

    def set_user_list(self, value):
        if isinstance(value, list):
            self.user_list = value

    def set_is_application_list_allowlist(self, value):
        if isinstance(value, bool):
            self.is_application_list_allowlist = value

    def set_is_website_list_allowlist(self, value):
        if isinstance(value, bool):
            self.is_website_list_allowlist = value

    # JSON
    def as_json(self):
        return json.dumps(
            self.__dict__,
            default=lambda o: o.__dict__,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

    # Insert
    def insert_application(self, app_id):
        if app_id in self.application_list:
            return False

        self.application_list.append(app_id)
        return True

    def insert_website(self, website_domain):
        if website_domain in self.website_list:
            return False

        self.website_list.append(website_domain)
        return True

    def insert_user(self, user_id):
        if user_id in self.user_list:
            return False

        self.user_list.append(user_id)
        return True

    # Delete
    def remove_application(self, app_id):
        if app_id not in self.application_list:
            return False

        self.application_list.remove(app_id)
        return True

    def remove_website(self, website_domain):
        if website_domain not in self.website_list:
            return False

        self.website_list.remove(website_domain)
        return True

    def remove_user(self, user_id):
        if user_id not in self.user_list:
            return False

        self.user_list.remove(user_id)
        return True


class ProfileManager:
    def __init__(self, json=None):
        if json is None:
            self.__dict__ = self.load_json_from_file()
        else:
            self.__dict__ = json  # deserialize json object

        for key in self.profile_list:
            self.profile_list[key] = Profile(self.profile_list[key])

    # Getters
    def get_profile_list(self):
        return self.profile_list

    def get_profile(self, name) -> Profile:
        return self.profile_list[name]

    def get_current_profile(self) -> Profile:
        return self.get_profile(self.current_profile)

    def get_current_profile_name(self):
        return self.current_profile

    def has_profile_name(self, profile_name):
        return profile_name in self.profile_list

    def get_base_dns_server(self):
        return self.base_dns_server

    # Setters
    def set_profile_dict(self, value):
        if isinstance(value, dict):
            self.profile_list = value

        self.save_as_json_file()

    def set_current_profile(self, value):
        if isinstance(value, str):
            self.current_profile = value

        self.save_as_json_file()

    # Insert
    def insert_default_profile(self, profile_name):
        self.profile_list[profile_name] = Profile(
            copy.deepcopy(_DEFAULT_PROFILES["profile_list"]["Profile-1"])
        )

        self.save_as_json_file()

    def duplicate_profile(self, main_profile_name, new_duplicated_profile_name):
        self.profile_list[new_duplicated_profile_name] = Profile(
            copy.deepcopy(self.get_profile(main_profile_name).__dict__)
        )

        self.save_as_json_file()

    # Remove
    def remove_profile(self, profile_name):
        if profile_name not in self.profile_list:
            return

        del self.profile_list[profile_name]

        self.save_as_json_file()

    # Update
    def update_profile_name(self, old_name, new_name):
        if old_name not in self.profile_list:
            return

        self.profile_list[new_name] = self.profile_list[old_name]

        del self.profile_list[old_name]

        if old_name == self.current_profile:
            self.current_profile = new_name

        self.save_as_json_file()

    # JSON
    def as_json(self):
        return json.dumps(
            self.__dict__,
            default=lambda o: o.__dict__,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

    def save_as_json_file(self, filepath=PROFILES_PATH, json_object=None):
        if json_object is None:
            json_object = self.__dict__

        # Create the profiles.json if not exists
        try:
            # First create the directories
            CONFIG_DIR.mkdir(mode=0o600, parents=True, exist_ok=True)

            # Then create the file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    json_object,
                    f,
                    default=lambda o: o.__dict__,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )
        except PermissionError:
            print("Not enough permissions to create the file")
            return

    def load_json_from_file(self, filepath=PROFILES_PATH):
        print("Loading profiles from {}".format(filepath))
        # Read the profiles.json
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("profiles.json file not found, returning the default profiles file.")

            return copy.deepcopy(_DEFAULT_PROFILES)
        except json.JSONDecodeError:
            print(
                "{} is not valid json file. Moving file to backup: profiles.json.backup. Using default profiles.json".format(
                    filepath
                )
            )
            # Backup current one
            os.rename(filepath, "{}.backup".format(filepath))

            return copy.deepcopy(_DEFAULT_PROFILES)


profile_manager = None


def get_default() -> ProfileManager:
    global profile_manager

    if profile_manager is None:
        profile_manager = ProfileManager()

    return profile_manager
