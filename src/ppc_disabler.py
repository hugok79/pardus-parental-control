#!/usr/bin/python3

import sys

from PPCActivator import PPCActivator

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "--disable":
            activator = PPCActivator(sys.argv)
            activator.clear_application_filter()
            activator.clear_website_filter()
