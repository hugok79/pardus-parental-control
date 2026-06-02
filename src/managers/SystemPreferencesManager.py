import copy
import ipaddress
import json
import os

import managers.PreferencesManager as PreferencesManager

SYSTEM_PREFS_PATH = os.path.join(
    PreferencesManager.CONFIG_DIR, "system_preferences.json"
)

_DEFAULT_PREFERENCES = {
    "base_dns_servers": ["1.1.1.3", "1.0.0.3"],
}


class SystemPreferencesManager:
    def __init__(self, json_object=None):
        if json_object is None:
            self.__dict__ = self.load_json_from_file()
        else:
            self.__dict__ = json_object  # deserialize json object

    def get_base_dns_servers(self):
        return self.base_dns_servers

    def set_base_dns_servers(self, value):
        if isinstance(value, list):
            self.base_dns_servers = value

    def extract_dns_list(self, value):
        try:
            servers = [s.strip() for s in value.split(",")]

            if not servers or any(not s for s in servers):
                return []

            for server in servers:
                ipaddress.IPv4Address(server)

            return servers
        except ValueError:
            return []

    # JSON
    def as_json(self):
        return json.dumps(
            self.__dict__,
            default=lambda o: o.__dict__,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    def load_json_from_file(self, filepath=SYSTEM_PREFS_PATH):
        # Read the profiles.json
        try:
            filestat = os.stat(filepath)
            owner_id = filestat.st_uid
            group_id = filestat.st_gid
            if owner_id != 0 or group_id != 0:
                print(
                    "system_preferences.json owner is not root, this is a security violation, please make sure it's owner is root"
                )
                return copy.deepcopy(_DEFAULT_PREFERENCES)

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
        except Exception as e:
            print("Exception on loading system_preferences.json:", e)
            return copy.deepcopy(_DEFAULT_PREFERENCES)

    def save(self, filepath=SYSTEM_PREFS_PATH, json_object=None):
        if json_object is None:
            json_object = self.__dict__

        # Create the profiles.json if not exists
        try:
            # First create the directories
            PreferencesManager.CONFIG_DIR.mkdir(mode=0o600, parents=True, exist_ok=True)

            # Then create the file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    json_object,
                    f,
                    default=lambda o: o.__dict__,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
        except PermissionError:
            print("Not enough permissions to create the file:", filepath)
            return


system_preferences_manager = None


def get_default() -> SystemPreferencesManager:
    global system_preferences_manager

    if system_preferences_manager is None:
        system_preferences_manager = SystemPreferencesManager()

    return system_preferences_manager
