import os
import json
from pathlib import Path
import copy

CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
PREFERENCES_PATH = os.path.join(CONFIG_DIR, "preferences.json")

_DEFAULT_USER_PREFERENCES = {
    # Lists
    "application_list": [],
    "website_list": [],
    # Allowlist Flags
    "is_application_list_allowlist": False,
    "is_website_list_allowlist": False,
    # Active Flags
    "is_application_filter_active": False,
    "is_website_filter_active": False,
    "is_session_time_filter_active": False,
    # Session Time minutes
    "session_time_start": 0,
    "session_time_end": 0,
}

_DEFAULT_PREFERENCES = {
    "user_list": {},
    "base_dns_servers": [
        "185.228.168.10",
        "185.228.169.11",
    ],  # Cleanbrowsing Adult Filter
}


class UserPreferences(object):
    def __init__(self, json):
        self.__dict__ = json  # deserialize json object to the profile struct

    # Getters
    def get_application_list(self):
        return self.application_list

    def get_website_list(self):
        return self.website_list

    def get_is_application_list_allowlist(self):
        return self.is_application_list_allowlist

    def get_is_website_list_allowlist(self):
        return self.is_website_list_allowlist

    def get_is_application_filter_active(self):
        return self.is_application_filter_active

    def get_is_website_filter_active(self):
        return self.is_website_filter_active

    def get_is_session_time_filter_active(self):
        return self.is_session_time_filter_active

    def get_session_time_start(self):
        return self.session_time_start

    def get_session_time_end(self):
        return self.session_time_end

    # Setters
    def set_application_list(self, value):
        if isinstance(value, list):
            self.application_list = value

    def set_website_list(self, value):
        if isinstance(value, list):
            self.website_list = value

    def set_is_application_list_allowlist(self, value):
        if isinstance(value, bool):
            self.is_application_list_allowlist = value

    def set_is_website_list_allowlist(self, value):
        if isinstance(value, bool):
            self.is_website_list_allowlist = value

    def set_is_application_filter_active(self, value):
        if isinstance(value, bool):
            self.is_application_filter_active = value

    def set_is_website_filter_active(self, value):
        if isinstance(value, bool):
            self.is_website_filter_active = value

    def set_is_session_time_filter_active(self, value):
        if isinstance(value, bool):
            self.is_session_time_filter_active = value

    def set_session_time_start(self, value):
        if isinstance(value, int):
            self.session_time_start = value

    def set_session_time_end(self, value):
        if isinstance(value, int):
            self.session_time_end = value

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


class PreferencesManager:
    def __init__(self, json=None):
        if json is None:
            self.__dict__ = self.load_json_from_file()
        else:
            self.__dict__ = json  # deserialize json object

        for key in self.user_list:
            self.user_list[key] = UserPreferences(self.user_list[key])

    def update_json_from_file(self):
        self.__dict__ = self.load_json_from_file()

        for key in self.user_list:
            self.user_list[key] = UserPreferences(self.user_list[key])

    # Getters
    def get_user_list(self):
        return self.user_list

    def get_user(self, name) -> UserPreferences:
        return self.user_list[name]

    def has_user(self, name):
        return name in self.user_list

    def get_base_dns_servers(self):
        return self.base_dns_servers

    # Setters
    def set_user_list(self, value):
        if isinstance(value, dict):
            self.user_list = value

        self.save()

    def set_base_dns_servers(self, value):
        if isinstance(value, list):
            self.set_base_dns_servers = value

    # Insert
    def insert_new_user(self, name):
        if name in self.user_list:
            return self.user_list[name]

        self.user_list[name] = UserPreferences(copy.deepcopy(_DEFAULT_USER_PREFERENCES))

        self.save()

        return self.user_list[name]

    # Remove
    def remove_user(self, name):
        if name not in self.user_list:
            return

        del self.user_list[name]

        self.save()

    # JSON
    def as_json(self):
        return json.dumps(
            self.__dict__,
            default=lambda o: o.__dict__,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

    def save(self, filepath=PREFERENCES_PATH, json_object=None):
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
            print(
                "Not enough permissions to create the file:",
            )
            return

    def load_json_from_file(self, filepath=PREFERENCES_PATH):
        # Read the profiles.json
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"'{filepath}' not found, returning the default profiles file.")

            return copy.deepcopy(_DEFAULT_PREFERENCES)
        except json.JSONDecodeError:
            print(
                "{} is not valid json file. Moving file to backup: profiles.json.backup. Using default profiles.json".format(
                    filepath
                )
            )
            # Backup current one
            os.rename(filepath, "{}.backup".format(filepath))

            return copy.deepcopy(_DEFAULT_PREFERENCES)


preferences_manager = None


def get_default() -> PreferencesManager:
    global preferences_manager

    if preferences_manager is None:
        preferences_manager = PreferencesManager()

    return preferences_manager
