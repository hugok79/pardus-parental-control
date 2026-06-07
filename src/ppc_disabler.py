#!/usr/bin/python3

import sys

import managers.FileRestrictionManager as FileRestrictionManager
import managers.FilterManager as FilterManager

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "--disable":
            # Privileged run check
            if not FileRestrictionManager.check_user_privileged():
                sys.stderr.write("You are not privileged to run this script.\n")
                sys.exit(1)

            FilterManager.clear_all_filters()
