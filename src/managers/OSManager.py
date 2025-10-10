def get_os_codename():
    with open("/etc/os-release", "rt") as f:
        for line in f.readlines():
            if "VERSION_CODENAME=" in line:
                return line.split("=")[1].strip()

    return ""
