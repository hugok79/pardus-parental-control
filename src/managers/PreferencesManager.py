import os
import json
from pathlib import Path
import copy

CONFIG_DIR = Path("/var/lib/pardus/pardus-parental-control/")
PREFERENCES_PATH = os.path.join(CONFIG_DIR, "preferences.json")

_DEFAULT_USER_PREFERENCES = {
    "application": {
        "list": [],
        "allowlist": False,
        "active": False,
    },
    "website": {
        "list": [],
        "allowlist": False,
        "active": False,
    },
    # Session Time minutes
    "daily_usage": {
        "start": [0, 0, 0, 0, 0, 0, 0],
        "end": [0, 0, 0, 0, 0, 0, 0],
        "limit": [0, 0, 0, 0, 0, 0, 0],
        "active": [False, False, False, False, False, False, False],
    },
}

_DEFAULT_PREFERENCES = {
    "user_list": {},
    "base_dns_servers": ["1.1.1.3", "1.0.0.3"],
}


class ListConfig(object):
    def __init__(self, obj):
        self.__dict__ = obj

    # Getters
    def get_list(self):
        return self.list

    def get_allowlist(self):
        return self.allowlist

    def get_active(self):
        return self.active

    # Setters
    def set_list(self, value):
        if isinstance(value, list):
            self.list = value

    def set_allowlist(self, value):
        if isinstance(value, bool):
            self.allowlist = value

    def set_active(self, value):
        if isinstance(value, bool):
            self.active = value

    # Update
    def list_insert(self, element):
        if element in self.list:
            return False

        self.list.append(element)
        return True

    def list_remove(self, element):
        if element not in self.list:
            return False

        self.list.remove(element)
        return True


class SessionTimeConfig(object):
    def __init__(self, obj):
        self.__dict__ = obj

    # Getters
    def get_start(self, weekday):
        return self.start[weekday]

    def get_end(self, weekday):
        return self.end[weekday]

    def get_limit(self, weekday):
        return self.limit[weekday]

    def get_active(self, weekday):
        return self.active[weekday]

    # Setters
    def set_start(self, weekday, value):
        if isinstance(value, int):
            self.start[weekday] = value

    def set_end(self, weekday, value):
        if isinstance(value, int):
            self.end[weekday] = value

    def set_limit(self, weekday, value):
        if isinstance(value, int):
            self.limit[weekday] = value

    def set_active(self, weekday, value):
        if isinstance(value, bool):
            self.active[weekday] = value


class UserPreferences(object):
    def __init__(self, json_object):
        self.__dict__ = json_object  # deserialize json object to the profile struct

        self.application = ListConfig(self.application)
        self.website = ListConfig(self.website)
        self.daily_usage = SessionTimeConfig(self.daily_usage)

    # Getters
    def get_application(self):
        return self.application

    def get_website(self):
        return self.website

    def get_daily_usage(self):
        return self.daily_usage

    # JSON
    def as_json(self):
        return json.dumps(
            self.__dict__,
            default=lambda o: o.__dict__,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )


class PreferencesManager:
    def __init__(self, json_object=None):
        if json_object is None:
            self.__dict__ = self.load_json_from_file()
        else:
            self.__dict__ = json_object  # deserialize json object

        self.migrate_versions()

    def update_json_from_file(self):
        self.__dict__ = self.load_json_from_file()

        self.migrate_versions()

    def migrate_versions(self):
        for key in self.user_list:
            old = self.user_list[key]
            new = UserPreferences(copy.deepcopy(_DEFAULT_USER_PREFERENCES))

            if "application_list" in self.user_list[key].keys():
                # Convert old <0.4.0 preferences to new ones:
                print(f"{key} user uses <0.4.0 format, migrating to new one...")

                # Application
                # From -> To
                # "application_list": [] -> application.list
                # "is_application_list_allowlist": False -> application.allowlist
                # "is_application_filter_active": False, -> application.active

                new.get_application().set_list(old["application_list"])
                new.get_application().set_allowlist(
                    old["is_application_list_allowlist"]
                )
                new.get_application().set_active(old["is_application_filter_active"])

                # Website
                # "website_list": [] -> website.list
                # "is_website_list_allowlist": False, -> website.allowlist
                # "is_website_filter_active": False, -> website.active

                new.get_website().set_list(old["website_list"])
                new.get_website().set_allowlist(old["is_website_list_allowlist"])
                new.get_website().set_active(old["is_website_filter_active"])

                self.user_list[key] = new
                print(self.user_list[key])
                print(f"{key} migration finished")

            if "session_time" in self.user_list[key]:
                # New session times format, daily_usage_limit <0.5.0
                print(f"{key} user uses <0.5.0 format, migrating to new one...")

                # Application and website are same format in 0.4.0
                new.application = old.application
                new.website = old.website
                # new."daily_usage" is default

                self.user_list[key] = new

                print(self.user_list[key])
                print(f"{key} migration finished")
            else:
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
